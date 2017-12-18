from flask import request, jsonify, session
from pymongo import MongoClient
import smartNutrition
import requests
import time
import math
from http import HTTPStatus as STATUS
import hashlib
import os
import binascii
from operator import itemgetter
import json # Remove once we aren't using sample_data.json

LOGIN_TIMEOUT = 60*60*24*2 # logged out after 2 days of inactivity
db = MongoClient().SmartNutrition

# MongoDB object structure:
# { "username":<username>, "password":<password", ...
#   "providers":{"Kroger":{"username":<username>...}...],
#   "trips":[{"provider":"Kroger", "date":<date>, "foods":["name", ...]...}...],
#   "goals":{}}

# Food collection object structure in MongoDB
# {
#    "name":<food name>,
#    "calories":<T/F>,
#    "protein":<T/F>,
#    ...
#    "cholesterol":<T/F>
# }

def json_key(k):
    try: k = int(k)
    except: pass
    return k

def clean_mongodb_id(obj):
    return {k:v for k,v in obj.items() if k != '_id'}

# Removed fields that aren't shown on the website
#base_fields = frozenset(["calories", "protein", "fat", "trans_fat", "sat_fat", "carb", "starch", "sucrose", "glucose", "fructose", "lactose", "maltose", "alcohol", "water", "caffeine", "sugar", "fiber", "calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc", "copper", "flouride", "manganese", "selenium", "vit_a", "vit_b6", "vit_b12", "vit_c", "vit_d", "vit_d2", "vit_d3", "vit_e", "vit_k", "carotene_alpha", "carotene_beta", "thiamin", "riboflavin", "niacin", "cholesterol"])
base_fields = frozenset(["calories", "protein", "fat", "sat_fat", "sodium", "carb", "fiber", "calcium", "iron", "zinc", "copper", "manganese", "vit_a", "vit_b6", "vit_b12", "vit_c", "vit_d", "vit_e", "vit_k", "riboflavin", "niacin", "cholesterol"])

def NanIfZero(x):
    if x == 0: x = math.nan
    return x
computed_fields = {
    "fat_cs":      lambda x: x["fat"]     * 9.0,
    "protein_cs":  lambda x: x["protein"] * 4.0,
    "carb_cs":     lambda x: x["carb"]    * 4.0,
    "fat_p":       lambda x: x["fat"]     * 9.0 / NanIfZero(x["calories"]),
    "protein_p":   lambda x: x["protein"] * 4.0 / NanIfZero(x["calories"]),
    "carb_p":      lambda x: x["carb"]    * 4.0 / NanIfZero(x["calories"]),
    "grain_s":     lambda x: x["carb"] / 200,
    "protein_s":   lambda x: x["protein"] / 200,
    "dairy_s":     lambda x: x["calcium"] / 200,
    "fruit_s":     lambda x: x["vit_c"] / 200,
    "vegetable_s": lambda x: x["fiber"] / (x["fat"]+1) / 10,
}
field_names = base_fields | frozenset(computed_fields)
goal_field_names = (field_names | frozenset(['name'])) - frozenset(['calories'])

def token_hex(bytes): # a replacement for secrets.token_hex from python 3.6
    return binascii.hexlify(os.urandom(bytes)).decode('utf-8')

def password_hash(username, userid, salt, password):
    m = hashlib.sha512()
    m.update(username.encode('utf-8'))
    m.update(str(userid).encode('utf-8'))
    m.update(salt.encode('utf-8'))
    m.update(password.encode('utf-8'))
    return m.hexdigest()

def active_user():
    if "username" not in session:
        return None
    curtime = time.time()
    if curtime - session["last_active"] > LOGIN_TIMEOUT:
        del session["username"]
        del session["last_active"]
        return None
    else:
        session["last_active"] = curtime
        return session["username"]

def remove_nan(val):
    if type(val) == dict:
        return {k:remove_nan(v) for k,v in val.items()}
    elif type(val) == list:
        return [remove_nan(v) for v in val]
    elif type(val) == float and math.isnan(val):
        return None
    return val

def goalstring_convert(val):
    try:
        return {'type':'near','value':float(val)}
    except: pass
    t, value = val.split(':')
    if t not in ['above', 'below', 'near']:
        raise KeyError()
    return {'type':t,'value':float(value)}

def MakeResult(code = 200, **vals):
    return jsonify(remove_nan(vals)), code
def MakeEmtpyResult():
    return "", STATUS.NO_CONTENT
def MakeErrResult(code, *messages):
    return MakeResult(code, errors = messages)

def MissingKey(key):
    return MakeErrResult(STATUS.BAD_REQUEST, "Missing key '{}'".format(key))

