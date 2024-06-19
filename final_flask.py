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

def get_url_data(group ,get_url):
    print(f"--------------{group} Data start Update------------------------")
    for url, filename in get_url:
        try:
            getkey.getjson(url, filename)
            print(f"{filename} has been updated")
        except Exception as e:
            print(f"---------{filename} Update failed--------")
            print(e)
        finally:
            time.sleep(0.5)
    print(f"--------------{group} Data Updated------------------------\n")
        
        
@app.route('/update')
def get_update():
    VD = request.args.get('VD')
    spot = request.args.get('spot')
    CCTV = request.args.get('CCTV')
    
    
    if(spot == '1'):
        spot_get_url = [
            ('https://tdx.transportdata.tw/api/basic/v2/Tourism/Activity?%24orderby=starttime%20desc&%24top=80&%24format=JSON', "Attractions_activity"),
                ('https://tdx.transportdata.tw/api/basic/v2/Tourism/ScenicSpot?%24top=100&%24format=JSON', "scenicSpot"),
                ('https://tdx.transportdata.tw/api/tourism/service/odata/V2/Tourism/Attraction?%24top=200', "Attractions"),
        ]
        get_url_data('spot', spot_get_url)
    
    #更新縣市的CCTV
    if(CCTV == '1'):
        CCTV_get_url = [
        ('https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/Freeway?%24top=100&%24format=JSON', 'highway'),
        ]
        for city in citylist:
            CCTV_get_url.append((f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/{city}?%24top=100&%24format=JSON', f'CCTV-{city}'))
        
        
        get_url_data('CCTV', CCTV_get_url) 
    
    #熱圖-將所有縣市VD資料全部整理在一起
    
    if(VD == '1'):
    
        heat_get_url=[
        ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/Highway?%24format=JSON", "VD"),
        ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/Highway?%24format=JSON", "Section"),
        ("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/Highway?%24format=JSON", "Congestion")]
        for url, filename in heat_get_url:
            try:
                getkey.getjson(url, filename)
                print(f"{filename} has been updated")
            except Exception as e:
                print(f"---------{filename} Update failed--------")
                print(e)
            finally:
                time.sleep(0.5)
    
        # #VD in country        
        # countrydata = []
        # for city in citylist:
        #     try:
        #         countrydata.append(func.getCountryData(city)) 
        #         print(f"---------{city}-VD has been add to CountryData--------")
        #     except Exception as e:
        #         print(f"---------{city}-VD Update failed--------")
        #         print(e)
        #     finally:
        #         time.sleep(0.5)
    
        # with open('data/CountryData.json', 'w') as file:
        #     file.write('')  # 清空文件内容
        #     file.write(json.dumps(countrydata, ensure_ascii=False))
            
                
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
    df = df.sort_values(by='DistanceToInputPoint_km').head(10)
    
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

@app.route('/allheatdata' , methods=['GET'])
def get_heatdata2():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    data = func.create_heatmap2(lat, lng)
    return jsonify(data)

@app.route('/countryheatdata' , methods=['GET'])
def get_country_heatdata():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    data = func.create_heatmap(lat, lng)
    
    with open(f'data/Countrydata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df_data = []

    # 遍历每个条目
    for entry in data:
        country = entry['country']
        position_lat = entry['data']['PositionLat']
        position_lon = entry['data']['PositionLon']
        congestion_level = entry['data']['CongestionLevel']
        
        # 确定最大长度以便对齐数据
        max_length = max(len(position_lat), len(position_lon), len(congestion_level))
        
        # 构建数据列表
        for i in range(max_length):
            lat = position_lat.get(str(i), None)
            lon = position_lon.get(str(i), None)
            congestion = congestion_level.get(str(i), None)
            df_data.append({
                'country': country,
                'PositionLat': lat,
                'PositionLon': lon,
                'CongestionLevel': congestion
            })

    # 创建 DataFrame
    df = pd.DataFrame(df_data)
    
    columns_to_check = ['PositionLat', 'PositionLon', 'CongestionLevel']
    df = df.dropna(subset=columns_to_check)
    df['DistanceToInputPoint_km'] = df.apply(calculate_distance, axis=1, args=(lat,lon))


    
    
    return jsonify(df.head(10).to_dict(orient='records'))

if __name__ == '__main__':

    app.run(debug=True)
