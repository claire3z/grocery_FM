import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time




if __name__ == '__main__':
    purchase_date = sys.argv[1]
    print(">>> Processing Receipt for {} <<<".format(purchase_date))

    receipt_file = 'receipt_{}.csv'.format(purchase_date)
    with open(receipt_file, mode='w') as f:
        f.write('sku,quantity')

    print("\nPlease enter sku number and purchase quantity for each item")
    f = os.system(receipt_file)

    df = pd.read_csv(receipt_file, header='infer')
    skus = df['sku'].to_list()
    quantities = df['quantity'].to_list()

    data = []
    for i in range(len(skus)):
        d = {}
        d['quantity'] = quantities[i]

        sku = str(skus[i])
        link = 'https://www.fredmeyer.com/p/*/' + (13 - len(sku)) * '0' + sku + '?fulfillment=PICKUP'
        driver = webdriver.Chrome()
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts = soup.find_all('script', type="application/ld+json")

        jsonObj = json.loads(scripts[0].string)
        d['name'] = jsonObj["itemListElement"][-1]['name']
        d['catetory'] = jsonObj["itemListElement"][-2]['name']

        jsonObj = json.loads(scripts[1].string)
        d['display_name'] = jsonObj['name']
        d['description'] = jsonObj['description']
        # d['brand'] = jsonObj['brand']
        d['sku'] = str(jsonObj['sku'])
        d['url'] = jsonObj['url']

        if jsonObj['offers'] != []:
            d['price'] = jsonObj['offers'][-1]['price']

        elems = driver.find_elements_by_tag_name("data")
        if len(elems) > 0:
            d['current_price'] = elems[0].get_property('value')

        elems = driver.find_elements_by_tag_name("s")
        if len(elems) > 0:
            d['original_price'] = elems[0].text

        if soup.find('span', id="ProductDetails-sellBy-unit"):
            d['unit'] = soup.find('span', id="ProductDetails-sellBy-unit").text

        if soup.find('span', id="ProductDetails-sellBy-weight"):
            d['uni_price'] = soup.find('span', id="ProductDetails-sellBy-weight").text

        d['serving_size'] = soup.find('div',
                                      {"class": "NutritionLabel-ServingSize font-bold flex justify-between"}).text[
                            len('Serving size'):]
        d['calories'] = soup.find('div', {"class": "NutritionLabel-Calories font-bold flex justify-between"}).text[
                        len('Calories'):]

        macro_nutrients = soup.find_all('span', {"class": "NutrientDetail-Title pr-4 is-macronutrient"})
        for n in macro_nutrients:
            nutrient = n.text
            amount = n.parent.text[len(nutrient):]
            d[nutrient] = amount

        sub_nutrients = soup.find_all('span', {"class": "NutrientDetail-Title pr-4 is-macronutrient is-subnutrient"})
        for n in sub_nutrients:
            nutrient = n.text
            amount = n.parent.text[len(nutrient):]
            d[nutrient] = amount

        micro_nutrients = soup.find_all('span', {"class": "NutrientDetail-Title pr-4 is-micronutrient"})
        for n in micro_nutrients:
            nutrient = n.text
            amount = n.parent.text[len(nutrient):]
            d[nutrient] = amount

        d['ingredients'] = soup.find('p', {"class": "NutritionIngredients-Ingredients"}).text[len('Ingredients'):]
        d['allergens'] = soup.find('p', {"class": "NutritionIngredients-Allergens"}).text[len('Allergen Info'):]
        driver.close()
        data.append(d)

    df = pd.DataFrame(data)
    # df = df.append(df,ignore_index=True)
    missing_items = df[df.price.isna()]['name'].tolist()
    missing_idx = df[df.price.isna()]['price'].index.tolist()

    if len(missing_items)>0:
        for i in range(len(missing_items)):
            item_name = missing_items[i]
            ix = missing_idx[i]
            # item_name = df[df.price.isna()]['name'].values[0]
            # ix = df[df.price.isna()]['price'].index.tolist()[0]
            df.at[ix,'price'] = input("Please enter unit price for {}: $".format(item_name))

    df['subtotal'] = df.price.astype(float) * df.quantity
    total = df['subtotal'].sum()

    df['saving'] = (df.original_price.str.replace('$','').astype(float) - df.price.astype(float))* df.quantity
    saving = df['saving'].sum()

    data_file = 'data_{}.csv'.format(purchase_date)
    df.to_csv(data_file, header=True)

    print("\nYou spent ${} in total and saved ${}!".format(total,saving))
    print("\nData saved at "+data_file)
    print("\nHappy Grocery Shopping!")