def goal_to_user_goal(goal):
    goal = clean_mongodb_id(goal)
    for k, v in goal['goals'].items():
        goal[k] = v
    del goal['goals']
    return goal

def api_create_user():
    if "password" not in request.form:
        return MissingKey("password")
    if "username" not in request.form:
        return MissingKey("username")
    if len(list(db.users.find({"username":request.form["username"]}))) != 0:
        return MakeErrResult(STATUS.CONFLICT, "A user with that username already exists")

    salt = token_hex(32)
    pw_hash = password_hash(request.form["username"],
                            0,
                            salt,
                            request.form["password"])
    user = {
        "username":request.form["username"],
        "password_hash": pw_hash,
        "time_created": time.time(),
        "salt": salt,
        "providers":{},
        "trips":[],
        "goals":goal_to_user_goal(db.goals.find_one({}))
    }
    db.users.insert_one(user)
    return MakeResult(STATUS.CREATED, username = request.form["username"])

def api_get_user():
    username = active_user()
    if not username:
        return MakeErrResult(403, "No user is logged in")
    user = list(db.users.find({"username":username}))[0]
    return MakeResult(STATUS.OK, username=username, goals=user["goals"])

def api_delete_user():
    username = active_user()
    if not username:
        return MakeErrResult(403, "No user is logged in")
    db.users.delete_many({"username":username})
    return MakeResult(username=username)

def api_modify_user():
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "You are not logged in")
    user = list(db.users.find({"username":username}))[0]

    if 'password' not in request.form:
        return MissingKey('password')
    if 'old_password' not in request.form:
        return MissingKey('old_password')

    hashed_pw = password_hash(username, 0, user["salt"], request.form["old_password"])
    if hashed_pw != user["password_hash"]:
        return MakeErrResult(STATUS.UNAUTHORIZED, "Incorrect Password")

    changes = {}
    changes["salt"] = token_hex(32)
    changes["password_hash"] = password_hash(username, 0, changes["salt"], request.form["password"])

    db.users.update_one({"username":username},{"$set":{k:v for k,v in changes.items()}})
    return MakeResult(username = username, **visiblechanges)

@smartNutrition.app.route("/api/login", methods=['POST'])
def login_api_route():
    if active_user():
        return MakeErrResult(STATUS.UNAUTHORIZED, "The user {} is already logged in".format(session["username"]))
    if "username" not in request.form:
        return MissingKey("username")
    if "password" not in request.form:
        return MissingKey("password")
    username = request.form["username"]
    match_users = list(db.users.find({"username":username}))
    if len(match_users) == 0:
        return MakeErrResult(STATUS.BAD_REQUEST, "User does not exist")
    user = match_users[0]

    hashed_pw = password_hash(username, 0, user["salt"], request.form["password"])
    if hashed_pw != user["password_hash"]:
        return MakeErrResult(STATUS.UNAUTHORIZED, "Incorrect Password")
    session["username"] = username
    session["last_active"] = time.time()
    return MakeResult(username = username)

@smartNutrition.app.route("/api/logout", methods=['POST'])
def logout_api_route():
    if active_user():
        del session["username"]
        del session["last_active"]
        return MakeEmtpyResult()
    else:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")

@smartNutrition.app.route("/api/users", methods=['POST', 'DELETE', 'PATCH', 'GET'])
def users_api_route():
    return {
        "POST": api_create_user,
        "DELETE": api_delete_user,
        "PATCH": api_modify_user,
        "GET": api_get_user
    }[request.method]()

@smartNutrition.app.route("/api/users/goals", methods=['PATCH'])
def users_goals_api_route():
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "You are not logged in")
    user = list(db.users.find({"username":username}))[0]

    changes = {}
    for key, val in request.form.items():
        if key not in goal_field_names:
            return MakeErrResult(STATUS.BAD_REQUEST, "Invalid field name: " + key)
        if key in field_names:
            try:
                changes[key] = goalstring_convert(val)
            except:
                return MakeErrResult(STATUS.BAD_REQUEST, "Invalid goal value: " + str(val))
        elif key == 'name':
            changes['name'] = val

    for k, v in changes.items():
        user['goals'][k] = v
    db.users.update_one({"username":username},{"$set":{'goals':user['goals']}})
    return MakeResult(**changes)

def lookup_foods(ids):
    foods_map = DB_select("foods", lambda k,v: int(k) in ids)
    foods_list = [(i, foods_map[i]) for i in ids]
    return [{"id":foodid,"name":name}
            for foodid, name
            in foods_list]

