**getkey.py**

- _app_id, app_key_ : 放入要存取 API 的金鑰
- _getjson(url, filename)_ : 從 API URL 抓資料存成 JSON 檔案，預設存到 data/資料夾下

**Bus-hot.html**

- 先產生資料 data/test-\* -> CCTV.ipynb 前四句
- 安裝函式庫（用管理者權限）

```
  sudo pip install flask flask_cors geopy folium
```

- 打開網頁測試

```
  python final-flask.py
```

#### 0615 更新:

1. 將更新資料的地方都在/update 的路徑
2. 獲取省道資料直接進行熱圖資料產出 -> final_tool.js 處理產出熱圖(把前端工作先分開處理)
3. 重新定義流程 : 由點擊地點開始去撈取 API，產出景點、CCTV 內容、熱圖範圍等
4. 後續繼續處理 :
   - 將縣市 VD 資料放入地圖當中，方法是撈取所有城市的 VD 後結合放在一起，遇到的問題是常常會很醜處理不好( 如 countrydata.json
   - 增加推薦功能，可以從景點遠近、VD 所得到的壅塞程度來給一個分數，但需要新增在左側的上層欄
   - leaflet 原生的醜控制鈕，透過 CSS 修改
