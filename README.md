# grocery_FM

### Scanning weekly promotion from Fred Meyer
cmd > python FredM-WeeklyAd.py [optional: items of interest (str), default = ['Zoi Greek Yogurt', 'Fred Meyer Milk', 'Avocado', 'berries']] 

Output


### Processing grocery receipts from Fred Meyer
cmd > python FredM-EnterReceipt.py 'yyyy-mm-dd' [purchase date] 

Wait for promt to enter SKU number and purchase quanity for each item on the receipt

Output

 

### Requirments

requests==2.25.1

pandas==1.2.3

selenium==3.141.0

beautifulsoup4==4.9.3

