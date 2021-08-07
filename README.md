# grocery_FM

### Scanning weekly promotion from Fred Meyer
_cmd:_ 
$>`python FredM-WeeklyAd.py [optional: items of interest (str), default = ['Zoi Greek Yogurt', 'Fred Meyer Milk', 'Avocado', 'berries']]`

output:
<img src='.\WeeklyAd-Output.png'>

### Processing grocery receipts from Fred Meyer
_cmd:_ 
$>`python FredM-EnterReceipt.py 'yyyy-mm-dd' [purchase date]`
Then wait for promt to enter SKU number and purchase quanity for each item on the receipt

output:
<img src='.\Receipt-Output.png'>
 
### Requirments
requests==2.25.1
pandas==1.2.3
selenium==3.141.0
beautifulsoup4==4.9.3
