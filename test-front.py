import folium

# 創建地圖
m = folium.Map(location=(25.033964, 121.564472), zoom_start=15)

# 保存地圖
m.save("test-index.html")
