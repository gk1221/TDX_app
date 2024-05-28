from flask import Flask, jsonify
from flask_cors import CORS
import requests
from geopy.distance import geodesic
import getkey
import json
import pandas as pd

app = Flask(__name__)
CORS(app)  # 這行代碼添加了 CORS 支持

@app.route('/busdata')
def get_data():
    
    
    city = "Taipei"
    api_url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/RealTimeByFrequency/City/{city}?%24format=JSON"

    getkey.getjson(api_url, 'test-freq')
    
    bus_data = ""
    with open('data/test-freq.json', 'r', encoding='utf-8') as f:
        bus_data = json.load(f)
    
   
    
    target_location = (25.033964, 121.564472)  # 台北101的經緯度
    radius = 3.0  # 公里

    filtered_data = []
    
    for item in bus_data:
        bus_location = (item['BusPosition']['PositionLat'], item['BusPosition']['PositionLon'])
        if geodesic(target_location, bus_location).km <= radius:
            filtered_data.append((bus_location[0], bus_location[1]))
    response = jsonify(filtered_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/CCTV')
def get_CCTV():
    column = ['CCTVID', 'LinkID', 'VideoStreamURL', 'PositionLon', 'PositionLat' ,'RoadName', 'SurveillanceDescription']
    citylist = ['YilanCounty', 'HsinchuCounty', 'ChanghuaCounty', 'NantouCounty', 'YunlinCounty', 'PingtungCounty', 'TaitungCounty', 'Keelung', 'Hsinchu', 'Chiayi', 'Taipei', 'Kaohsiung', 'NewTaipei', 'Taichung', 'Tainan', 'Taoyuan']
    df = pd.DataFrame(columns=column)
    for city in citylist:        
        with open(f'data/test-{city}.json', 'r', encoding='utf-8') as f:
            testTV = json.load(f)['CCTVs']

        city_data = {}
        for TV in testTV:

            for col in column:
                if col in TV:
                    
                    city_data[col] = TV[col]
                else:
                    pass
                    #print(city, col)

            df = pd.concat([df, pd.DataFrame([city_data])], ignore_index=True)
    df.fillna('', inplace=True)
    return jsonify(df.to_dict(orient='records'))

@app.route('/highwayCCTV')
def get_highwayCCTV():
    df = pd.DataFrame()
    with open(f'data/test-highway.json', 'r', encoding='utf-8') as f:
        highTV = json.load(f)['CCTVs']
    df.fillna('', inplace=True)
    df = pd.DataFrame(highTV)
    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