def trip_field(trip, field):
    if field in base_fields:
        return trip[field]
    return computed_fields[field](trip)

def prepare_trip(trip, fields):
    return {
        "id": trip["trip_id"],
        "time":    trip["time"],
        "provider":trip["provider"],
        "totals": {f:trip_field(trip,f) for f in fields},
        "key_foods": trip["key_foods"]
    }

@smartNutrition.app.route("/api/trip", methods=['GET'])
def trip_api_route():
    if "id" not in request.args:
        return MakeErrResult(STATUS.BAD_REQUEST, "No trip ID was provided")
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    user = list(db.users.find({"username":username}))[0]
    matching_trips = [t for t in user["trips"] if t["trip_id"] == request.args["id"]]
    if len(matching_trips) == 0:
        return MakeErrResult(STATUS.UNAUTHORIZED, "The specified trip does not belong to this user")
    trip = matching_trips[0]
    return MakeResult(STATUS.OK, **prepare_trip(trip, field_names), food=trip["foods"])

def make_summary(start, end, username, fields):
    user = list(db.users.find({"username":username}))[0]
    trips= [t for t in user["trips"] if start < t["time"] < end]
    relevant_goals = {f:v for f, v in user["goals"].items() if f in fields or f == 'name'}
    totals = {field:sum(trip_field(t,field) for t in trips) for field in fields}
    return MakeResult(STATUS.OK, username=username,
                                 goals=relevant_goals,
                                 totals=totals,
                                 trips=[prepare_trip(t, fields) for t in trips])

def make_short_summary(start, end, username, fields):
    user = list(db.users.find({"username":username}))[0]
    trips= [t for t in user["trips"] if start < t["time"] < end]
    relevant_goals = {f:v for f, v in user["goals"].items() if f in fields}
    totals = {field:sum(trip_field(t,field) for t in trips) for field in fields}
    return MakeResult(STATUS.OK, goals=relevant_goals, totals=totals)

def get_time_range():
    start = 0
    if start in request.args:
        start = request.args["start"]
    end = time.time() * 1000 # JS uses ms instead of seconds.
    if end in request.args:
        end = request.args["end"]
    return start, end

@smartNutrition.app.route("/api/summary", methods=['GET'])
def summary_api_route():
    start, end = get_time_range()
    fields = frozenset(request.args.getlist("field"))
    if not fields:
        fields = field_names
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    return make_summary(start, end, username, fields)

@smartNutrition.app.route("/api/macronutrients", methods=['GET'])
def macronutrients_api_route():
    start, end = get_time_range()
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    return make_short_summary(start, end, username, {"fat_p","carb_p","protein_p"})

@smartNutrition.app.route("/api/foodgroups", methods=['GET'])
def foodgroups_api_route():
    start, end = get_time_range()
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    return make_short_summary(start, end, username, {"grain_s","protein_s","dairy_s","fruit_s","vegetable_s"})

@smartNutrition.app.route("/api/providers", methods=['GET'])
def providers_api_route():
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    user = list(db.users.find({"username":username}))[0]
    providers = user["providers"]
    return MakeResult(STATUS.OK, **{pt:{k:p[k] for k in ["date_added","username"]} for pt,p in providers.items()})

@smartNutrition.app.route("/api/providers/<provider_type>", methods=['POST','DELETE'])
def provider_api_route(provider_type):
    username = active_user()
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")
    if provider_type not in ["Kroger", "Manual"]:
        return MakeErrResult(STATUS.BAD_REQUEST, "The only supported provider types are Kroger or Manual")
    user = list(db.users.find({"username":username}))[0]
    if request.method == 'POST':
        if "username" not in request.form:
            return MissingKey("username")
        if "password" not in request.form:
            return MissingKey("password")
        user["providers"][provider_type] = {
            "username":request.form["username"],
            "password":request.form["password"],
            "date_added":time.time()}
        db.users.update_one({"username":username}, {"$set":{"providers":user["providers"]}})

        if provider_type == "Kroger":
            # Trigger kroger scraper
            pid = os.fork()
            if pid == 0:
                os.system("smartNutritionScraper " + username + " " + request.form["username"] + " " + request.form["password"])

        return MakeEmtpyResult()
    elif request.method == 'DELETE':
        providers = user["providers"]
        if provider_type not in providers:
            return MakeErrResult(STATUS.BAD_REQUEST, "Provider does not exist")
        del providers[provider_type]
        db.users.update_one({"username":username}, {"$set":{"providers":providers}})
        return MakeEmtpyResult()

