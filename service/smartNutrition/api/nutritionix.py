import requests
import pint
import string
from pymongo import MongoClient
ureg = pint.UnitRegistry()

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

def clean_unit_name(name):
    return "".join(name.split()).lower()

def addToAllFoodDatabase(info):
    db = MongoClient().SmartNutrition

    defaultGoals = db.goals.find_one({"name":"RDI"})

    name = info["food_name"]
    if len(list(db.all_foods.find({"name":name}))) == 0:
        newEntry = {"name":name}
        for n in info['full_nutrients']:
            if n["attr_id"] in id_map:
                nutrient = id_map[n["attr_id"]]
                goalForNutrient = defaultGoals["goals"][nutrient]
                if goalForNutrient != null:
                    goalForNutrient /= defaultGoals["goals"]["calories"] # <nutrient>/calorie
                    goalForNutrient *= 0.8 # Threshold for if a food is high in this nutrient

                    newEntry[nutrient] = ((n["value"]/info['nf_calories']) > goalForNutrient)
        db.all_foods.insert_one(newEntry)



def compute_trip_nutrition(trip):
    foods = trip['foods']
    trip["calories"] = 0
    highest = {v:(0,None) for v in id_map.values()}
    for k,v in id_map.items():
        trip[v] = 0
    for food in foods:
        name, amt, unit_name = food.split(':')
        try:
            qty = float(amt) * ureg(clean_unit_name(unit_name))
        except pint.errors.UndefinedUnitError:
            continue
        r = requests.get('https://trackapi.nutritionix.com/v2/search/instant', params={'query':name}, headers=headers).json()
        if "branded" not in r or len(r["branded"]) == 0:
            continue
        matches = []
        for item in r['branded']:
            try:
                num_servings = qty.to(ureg(clean_unit_name(item['serving_unit']))).magnitude / item['serving_qty']
            except ValueError:
                continue
            except pint.errors.UndefinedUnitError:
                continue
            lookup = {'nix_item_id':item["nix_item_id"]}
            r2 = requests.get('https://trackapi.nutritionix.com/v2/search/item', params=lookup, headers=headers).json()
            if "foods" not in r2 or len(r2["foods"]) != 1:
                continue
            matches.append(r2['foods'][0])
            break

        if len(matches) == 0:
            continue

        info = matches[0]
        #addToAllFoodDatabase(info)
        trip['calories'] += info['nf_calories'] * num_servings

        for d in info['full_nutrients']:
            if d["attr_id"] in id_map:
                nutrient = id_map[d["attr_id"]]
                trip[nutrient] += d["value"] * num_servings
                if highest[nutrient][0] < d["value"] * num_servings:
                    highest[nutrient] = (d["value"] * num_servings, food)
    trip["key_foods"] = {k:v[1] for k,v in highest.items() if v[1] != None}
