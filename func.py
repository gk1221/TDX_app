import json
import pandas as pd
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap
import getkey

# 讀取數據
def getHighwayData():
    # 抓省道即時發布路況
    getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/Highway?%24format=JSON", "Congestion")
    with open('data/Congestion.json', 'r', encoding='utf-8') as f:
        Congestion = json.load(f)
    # 抓省道發布路段
    getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/Highway?%24format=JSON", "Section")
    with open('data/Section.json', 'r', encoding='utf-8') as f:
        Section = json.load(f)
    # 抓省道車輛偵測器
    getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/Highway?%24format=JSON", "VD")
    with open('data/VD.json', 'r', encoding='utf-8') as f:
        VD = json.load(f)

    #省道即時路況資料整理
    pd_Congestion = pd.DataFrame(Congestion)
    LiveTraffics = pd.DataFrame(pd_Congestion['LiveTraffics'])
    LiveTraffics['SectionID'] = LiveTraffics['LiveTraffics'].apply(lambda x: x['SectionID'])
    LiveTraffics['CongestionLevel'] = LiveTraffics['LiveTraffics'].apply(lambda x: x['CongestionLevel'])
    HighwayCongestion = LiveTraffics.drop(columns='LiveTraffics')

    #省道發布路段資料整理
    pd_Section = pd.DataFrame(Section)
    Sections = pd.DataFrame(pd_Section['Sections'])
    Sections['SectionID'] = Sections['Sections'].apply(lambda x : x['SectionID'])
    Sections['LinkIDs'] = Sections['Sections'].apply(lambda x : x['LinkIDs'])
    Sections = Sections.drop(columns='Sections')
    Sections = Sections.explode('LinkIDs')
    Sections['LinkID'] = Sections['LinkIDs'].apply(lambda x: x['LinkID'])
    HighwaySection = Sections.drop(columns = 'LinkIDs')
    
    #省道車輛偵測器資料處理
    pd_VD = pd.DataFrame(VD)
    VDs = pd.DataFrame(pd_VD, columns=['VDs'])
    VDs['VDID'] = VDs['VDs'].apply(lambda x : x['VDID'])
    VDs['DetectionLinks'] = VDs['VDs'].apply(lambda x : x['DetectionLinks'])
    VDs['PositionLat'] = VDs['VDs'].apply(lambda x : x['PositionLat'])
    VDs['PositionLon'] = VDs['VDs'].apply(lambda x : x['PositionLon'])
    HighwayVD = VDs.drop(columns='VDs')
    HighwayVD = HighwayVD.explode('DetectionLinks')
    HighwayVD['LinkID'] = HighwayVD['DetectionLinks'].apply(lambda x: x['LinkID'])
    HighwayVD = HighwayVD.drop(columns='DetectionLinks')

    #合併資料
    SectionCongestion = pd.merge(HighwayCongestion,HighwaySection, how='inner', on='SectionID')
    HighwayData = pd.merge(HighwayVD,SectionCongestion, how='inner', on='LinkID')
    HighwayData = HighwayData.drop(columns='VDID')
    HighwayData = HighwayData.drop(columns='LinkID')
    HighwayData = HighwayData.drop(columns='SectionID')

    return HighwayData

def find_nearest_points(lat, lon, data):
    #除去重複數據，我也不曉得為什麼有重複的
    data = data.drop_duplicates(subset=['PositionLat', 'PositionLon'])
    # 計算距離
    data['distance'] = data.apply(lambda row: geodesic((lat, lon), (row['PositionLat'], row['PositionLon'])).meters, axis=1)
    # 按距離排序並取前 top_n 個點
    nearest_points = data.nsmallest(20, 'distance') #原則上前面的數字是代表要抓幾個點的意思，我先用20，用10的時候我覺得有點少，再看學長你怎麼想
    return nearest_points

def create_heatmap(lat, lon, data):
    nearest_points = find_nearest_points(lat, lon, data)
    
    # 創建地圖
    m = folium.Map(location=[lat, lon], zoom_start=12)
    
    # 調整型態
    nearest_points['PositionLat'] = nearest_points['PositionLat'].astype(float)
    nearest_points['PositionLon'] = nearest_points['PositionLon'].astype(float)
    nearest_points['CongestionLevel'] = nearest_points['CongestionLevel'].astype(float)

    # 準備熱力圖數據
    heat_data = [[row['PositionLat'], row['PositionLon'], row['CongestionLevel']] for index, row in nearest_points.iterrows()]
    
    # 添加熱力圖層，這裡的radius學長可以看要多少比較好
    HeatMap(heat_data, radius =100).add_to(m)
    
    # 保存並返回地圖，存起來只是為了測試
    m.save('heatmap.html')
    return m

# 示例使用
lat = 23.5 # 替換為你的緯度
lon = 120.5  # 替換為你的經度

# print(getHighwayData())
print(find_nearest_points(lat,lon,getHighwayData()))
create_heatmap(lat, lon, getHighwayData())