from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from geopy.distance import geodesic, distance
import json
import pandas as pd
import time
from datetime import datetime, timezone

import getkey
import func

app = Flask(__name__)
CORS(app)  # 這行代碼添加了 CORS 支持

#共用函數
citylist = ['YilanCounty', 'HsinchuCounty', 'ChanghuaCounty', 'NantouCounty', 'YunlinCounty', 'PingtungCounty', 'TaitungCounty', 'Keelung', 'Hsinchu', 'Chiayi', 'Taipei', 'Kaohsiung', 'NewTaipei', 'Taichung', 'Tainan', 'Taoyuan']
CCTV_column = ['CCTVID', 'LinkID', 'VideoStreamURL', 'PositionLon', 'PositionLat' ,'RoadName', 'SurveillanceDescription']


    
global lat,lng
    
def calculate_distance(row,lat, lng):
        camera_location = (row['PositionLat'], row['PositionLon'])
        input_location = (lat, lng)
        return distance(camera_location, input_location).kilometers


@app.route('/update')
def get_update():
    get_url = [
          ('https://tdx.transportdata.tw/api/basic/v2/Tourism/Activity?%24orderby=starttime%20desc&%24top=80&%24format=JSON', "Attractions_activity"),
    ('https://tdx.transportdata.tw/api/basic/v2/Tourism/ScenicSpot?%24top=100&%24format=JSON', "scenicSpot"),
    ('https://tdx.transportdata.tw/api/tourism/service/odata/V2/Tourism/Attraction?%24top=200', "Attractions"),
    ('https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Freeway?%24top=100&%24format=JSON', 'highway'),
    #熱圖-高速公路
    ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/Highway?%24format=JSON", "VD"),
    ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/Highway?%24format=JSON", "Section"),
    ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/Highway?%24format=JSON", "Congestion")
     ]
    #更新縣市的CCTV
    for city in citylist:
        get_url.append((f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/{city}?%24top=100&%24format=JSON', f'CCTV-{city}'))
    
    print("--------------CCTV Data start Update------------------------")
    for url, filename in get_url:
        try:
            getkey.getjson(url, filename)
            print(f"{filename} has been updated")
        except Exception as e:
            print(f"---------{filename} Update failed--------")
            print(e)
        finally:
            time.sleep(0.5)
    print("--------------CCTV Data Updated------------------------")
    
    #熱圖-將所有縣市VD資料全部整理在一起
    with open('data/CountryData.json', 'w') as file:
        file.write('')  # 清空文件内容
    countrydata = []
    for city in citylist:
        try:
            countrydata.append(func.getCountryData(city)) 
            print(f"---------{city}-VD has been add to CountryData--------")
            
        except Exception as e:
            
            print(f"---------{city}-VD Update failed--------")
            print(e)
        finally:
            time.sleep(0.5)
 
    with open('data/CountryData.json', 'w') as file:
        file.write(json.dumps(countrydata, ensure_ascii=False))
        
            
    print("--------------VD Data Updated------------------------")
    
    return jsonify({'status':'success'})

@app.route('/CCTV')
def get_CCTV():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    df = pd.DataFrame(columns=CCTV_column)
    for city in citylist:        
        with open(f'data/CCTV-{city}.json', 'r', encoding='utf-8') as f:
            try:
                testTV = json.load(f)['CCTVs']
            except Exception:
                testTV = {}
        city_data = {}
        for TV in testTV:
            for col in CCTV_column:
                if col in TV:
                    city_data[col] = TV[col]
                else:
                    pass
                    #print(city, col)
            df = pd.concat([df, pd.DataFrame([city_data])], ignore_index=True)
            
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lng))
    print(df.shape[1])
    df = df.sort_values(by='DistanceToInputPoint_km').head(10)
            
    df.fillna('', inplace=True)

    return jsonify(df.to_dict(orient='records'))

@app.route('/highwayCCTV', methods=['GET'])
def get_highwayCCTV():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    df = pd.DataFrame()
    city_data = {}
    with open(f'data/highway.json', 'r', encoding='utf-8') as f:
        highTV = json.load(f)['CCTVs']
    for TV in highTV:
        for col in CCTV_column:
            if col in TV:
                city_data[col] = TV[col]
                #print(city, col)
        df = pd.concat([df, pd.DataFrame([city_data])], ignore_index=True)
    
    df.fillna('', inplace=True)
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lng))
    df = df.sort_values(by='DistanceToInputPoint_km').head(10)
    
    return jsonify(df.to_dict(orient='records'))
    
    

@app.route('/attractions_activity')
def get_attractions_activity():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    #getkey.getjson('https://tdx.transportdata.tw/api/basic/v2/Tourism/Activity?%24orderby=starttime%20desc&%24top=80&%24format=JSON', "Attractions_activity")
    df = pd.DataFrame()
    with open(f'data/Attractions_activity.json', 'r', encoding='utf-8') as f:
        Attractions_activity = json.load(f)
    df = pd.DataFrame(Attractions_activity)
    current_time = datetime.now(timezone.utc)

# 筛选 StartTime 大于当前时间的行
    # 将 StartTime 列转换为 datetime 类型
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    # 获取当前时间
    current_time = datetime.now(timezone.utc)
    # 筛选 StartTime 大于当前时间的行
    df = df[df['StartTime'] > current_time]
   
    df['PositionLon'] = df['Position'].apply(lambda x: x['PositionLon'])
    df['PositionLat'] = df['Position'].apply(lambda x: x['PositionLat'])
    df.drop(columns=['Position'], inplace=True)
    
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lng))
    df = df.sort_values(by='DistanceToInputPoint_km')
    
    df.fillna('', inplace=True)
    return jsonify(df.to_dict(orient='records'))

@app.route('/attractions')
def get_attractions():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    # getkey.getjson('https://tdx.transportdata.tw/api/tourism/service/odata/V2/Tourism/Attraction?%24top=200', "Attractions")
    df = pd.DataFrame()
    with open(f'data/Attractions.json', 'r', encoding='utf-8') as f:
        Attractions = json.load(f)['value']
    df = pd.DataFrame(Attractions)
    df.drop(columns=['PaymentMethods'], inplace=True)
    
    df.fillna('', inplace=True)
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lng))
    df = df.sort_values(by='DistanceToInputPoint_km').head(10)
    
    return jsonify(df.to_dict(orient='records'))

@app.route('/scenicSpot', methods=['GET'])
def get_scenic():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    # getkey.getjson('https://tdx.transportdata.tw/api/basic/v2/Tourism/ScenicSpot?%24top=100&%24format=JSON', "scenicSpot")
    df = pd.DataFrame()
    with open(f'data/scenicSpot.json', 'r', encoding='utf-8') as f:
        Attractions_activity = json.load(f)
    df = pd.DataFrame(Attractions_activity)

    # 提取嵌套的 PositionLon 和 PositionLat
    df['PositionLon'] = df['Position'].apply(lambda x: x['PositionLon'])
    df['PositionLat'] = df['Position'].apply(lambda x: x['PositionLat'])
    df.drop(columns=['Position'], inplace=True)
    
    df.fillna('', inplace=True)
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lng))
    df = df.sort_values(by='DistanceToInputPoint_km').head(10)
    
    return jsonify(df.to_dict(orient='records'))

@app.route('/asklocation' , methods=['GET'])
def send_location():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    print(lat, lon)
    

    
    

    return jsonify({"return ":200})


@app.route('/heatdata' , methods=['GET'])
def get_heatdata():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    data = func.create_heatmap(lat, lng)
    
    
    return jsonify(data)

if __name__ == '__main__':

    app.run(debug=True)
