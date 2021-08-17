import requests
from bs4 import BeautifulSoup
import pandas as pd

if __name__ == '__main__':

    url = "https://shop.worldofweed.com/tacoma/edible"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    items = soup.find_all('a',{'class': "product-card justify-between items-center ma2 relative"})
    data = []
    for item in items:
        sales = item.find('p', {"class": "strike red ma0"})
        if sales:
            d = {}
            d["page"] = item['href']
            d["regular"] = sales.text
            d["current"] = item.find('section',{'class':'flex items-center justify-around'}).text[len(sales.text):]
            d["discount"] = "{:.1f}%".format((1- float(d["current"][1:]) /float(d["regular"][1:]))*100)
            d["brand"] = item.find('p', {"class": "tc ma0 mt1 f7"}).text
            d["name"] = item.find('b', {"class": "tc mv2 f5"}).text
            d["details"] = item.find('section',{"class":"flex flex-column justify-around w-100 grow-1"}).text
            data.append(d)

    if len(data) == 0:
        print("No sales could be found currently on edibles. \nFor more details, please visit "+url)
    else:
        df = pd.DataFrame(data)
        print("{} items are found on sale: \n{} \nFor more details, please visit {}.".format(len(data), df[["discount","name","brand","current","regular"]],url))
