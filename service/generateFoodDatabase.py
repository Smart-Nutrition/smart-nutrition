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


"""
"Hamburger:16:oz",
"Chicken Breast:32:oz",
"Italian Sausage:19:oz",
"Hotdogs:30:oz",
"Ground Turkey:16:oz",
"Pork Chops:24:oz",
"Meatballs:16:oz",
"Salmon:24:oz",
"Tilapia:24:oz",
"Shrimp:16:oz",
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
"Grapefruit:16:oz",
"""
foods = [
#"Carrots:15:oz",
"Broccoli:15:oz",
"Lettuce:15:oz",
#"Green Pepper:12:oz",
"Green Beans:15:oz",
#"Corn:15:oz",
"Mushrooms:15:oz",
#"Peas:15:oz",
"Spinach:15:oz",
"Onions:15:oz",
"Potatoes:15:oz",
#"Potato Chips:16:oz",
#"Tortilla Chips:18:oz",
"Crackers:16:oz",
#"Triscuits:16:oz",
#"Cheez-its:16:oz",
"Beef Jerky:16:oz",
#"Bagels:20:oz",
#"Croissants:18:oz",
#"Chocolate Chip Cookies:16:oz",
#"Brownies:16:oz",
"Coca Cola:144:fl oz",
#"Apple Juice:64:fl oz",
"Orange Juice:64:fl oz",
"Grapefruit Juice:64:fl oz",
"Vegetable Juice:64:fl oz"]
#"Grape Juice:64:fl oz",
#"Cranberry Juice:64:fl oz"]

def clean_unit_name(name):
	return "".join(name.split()).lower()

def main():
	headers = {"x-app-id":"2b34e2d7","x-app-key":"790d666a02c713823502567cc364dc04"}

	output = []
	
	for food in foods:
		name, amt, unit_name = food.split(':')
		qty = float(amt) * ureg(clean_unit_name(unit_name))
		r = requests.get('https://trackapi.nutritionix.com/v2/search/instant', params={'query':name}, headers=headers).json()
		if "branded" not in r or len(r["branded"]) == 0:
			continue
		matches = []
		for item in r['branded']:
			"making limited request"
			lookup = {'nix_item_id':item["nix_item_id"]}
			r2 = requests.get('https://trackapi.nutritionix.com/v2/search/item', params=lookup, headers=headers).json()
			if "foods" not in r2 or len(r2["foods"]) != 1:
				continue
			try:
				num_servings = qty.to(ureg(clean_unit_name(r2['foods'][0]['serving_unit']))).magnitude / r2['foods'][0]['serving_qty']
			except:
				continue
			matches.append(r2['foods'][0])
			break

		if len(matches) > 0:
			info = matches[0]
			#addToAllFoodDatabase(info)
			entry = {}
			num_servings = qty.to(ureg(clean_unit_name(info['serving_unit']))).magnitude / info['serving_qty']
			entry['name'] = info["food_name"]
			entry['calories'] = info['nf_calories'] * num_servings

			for d in info['full_nutrients']:
				if d["attr_id"] in id_map:
					nutrient = id_map[d["attr_id"]]
					entry[nutrient] = d["value"] * num_servings

			output.append(entry)
		else:
			print(food)

	open("sample_foods.txt", "w").close() # Delete contents
	file = open("sample_foods.txt", "w")
	file.write(json.dumps(output, indent=4, sort_keys=False))
	file.close()

	print(json.dumps(output, indent=4, sort_keys=False))





if __name__ == "__main__":
	main()