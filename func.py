import json
import pandas as pd
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap
import getkey

# 讀取數據，不是所有縣市都有，以下是有的縣市及縣市資料數目，
# 台北（'Taipei'）：802 ，台南（'Tainan'）：7，高雄（'Kaohsiung'）：0（皆為-99），
# 桃園（'Taoyuan'）：246，雲林市（'YunlinCounty'）：6，屏東市（'PingtungCounty'）：27，數目會是動態的
def check_update():
    
    raise Exception("Update failed")
def getCountryData(country):
    #抓縣市即時發布路況
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/City/"+country+"?%24format=JSON", f"CountryCongestion-{country}")
    with open(f'data/CountryCongestion-{country}.json', 'r', encoding='utf-8') as f:
        CountryCongestion = json.load(f)
        print()
    #抓縣市發布路段
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/City/"+country+"?%24format=JSON", f"CountrySection-{country}")
    with open(f'data/CountrySection-{country}.json', 'r', encoding='utf-8') as f:
        CountrySection = json.load(f)
    #抓縣市車輛偵測器
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/City/"+country+"?%24format=JSON", f"CountryVD-{country}")
    with open(f'data/CountryVD-{country}.json', 'r', encoding='utf-8') as f:
        CountryVD = json.load(f)
    
    #縣市即時發布路況整理
    pd_CountryCongestion = pd.DataFrame(CountryCongestion)
    pd_CountryCongestion = pd.DataFrame(pd_CountryCongestion['LiveTraffics'])
    pd_CountryCongestion['SectionID'] = pd_CountryCongestion['LiveTraffics'].apply(lambda x: x['SectionID'])
    pd_CountryCongestion['CongestionLevel'] = pd_CountryCongestion['LiveTraffics'].apply(lambda x: x['TravelSpeed'] if x['TravelSpeed']<=0  else (100-int(x['TravelSpeed']) )  )
    pd_CountryCongestion = pd_CountryCongestion.drop(columns='LiveTraffics')
    #print(pd_CountryCongestion.to_dict())

    #縣市發布路段整理
    pd_CountrySection = pd.DataFrame(CountrySection)
    pd_CountrySection = pd.DataFrame(pd_CountrySection['Sections'])    
    pd_CountrySection['SectionID'] = pd_CountrySection['Sections'].apply(lambda x : x['SectionID'])
    pd_CountrySection['LinkIDs'] = pd_CountrySection['Sections'].apply(lambda x: x['LinkIDs'] if 'LinkIDs' in x else "")
    pd_CountrySection = pd_CountrySection.drop(columns='Sections')
    pd_CountrySection = pd_CountrySection.explode('LinkIDs')
    pd_CountrySection['LinkID'] = pd_CountrySection['LinkIDs'].apply(lambda x: x['LinkID'] if isinstance(x, dict) else "")
    pd_CountrySection = pd_CountrySection.drop(columns = 'LinkIDs')
    #print(pd_CountrySection.to_dict())
    #縣市車輛偵測器整理
    pd_CountryVD = pd.DataFrame(CountryVD)
    pd_CountryVD = pd.DataFrame(pd_CountryVD, columns=['VDs'])
    pd_CountryVD['VDID'] = pd_CountryVD['VDs'].apply(lambda x : x['VDID'])
    pd_CountryVD['DetectionLinks'] = pd_CountryVD['VDs'].apply(lambda x : x['DetectionLinks'])
    pd_CountryVD['PositionLat'] = pd_CountryVD['VDs'].apply(lambda x : x['PositionLat'])
    pd_CountryVD['PositionLon'] = pd_CountryVD['VDs'].apply(lambda x : x['PositionLon'])
    pd_CountryVD = pd_CountryVD.drop(columns='VDs')
    pd_CountryVD = pd_CountryVD.explode('DetectionLinks')
    pd_CountryVD = pd_CountryVD.dropna(subset=['DetectionLinks'])
    pd_CountryVD['LinkID'] = pd_CountryVD['DetectionLinks'] .apply(lambda x: x['LinkID'])
    pd_CountryVD = pd_CountryVD.drop(columns='DetectionLinks')
    #print(pd_CountryVD.to_dict())
    pd_CountryVD.fillna("", inplace=True)
    
    
    #合併資料
    CountrySectionCongestion = pd.merge(pd_CountryCongestion,pd_CountrySection, how='inner', on='SectionID')
    CountryData = pd.merge(pd_CountryVD,CountrySectionCongestion, how='inner', on='LinkID')

    CountryData = CountryData.drop(columns='VDID')
    CountryData = CountryData.drop(columns='LinkID')
    CountryData = CountryData.drop(columns='SectionID')
    #因為congestion level等於99的話，代表未開放通行，所以我刪掉這部分數據
    CountryData['CongestionLevel'].fillna(0, inplace=True)
    CountryData['CongestionLevel'] = CountryData['CongestionLevel'].astype(int)
    CountryData = CountryData[CountryData['CongestionLevel'] > 0]
    combine = {"country":country, "data":CountryData.to_dict()}
    #print(combine)
    return combine

