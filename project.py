from getkey import Updateroute
import json
import pandas as pd

scenic = pd.read_json('scenic.json')

for i in scenic:
    print(i)