@smartNutrition.app.route("/api/manual/trips", methods=['POST'])
def manual_trips_api_route():
    username = active_user()
    if not username and 'username' in request.form:
        username = request.form['username']
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")

    if "provider" not in request.form:
        return MissingKey("provider")
    provider_type = request.form["provider"]
    if provider_type not in ["Kroger", "Manual"]:
        return MakeErrResult(STATUS.BAD_REQUEST, "The only supported provider types are Kroger or Manual")

    trip_time = time.time()
    if "time" in request.form:
        try: trip_time = float(request.form["time"])
        except: return MakeErrResult(STATUS.BAD_REQUEST, "'time' must be a number.")
    user = list(db.users.find({"username":username}))[0]
    trip = {
        "trip_id":token_hex(16),
        "time":trip_time,
        "provider":provider_type,
        "foods":[],
        "key_foods":{},
        **{k:0 for k in base_fields}}
    user["trips"].append(trip)
    db.users.update_one({"username":username}, {"$set":{"trips":user["trips"]}})
    return MakeResult(STATUS.OK, **prepare_trip(trip, field_names), food=[])

@smartNutrition.app.route("/api/manual/trips/<trip_id>", methods=['POST','DELETE'])
def manual_trip_api_route(trip_id):
    username = active_user()
    if not username and 'username' in request.form:
        username = request.form['username']
    if not username:
        return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")

    user = list(db.users.find({"username":username}))[0]
    trip = None
    for i in range(len(user["trips"])):
        if user["trips"][i]["trip_id"] == trip_id:
            trip = user["trips"][i]
            if request.method == 'POST':
                foods = request.form.getlist("food")
                user["trips"][i]["foods"] = foods
                smartNutrition.api.compute_trip_nutrition(user["trips"][i])
            else:
                del user["trips"][i]
    if not trip:
        return MakeErrResult(STATUS.BAD_REQUEST, "Trip does not exist.")

    db.users.update_one({"username":username}, {"$set":{"trips":user["trips"]}})

    return MakeResult(STATUS.OK, **prepare_trip(trip, field_names), food=trip["foods"])

@smartNutrition.app.route("/api/goals", methods=['GET', 'POST'])
def goals_api_route():
    if request.method == 'GET':
        search = {}
        limit = 10
        if 'name' in request.args:
            search['name'] = request.args['name']
            limit = 1
        foundgoals = db.goals.find(search).limit(limit)
        return MakeResult(STATUS.OK, goals=[clean_mongodb_id(g) for g in foundgoals])
    if request.method == 'POST':
        if 'name' not in request.form:
            return MakeErrResult(STATUS.BAD_REQUEST, "No name provided")
        if 'description' not in request.form:
            return MakeErrResult(STATUS.BAD_REQUEST, "No description provided")
        if db.goals.count({"name":request.form['name']}) != 0:
            return MakeErrResult(STATUS.CONFLICT, 'Name is already in use')
        goal = {}
        for field in goal_field_names:
            if field in request.form:
                if field == 'name': continue
                if field == 'description': continue
                try:
                    goal[field] = goalstring_convert(request.form[field])
                except:
                    return MakeErrResult(STATUS.BAD_REQUEST, "Invalid goal value: " + request.form[field])
            else:
                goal[field] = None
        db.goals.insert_one({"name":request.form['name'], "description":request.form['description'], "goals":goal})
        return MakeResult(STATUS.OK, name=request.form['name'])