def getHighwayData():
    # 抓省道即時發布路況
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/Highway?%24format=JSON", "Congestion")
    with open('data/Congestion.json', 'r', encoding='utf-8') as f:
        Congestion = json.load(f)
    # 抓省道發布路段
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/Highway?%24format=JSON", "Section")
    with open('data/Section.json', 'r', encoding='utf-8') as f:
        Section = json.load(f)
    # 抓省道車輛偵測器
    #getkey.getjson("https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/Highway?%24format=JSON", "VD")
    with open('data/VD.json', 'r', encoding='utf-8') as f:
        VD = json.load(f)

    #省道即時路況資料整理
    pd_Congestion = pd.DataFrame(Congestion)
    LiveTraffics = pd.DataFrame(pd_Congestion['LiveTraffics'])
    LiveTraffics['SectionID'] = LiveTraffics['LiveTraffics'].apply(lambda x: x['SectionID'])
    LiveTraffics['CongestionLevel'] = LiveTraffics['LiveTraffics'].apply(lambda x: 100-int(x['TravelSpeed']) if x['TravelSpeed']>0  else -1  )
    LiveTraffics = LiveTraffics[LiveTraffics['CongestionLevel'] > 0]
    HighwayCongestion = LiveTraffics.drop(columns='LiveTraffics')

    #省道發布路段資料整理
    pd_Section = pd.DataFrame(Section)
    Sections = pd.DataFrame(pd_Section['Sections'])
    Sections['SectionID'] = Sections['Sections'].apply(lambda x : x['SectionID'])
    Sections['SectionName'] = Sections['Sections'].apply(lambda x : x['SectionName'])
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

def find_nearest_points(lat, lon):
    #除去重複數據，我也不曉得為什麼有重複的，後來發現是抓的資料會有重複的，現在不曉得是什麼原因
    data = getHighwayData()
    data = data.drop_duplicates(subset=['PositionLat', 'PositionLon'])
    # 計算距離
    data['distance'] = data.apply(lambda row: geodesic((lat, lon), (row['PositionLat'], row['PositionLon'])).meters, axis=1)
    # 按距離排序並取前 20 點
    nearest_points = data.nsmallest(30, 'distance') #原則上前面的數字是代表要抓幾個點的意思，我先用20，用10的時候我覺得有點少，再看學長你怎麼想
    return nearest_points

def create_heatmap(lat, lon):
    nearest_points = find_nearest_points(lat, lon)
    
    # 創建地圖
    #m = folium.Map(location=[lat, lon], zoom_start=12)
    
    # 調整型態
    nearest_points['PositionLat'] = nearest_points['PositionLat'].astype(float)
    nearest_points['PositionLon'] = nearest_points['PositionLon'].astype(float)
    nearest_points['CongestionLevel'] = nearest_points['CongestionLevel'].astype(float)

    # 準備熱力圖數據
    heat_data = [[row['PositionLat'], row['PositionLon'], row['CongestionLevel']] for index, row in nearest_points.iterrows()]
    
    return {"data": heat_data , "roadname": [[row['SectionName']] for index, row in nearest_points.iterrows()]}
    # # 添加熱力圖層，這裡的radius學長可以看要多少比較好
    # HeatMap(heat_data, radius =100).add_to(m)
    
    # # 保存並返回地圖，存起來只是為了測試
    # m.save('heatmap.html')
    # return m


# # 示例使用
# lat = 23.5 # 替換為你的緯度
# lon = 120.5  # 替換為你的經度

# # print(getHighwayData())
# # print(find_nearest_points(lat,lon,getHighwayData()))
 # # create_heatmap(lat, lon, getHighwayData())
# country = "Taipei"
# print(getCountryData(country))
