import os
import sys
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json
from selenium import webdriver
pd.options.mode.chained_assignment = None




if __name__ == '__main__':
    purchase_date = sys.argv[1]
    print(">>> Processing Receipt for {} <<<".format(purchase_date))

    receipt_file = 'receipt_{}.csv'.format(purchase_date)
    with open(receipt_file, mode='w') as f:
        f.write('sku,quantity')

    print("\nPlease enter sku number and purchase quantity for each item")
    f = os.system(receipt_file)

    # purchase_date = 'TEST'
    # receipt_file = 'receipt_TEST.csv'

    df = pd.read_csv(receipt_file, header='infer')
    skus = df['sku'].to_list()
    quantities = df['quantity'].to_list()
    data = []

    for i in range(len(skus)):
        d = {}
        d['quantity'] = quantities[i]
        d['sku'] = skus[i]
        sku = str(skus[i])
        link = 'https://www.fredmeyer.com/p/*/' + (13 - len(sku)) * '0' + sku + '?fulfillment=PICKUP'
        d['url'] = link

        driver = webdriver.Chrome()
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        scripts = soup.find_all('script', type="application/ld+json")

        jsonObj = json.loads(scripts[0].string)
        print(jsonObj["itemListElement"][-1]['name'])
        if jsonObj["itemListElement"][-1]['name'] == 'Product Unavailable':
            d['missing'] = 'webpage' # webpage no longer available
            driver.close()
            data.append(d)
            continue

        d['name'] = jsonObj["itemListElement"][-1]['name']
        d['catetory'] = jsonObj["itemListElement"][-2]['name']

        jsonObj = json.loads(scripts[1].string)
        d['display_name'] = jsonObj['name']
        d['description'] = jsonObj['description']
        # d['sku'] = str(jsonObj['sku'])
        # d['url'] = jsonObj['url']
        if 'brand' in jsonObj.keys():
            d['brand'] = jsonObj['brand']

        if jsonObj['offers'] != []:
            d['price'] = jsonObj['offers'][-1]['price']
        else:
            d['missing'] = 'price'

        elems = driver.find_elements_by_tag_name("data")
        if len(elems) > 0:
            d['current_price'] = elems[0].get_property('value')

        elems = driver.find_elements_by_tag_name("s") # < s class ="kds-Price-original" >
        if len(elems) > 0:
            d['original_price'] = elems[0].text[1:] #remove $ sign in front

        if soup.find('span', {'class': "kds-MicroTag-text"}):
            d['promotion'] = soup.find('span', {'class': "kds-MicroTag-text"}).text

        if soup.find('span', id="ProductDetails-sellBy-unit"):
            d['unit'] = soup.find('span', id="ProductDetails-sellBy-unit").text

        if soup.find('span', id="ProductDetails-sellBy-weight"):
            d['uni_price'] = soup.find('span', id="ProductDetails-sellBy-weight").text

        if soup.find('div',{"class": "NutritionLabel-ServingSize font-bold flex justify-between"}):
            d['serving_size'] = soup.find('div',{"class": "NutritionLabel-ServingSize font-bold flex justify-between"}).text[len('Serving size'):]

        if soup.find('div', {"class": "NutritionLabel-Calories font-bold flex justify-between"}):
            d['calories'] = soup.find('div', {"class": "NutritionLabel-Calories font-bold flex justify-between"}).text[len('Calories'):]

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

        if soup.find('p', {"class": "NutritionIngredients-Ingredients"}):
            d['ingredients'] = soup.find('p', {"class": "NutritionIngredients-Ingredients"}).text[len('Ingredients'):]

        if soup.find('p', {"class": "NutritionIngredients-Allergens"}):
            d['allergens'] = soup.find('p', {"class": "NutritionIngredients-Allergens"}).text[len('Allergen Info'):]
        driver.close()
        data.append(d)

    df = pd.DataFrame(data)

    columns = ['missing', 'price', 'current_price', 'original_price', 'promotion', 'quantity', 'name', 'catetory', 'display_name', 'description', 'sku','url','unit', 'serving_size', 'calories', 'Total Fat', 'Cholesterol', 'Sodium', 'Total Carbohydrate', 'Protein', 'Saturated Fat', 'Trans Fat', 'Polyunsaturated Fat', 'Monounsaturated Fat', 'Dietary Fiber', 'Sugar', 'Calcium', 'Iron', 'Vitamin A', 'Vitamin C', 'ingredients','allergens']
    for c in columns:
        if c not in df.columns:
            df[c] = np.nan

    print("\nI have now finished scanning the Fred Meyer's website for price information. I need your help with a few items.")

    # website no longer available
    missing_webpage_skus = df['sku'][df.missing == 'webpage']
    missing_idx = df[df.missing == 'webpage'].index.tolist()
    if len(missing_webpage_skus)>0:
        print("\nWebpages on the following SKUs are no longer available. Please enter manually.")
        for sku,ix in zip(missing_webpage_skus, missing_idx):
            print('SKU: {}'.format(sku))
            df.at[ix,'name'] = input(" > Item Name: ")
            df.at[ix,'price'] = input(" > Price per unit: $")
            df.at[ix,'original_price'] = input(" > Original Price before discount: $")

    # price info no longer available
    missing_price_names = df['name'][df.missing == 'price']
    missing_idx = df[df.missing == 'price'].index.tolist()
    if len(missing_price_names)>0:
        print("\nPrice information on the following items is no longer available. Please enter manually.")
        for name,ix in zip(missing_price_names, missing_idx):
            print('Item: {} '.format(name))
            df.at[ix,'price'] = input(" > Price per unit: $")
            df.at[ix,'original_price'] = input(" > Original Price before discount: $")

    # modify price based on quantity according to promotion rules
    if len(df.promotion[df.promotion.notnull()].to_list()) > 0:
        for ix in df.promotion[df.promotion.notnull()].index.to_list():
            text = df.at[ix, 'promotion']

            pattern_1 = r"\d+ For \$\d+.\d+"  # e.g. '2 For $5.00'; 'Buy 3 For $10.00'
            pattern_2 = r"\d+ or More, Save \$\d+.\d+ Each"  # 'Buy 5 or More, Save $1.00 Each'
            pattern_3 = r"Buy \d+, Get \d+ "  # 'Buy 1, Get 1 Free'

            if len(re.findall(pattern_1, text)) == 1:
                s = re.findall(pattern_1, text)[0]
                q = int(re.findall(pattern_1[:4], s)[0][:-1])
                p = float(re.findall(pattern_1[-9:], s)[0][1:])
                if int(df.at[ix, 'quantity']) >= q:
                    df.at[ix, 'price'] = str(p / q)  # keep as string

            elif len(re.findall(pattern_2, text)) == 1:
                s = re.findall(pattern_2, text)[0]
                q = int(re.findall(pattern_2[:4], s)[0][:-1])
                p = float(re.findall(pattern_2[-14:-5], s)[0][1:])
                if int(df.at[ix, 'quantity']) >= q:
                    df.at[ix, 'price'] = str(float(df.at[ix, 'price']) - p)  # keep as string

            elif len(re.findall(pattern_3, text)) == 1:
                f = input(
                    "It seems {} has a special promotion: {}. \nYou have bought {} units of SKU {} in total. Is the unit price ${} still correct? [y/n]".format(
                        df.at[ix, 'name'], df.at[ix, 'promotion'], df.at[ix, 'quantity'], df.at[ix, 'sku'],
                        df.at[ix, 'price']))
                if f == 'n':
                    df.at[ix, 'price'] = input("Please enter the effective unit price after discount: $")

    df['subtotal'] = df.price.astype(float) * df.quantity
    total = df['subtotal'].sum()

    df['original_price'][df['original_price'].isna()] = df['current_price'][df['original_price'].isna()]
    # df['saving'] = (df.original_price.str.replace('$','').astype(float) - df.price.astype(float))* df.quantity
    df['saving'] = (df.original_price.astype(float) - df.price.astype(float))* df.quantity
    saving = df['saving'].sum()

    data_file = 'data_{}.csv'.format(purchase_date)
    df.to_csv(data_file, header=True)

    print("\nYou spent ${:.2f} in total on {} and saved ${:.2f}!".format(total,purchase_date,saving))
    print("\nHere is a snapshot of your purchase:")
    print(df[['name','quantity','price','subtotal','saving','promotion']])
    print("\nFull set of data is saved in {}".format(data_file))
    print("\nHappy Grocery Shopping!")
