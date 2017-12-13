import json
from pymongo import MongoClient

db = MongoClient().SmartNutrition

with open("smartNutrition/api/reset_db/sample_data.json") as f:
    db.users.drop()
    for user in json.load(f):
        db.users.insert_one(user)
with open('smartNutrition/api/reset_db/sample_goals.json') as f:
    db.goals.drop()
    for goal in json.load(f):
        db.goals.insert_one(goal)
with open('smartNutrition/api/reset_db/sample_foods.json') as f:
	db.all_foods.drop()
	for food in json.load(f):
		db.all_foods.insert_one(food)
