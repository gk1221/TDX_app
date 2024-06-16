//pase CCTV
const flask_ip = "http://127.0.0.1:5000";

const parseCCTV = (data, group) => {
  group.clearLayers();

  var MarkerIcon = L.AwesomeMarkers.icon({
    icon: "facetime-video",
    markerColor: group == highway_Group ? "lightgray" : "gray",
  });

  data.forEach((element) => {
    var popContent = `
    <div style="width:400px;height:300px;">
    <h2 class="myhead">${
      element.RoadName != ""
        ? element.RoadName
        : element.SurveillanceDescription
    }</h2>
      <div style="min-width: 360px; min-height: 280px;" >
        <iframe style="min-width: 360px; min-height: 260px;"  src="${
          element.VideoStreamURL
        }" frameborder="0" allowfullscreen></iframe>
      </div>
    </div>`;

    var marker = L.marker([element.PositionLat, element.PositionLon], {
      icon: MarkerIcon,
    });

    marker.bindPopup(popContent, {
      maxWidth: 2500,
      lazy: true,
    });

    marker.addTo(group);
  });
};

const parsescenic = (data, group) => {
  group.clearLayers();
  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "blue",
  });
  data.forEach((element) => {
    var popContent = `    <div style="width:400px;height:200px;background='green'">
          <h2  class="myhead"> ${element.ScenicSpotName}</h2>
          <p>  ${element.DescriptionDetail.substring(0, 100) + " ......"}  </p>
          </div>`;
    var marker = L.marker([element.PositionLat, element.PositionLon], {
      icon: redMarkerIcon,
    });
    marker.bindPopup(popContent, {
      maxWidth: 1800,
      lazy: true,
    });
    marker.addTo(group);
  });
};

const parseattractions = (data, group) => {
  group.clearLayers();
  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "orange",
  });
  data.forEach((element) => {
    var popContent = `    <div style="width:400px;height:300px;background='green'">
            <h2  class="myhead"> ${element.AttractionName}</h2>
            <p>  ${element.Description.substring(0, 100) + " ......"}  </p>
            <img src='${element.Images[0].URL}'  class="scenice-pic"/>
            </div>`;
    var marker = L.marker([element.PositionLat, element.PositionLon], {
      icon: redMarkerIcon,
    });
    marker.bindPopup(popContent, {
      maxWidth: 1800,
      lazy: true,
    });
    marker.addTo(group);
  });
};
//景點活動位置get

const parseactivity = (data, group) => {
  group.clearLayers();

  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "green",
  });
  data.forEach((element) => {
    var popContent = `    <div style="width:400px;height:200px;background='green'">
              <h2  class="myhead"> ${element.ActivityName}</h2>
              <p>  ${
                element.Description == "無"
                  ? element.Description
                  : element.Description.substring(0, 100) + " ......"
              }  </p>
              </div>`;
    var marker = L.marker([element.PositionLat, element.PositionLon], {
      icon: redMarkerIcon,
    });
    marker.bindPopup(popContent, {
      maxWidth: 1800,
      lazy: true,
    });
    marker.addTo(group);
    //layerGroup.addLayer(marker);
  });
};

// 獲取數據並更新熱圖
const updateHeatmap = (data) => {
  if (heatLayer) {
    map.removeLayer(heatLayer);
  }
  heatLayer = L.heatLayer(data, { radius: 80, blur: 60 }).addTo(map);
};

// 獲取數據並更新熱圖
const updateCountryHeatmap = (data) => {
  var clean_data = [];
  data.forEach((element) => {
    clean_data.push([
      element.PositionLat,
      element.PositionLon,
      element.CongestionLevel,
    ]);
  });
  console.log(clean_data);
  heatLayer = L.heatLayer(clean_data, { radius: 80, blur: 60 }).addTo(map);
};

const clickSearch = (event) => {
  const lat = event.latlng.lat.toFixed(5);
  const lng = event.latlng.lng.toFixed(5);
  //alert(`搜尋位置\n經度 ： ${lat}\n緯度 ： ${lng}`);
  console.log(`搜尋位置\n經度 ： ${lat}\n緯度 ： ${lng}`);
  var Herecon = L.icon({
    iconUrl: "./hereicon.png",
    iconSize: [38, 38], // 图标大小
    iconAnchor: [19, 19], // 图标锚点（图标的哪一点与坐标对应）
    popupAnchor: [-3, -76], // 弹出窗口的锚点
  });
  currentMarker != null ? map.removeLayer(currentMarker) : "";
  currentMarker = L.marker([lat, lng], { icon: Herecon }).addTo(map);

  //測試
  fetch(`${flask_ip}/asklocation?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
    })
    .catch((error) => console.error("Error fetching data:", error));
  //fetch highway CCTV
  fetch(`${flask_ip}/highwayCCTV?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      parseCCTV(data, highway_Group);
    })
    .catch((error) => console.error("Error fetching highwayCCTV data:", error));
  //fetch CCTV
  fetch(`${flask_ip}/CCTV?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      parseCCTV(data, CCTV_Group);
    })
    .catch((error) => console.error("Error fetching highwayCCTV data:", error));
  //fetch scenicSpot
  fetch(`${flask_ip}/scenicSpot?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      parsescenic(data, scenic_Group);
    })
    .catch((error) => console.error("Error fetching scenicSpot data:", error));
  //fetch attractions
  fetch(`${flask_ip}/attractions?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      parseattractions(data, attraction_Group);
    })
    .catch((error) => console.error("Error fetching attractions data:", error));
  //fetch attractions activities
  fetch(`${flask_ip}/attractions_activity?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      parseactivity(data, activity_Group);
    })
    .catch((error) => console.error("Error fetching attractions data:", error));

  //fetch heatdata

  fetch(`${flask_ip}/heatdata?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      updateHeatmap(data, heatLayer);
    })
    .catch((error) => console.error("Error fetching heatdata data:", error));

  // fetch(`${flask_ip}/countryheatdata?lat=${lat}&lng=${lng}`)
  //   .then((response) => response.json())
  //   .then((data) => {
  //     console.log(data);
  //     updateCountryHeatmap(data, heatLayer);
  //   })
  //   .catch((error) => console.error("Error fetching heatdata data:", error));
};

const updateDate = (data_name, out_name) => {
  fetch(`${flask_ip}/update?${data_name}=1`)
    .then((response) => response.json())
    .then((data) => {
      alert(`更新${out_name}資料成功`);
    })
    .catch((error) =>
      console.error(`Error fetching ${data_name} data:`, error)
    );
};

//fit map function
const fitMapToLayer = (layer) => {
  layer = layer.target;

  if (layer.getBounds) {
    map.fitBounds(layer.getBounds());
  } else if (layer.getLatLng) {
    console.log("here");
    map.setView([23.800983, 120.772569], 7.3); // 你可以調整縮放級別
  }
};
