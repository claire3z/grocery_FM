import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

def fredmeyer_weakly(items_of_interest):
    r = requests.get("https://wklyads.fredmeyer.com/flyers/fredmeyer-weekly/grid_view/724005?postal_code=98466&store_code=00111&type=2")
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script', type='text/javascript')
    your_script = [script for script in scripts if "window['flyerData']" in str(script)][0]
    begin =len("  window['flyerData'] = {")
    end = your_script.string.find(";\n  window['flyerData']['location_options']")
    jsonObj = json.loads(your_script.string[begin:end])

    columns = ['display_name','current_price','discount_percent','valid_from','valid_to','disclaimer_text','category_names','brand','description','x_large_image_url','dist_coupon_image_url']
    df = pd.DataFrame(jsonObj['items'])

    from_date = df['valid_from'][0]
    until_date = df['valid_to'][0]
    file_output = 'weeklyAd_'+until_date+'.csv'
    df[columns].to_csv(file_output)
    print(">>> {} to {} <<<".format(from_date,until_date))
    print("Data saved at "+file_output)

    alerts = items_of_interest
    for i in alerts:
        item = df[df.display_name.str.contains(i,case=False)]
        # print('\n  -> Alert! {} is on sale at {}. Discount: {}. Details: {}.'.format(item['display_name'].values[0],item['current_price'].values[0],item['discount_percent'].values[0], item['disclaimer_text'].values[0]))
        for j in range(len(item['display_name'].values[:])):
            print('\n  -> Alert! {} is on sale at {}. Discount: {}. Details: {}.'.format(item['display_name'].values[j],item['current_price'].values[j],item['discount_percent'].values[j], item['disclaimer_text'].values[j]))


if __name__ == '__main__':
    print("Scanning Fred Meyer's Weekly Promotion for " )
    if len(sys.argv) == 1:
        item_of_interest = ['Zoi Greek Yogurt', 'Fred Meyer Milk', 'Avocado', 'berries']
    else:
        item_of_interest = sys.argv[1:]
    fredmeyer_weakly(item_of_interest)
    print("\nHappy Grocery Shopping!")