@smartNutrition.app.route("/api/recommend", methods=['GET'])
def recommend_api_route():

    def score_for_ratio(r, type):
        if type == "above":
            if r < 1: # Below goal, lower score
                return r ** 2
            else:
                return 1.0
        elif type == "below":
            if r > 1: # Above goal, lower score
                return (r - 2) ** 2
            else:
                return 1.0
        else: # Penelize score unless exact
            if r < 1:
                return r ** 2
            else:
                return (r - 2) ** 2

    id_map = {
    203:"protein",
    204:"fat",
    605:"trans_fat",
    606:"sat_fat",
    205:"carb",
    209:"starch",
    210:"sucrose",
    211:"glucose",
    212:"fructose",
    213:"lactose",
    214:"maltose",
    221:"alcohol",
    255:"water",
    262:"caffeine",
    269:"sugar",
    291:"fiber",
    301:"calcium",
    303:"iron",
    304:"magnesium",
    305:"phosphorus",
    306:"potassium",
    307:"sodium",
    309:"zinc",
    312:"copper",
    313:"flouride",
    315:"manganese",
    317:"selenium",
    318:"vit_a",
    415:"vit_b6",
    418:"vit_b12",
    401:"vit_c",
    324:"vit_d",
    325:"vit_d2",
    326:"vit_d3",
    323:"vit_e",
    430:"vit_k",
    322:"carotene_alpha",
    321:"carotene_beta",
    404:"thiamin",
    405:"riboflavin",
    406:"niacin",
    601:"cholesterol"}

    headers = {"x-app-id":"2b34e2d7","x-app-key":"790d666a02c713823502567cc364dc04"}

    defaultGoals = db.goals.find_one({"name":"RDI"})

    # Default nutrients
    # calcium cholesterol vitamin-d
    nutrients = ["calcium", "cholesterol", "vit_d"]

    if "nutrient" in request.args:
        if len(request.args["nutrient"]) != 0:
            n = request.args["nutrient"]
            nutrients = n.split(" ")
    """else:
        # Need to get the nutrients that the user needs
        username = active_user()
        if not username and 'username' in request.form:
            username = request.form['username']
        if not username:
            return MakeErrResult(STATUS.UNAUTHORIZED, "No user is logged in.")

        user = db.users.find_one({"username":username})

        start, end = get_time_range()

        trips = [t for t in user["trips"] if start < t["time"] < end]
        totals = {field:sum(t[field] for t in trips) for field in base_fields}
        totalsPerCal = {field:value/totals["calories"] for field, value in totals if field != "calories"}
        user_goals = user["goals"]
        nutrientScores = {}
        for n, value in totalsPerCal.items():
            defaultCalories = float(defaultGoals["goals"]["calories"])
            if n in relevant_goals:
                goalPerCal = user_goals[n]["value"] / ("calories" in user_goals ? float(user_goals["calories"]) : defaultCalories)
                nutrientScores[n] = score_for_ratio(value / goalPerCal, user_goals[n]["type"])
            else:
                goalPerCal = defaultGoals[n]["value"] / defaultCalories
                nutrientScores[n] = score_for_ratio(value / goalPerCal, defaultGoals[n]["type"])

        sortedNutrientScores = [{"nutrient":n, "score":s for (n, s) in nutrientScores.items()}]
        sortedNutrientScores = sorted(sortedNutrientScores, key=itemgetter("score"))

        numNutrients = 5

        if len(sortedNutrientScores) < 5:
            numNutrients = len(sortedNutrientScores)

        nutrients = [v["nutrient"] for v in list(sortedNutrientScores[:numNutrients])]
        """


    # Use the needed nutrients to query the food database

    allFoods = {}
    for n in nutrients:
        for f in db.all_foods.find({}):
            allFoods[f["name"]] = f



    foodScore = {} # Using a dict here to avoid repeats

    for name, info in allFoods.items():
        score = 0
        for n in nutrients:
            if n in info:
                goal = defaultGoals["goals"][n]
                if goal != None:
                    goalPerCal = float(goal["value"]) / float(defaultGoals["goals"]["calories"])
                    realPerCal = float(info[n]) / float(info["calories"])
                    ratioOfGoal = realPerCal / goalPerCal
                    score += score_for_ratio(ratioOfGoal, goal["type"])
        foodScore[name] = score

    # Sort the foods by their scores
    sortedFoodScore = [{"name":n, "score":s} for (n, s) in foodScore.items()]
    sortedFoodScore = sorted(sortedFoodScore, key=itemgetter("score"), reverse=True)

    numRecommendations = 5

    if len(sortedFoodScore) < numRecommendations:
        numRecommendations = len(sortedFoodScore)

    # Show the best ~5 foods
    recommendedFoods = list(v["name"] for v in list(sortedFoodScore[:numRecommendations]))

    # Query the nutritionix API to get the rest of the information that is sent with each food
    foodInfo = []
    for food in recommendedFoods:
        nutrientInfo = db.all_foods.find_one({"name":food})
        outputInfo = {"name":food, "calories":nutrientInfo["calories"]}
        bestNutrients = []
        bestNutrientScore = -float('inf')
        for n, v in nutrientInfo.items():
            if n in id_map.values():
                outputInfo[n] = v # Add nutrition info to output
                if n in nutrients:
                    goalForNutrient = defaultGoals["goals"][n]
                    if goalForNutrient != None:
                        goalPerCal = float(goalForNutrient["value"]) / float(defaultGoals["goals"]["calories"])
                        realPerCal = v / nutrientInfo["calories"]
                        score = score_for_ratio(realPerCal / goalPerCal, goalForNutrient["type"])
                        if score > bestNutrientScore:
                            bestNutrients = [n]
                            bestNutrientScore = score


        outputInfo["recommended_for"] = bestNutrients

        foodInfo.append(outputInfo)

    return MakeResult(STATUS.OK, food=foodInfo)
