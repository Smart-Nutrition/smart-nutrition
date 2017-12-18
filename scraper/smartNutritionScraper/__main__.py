import sys
import scrapy
import requests
import json
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def postItems(items, user):
    # Actually make the request.
    # First create a new trip
    # Then add items to the trip.
    payload = {'provider': 'Kroger', 'username': user}


    r = requests.post("http://localhost:8000/api/manual/trips", data=payload)
    if r.status_code != 200:
        print("Error sending data!")
        print(r.status_code)
        print(r.text)


    response = r.json()
    trip = response["id"]
    print(trip)

    payload = []
    payload.append(('username', user))

    for item in items:
        if len(item["weight"].split(" ", 1)) >= 2:
            weight = item["weight"].split(" ", 1)[0]
            unit = item["weight"].split(" ", 1)[1]
            qty =  float("".join(filter( lambda x: x in '0123456789.', item["qty"] )))
            foodstring = item["name"] + ":" + str(qty * float(weight)) + ":" + unit
            print(foodstring)
            payload.append(('food', foodstring))

    r = requests.post("http://localhost:8000/api/manual/trips/" + trip, data=tuple(payload))
    if r.status_code != 200:
        print("Error sending data!")
        print(r.status_code)
        print(r.text)

    print(r.text)

    return


def submitTrip(data, user):
    soup = BeautifulSoup(data)
    rows = soup.findAll("div", { "class" : "ReceiptDetail-itemContainer" })
    upcs = []
    names = []
    weights = []
    qtys = []
    for row in rows:
        description = row.findAll("div", { "class" : "ReceiptDetail-itemDescription" })[0]
        qty = row.findAll("div", { "class" : "ReceiptDetail-itemQuantity" })[0]
        if len(description.findAll("a", { "class" : "ReceiptDetail-itemName" })) > 0:
            name = description.findAll("a", { "class" : "ReceiptDetail-itemName" })[0]
            weight = description.findAll("div", { "class" : "ReceiptDetail-weight" })[0]
            upcs.append(name['href'].split("/")[-1])
            names.append(name.getText())
            weights.append(weight.getText())
            qtys.append(qty.getText().split("Amount: ", 1)[1])

    items = []

    if len(upcs) != 0:
        for i in range(len(upcs)):
            item = {}
            item['upc'] = upcs[i]
            item['name'] = names[i]
            item['weight'] = weights[i]
            item['qty'] = qtys[i]
            print(item)
            items.append(item)

        postItems(items, user)
        return True
    else:
        return False


def krogerScraper(smartusername, user, password):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    browser = webdriver.Firefox(firefox_options=opts)
    browser.get("https://www.kroger.com/signin")

    username = WebDriverWait(browser, 30).until(
        EC.visibility_of_element_located((By.ID, 'emailAddress'))
    )

    passwd = WebDriverWait(browser, 30).until(
        EC.visibility_of_element_located((By.ID, 'password'))
    )
    try:
        username.send_keys(user)
    except StaleElementReferenceException:
        print("Retry")
        username.send_keys(user)
    passwd.send_keys(password)
    browser.find_element_by_id("submit").click()
    homeHTML = browser.page_source

    browser.get("https://www.kroger.com/mypurchases")
    purchasesHTML = browser.page_source
    receipts = browser.find_elements_by_class_name("ReceiptList-receiptDateLink")
    tripLen = len(receipts)

    i = 0
    while i < tripLen:
	    receipts[i].click()
	    sent = submitTrip(browser.page_source, smartusername) # username should be passed in
	    if (not sent):
	        i -= 1 # Retry
	    browser.get("https://www.kroger.com/mypurchases")
	    receipts = browser.find_elements_by_class_name("ReceiptList-receiptDateLink")
	    i += 1


    browser.quit()


def main():
    """Start doing stuff"""

    if (len(sys.argv) != 4):
        print("Need <smartNutrition username> <username> <password> as arguments")
        return

    smartusername = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    krogerScraper(smartusername, username, password)

if __name__ == "__main__":
    main()
