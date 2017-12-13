import requests, json, pint, string, random
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

def generateTripFoods(num_weeks, num_protiens, num_fruits, num_vegtables, num_snacks, num_drinks):

	# These are the foods that are randomly sampled to fill the trip history
	# We can add more at any time
	proteins = [
	"Hamburger:16:oz",
	"Chicken Breast:32:oz",
	"Italian Sausage:19:oz",
	"Hotdogs:30:oz",
	"Ground Turkey:16:oz",
	"Pork Chops:24:oz",
	"Meatballs:16:oz",
	"Salmon:24:oz",
	"Tilapia:24:oz",
	"Shrimp:16:oz"]

	fruits = [
	"Apples:16:oz",
	"Bananas:16:oz",
	"Oranges:16:oz",
	"Cherries:16:oz",
	"Blueberries:16:oz",
	"Raspberries:16:oz",
	"Blackberries:16:oz",
	"Peaches:16:oz",
	"Pears:16:oz",
	"Grapes:16:oz",
	"Grapefruit:16:oz"]

	vegetables = [
	"Carrots:15:oz",
	"Broccoli:15:oz",
	"Lettuce:15:oz",
	"Green Pepper:12:oz",
	"Green Beans:15:oz",
	"Corn:15:oz",
	"Mushrooms:15:oz",
	"Peas:15:oz",
	"Spinach:15:oz",
	"Onions:15:oz",
	"Potatoes:15:oz"]

	snacks = [
	"Potato Chips:16:oz",
	"Tortilla Chips:18:oz",
	"Crackers:16:oz",
	"Triscuits:16:oz",
	"Cheez-its:16:oz",
	"Beef Jerky:16:oz",
	"Bagels:20:oz",
	"Croissants:18:oz",
	"Chocolate Chip Cookies:16:oz",
	"Brownies:16:oz"]

	drinks = [
	"Coca Cola:144:fl oz",
	"Apple Juice:64:fl oz",
	"Orange Juice:64:fl oz",
	"Grapefruit Juice:64:fl oz",
	"Vegetable Juice:64:fl oz",
	"Grape Juice:64:fl oz",
	"Cranberry Juice:64:fl oz",
	"Beer:72:fl oz"]

	trip_foods = []

	for _ in range(num_weeks):
		trip = []

		# Add proteins

		n_p = random.choice(num_protiens)
		trip += list(proteins[i] for i in random.choices(range(len(proteins)), k=n_p))

		# Add fruits

		n_f = random.choice(num_fruits)
		trip += list(fruits[i] for i in random.choices(range(len(fruits)), k=n_f))

		# Add vegetables

		n_v = random.choice(num_vegtables)
		trip += list(vegetables[i] for i in random.choices(range(len(vegetables)), k=n_v))

		# Add snacks

		n_s = random.choice(num_snacks)
		trip += list(snacks[i] for i in random.choices(range(len(snacks)), k=n_s))

		# Add drinks

		trip.append("Water:480:fl oz") # Get water every trip
		n_d = random.choice(num_drinks)
		trip += list(snacks[i] for i in random.choices(range(len(snacks)), k=n_d))

		trip_foods.append(trip)

	return(trip_foods)

def clean_unit_name(name):
	return "".join(name.split()).lower()

"""
headers_old = {"x-app-id":"7ed6d61b","x-app-key":"8d2a6a2462376ce31105b039ce6cca69"}
headers_old1 = {"x-app-id":"2b34e2d7","x-app-key":"790d666a02c713823502567cc364dc04"}
headers_old2 = {"x-app-id":"02010594", "x-app-key":"eece65e16fa5ebfef1dde3715d13bffe"}
headers = {"x-app-id":"52536da3", "x-app-key":"b44d5217eb3f652268f1f47bcda35f5a"}
"""

def compute_trip_nutrition(trip):
	headers = {"x-app-id":"52536da3", "x-app-key":"b44d5217eb3f652268f1f47bcda35f5a"}
	foods = trip['foods']
	trip["calories"] = 0
	highest = {v:(0,None) for v in id_map.values()}
	for k,v in id_map.items():
		trip[v] = 0
	for food in foods:
		name, amt, unit_name = food.split(':')
		qty = float(amt) * ureg(clean_unit_name(unit_name))
		r = requests.get('https://trackapi.nutritionix.com/v2/search/instant', params={'query':name}, headers=headers).json()
		if "branded" not in r or len(r["branded"]) == 0:
			continue
		matches = []
		for item in r['branded']:
			lookup = {'nix_item_id':item["nix_item_id"]}
			r2 = requests.get('https://trackapi.nutritionix.com/v2/search/item', params=lookup, headers=headers).json()
			if "foods" not in r2 or len(r2["foods"]) != 1:
				continue
			try:
				num_servings = qty.to(ureg(clean_unit_name(r2['foods'][0]['serving_unit']))).magnitude / r2['foods'][0]['serving_qty']
			except ValueError:
				continue
			matches.append(r2['foods'][0])
			break
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



def main():


	trip_foods = generateTripFoods(
		num_weeks = 52,
		num_protiens = range(2, 3),
		num_fruits = range(3, 5),
		num_vegtables = range(3, 5),
		num_snacks = range(3, 4),
		num_drinks = range(2, 3))

	time = 1208794522.5174572
	time_delta = 700000000

	trip_id = 0

	trips = {"trips":[]}

	for foods in trip_foods:
		trip = {"trip_id":"{}".format(trip_id), "provider":"Kroger", "time":time, "foods":foods, "key_foods":{}}
		trips["trips"].append(compute_trip_nutrition(trip))

		time += time_delta
		trip_id += 1

	open("sample_trips.txt", "w").close() # Delete contents
	file = open("sample_trips.txt", "w")
	file.write(json.dumps(trips, indent=4, sort_keys=False))
	file.close()

	print(json.dumps(trips, indent=4, sort_keys=False))


if __name__ == "__main__":
	main()
