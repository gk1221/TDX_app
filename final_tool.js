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
    <h2>${
      element.RoadName != ""
        ? element.RoadName
        : element.SurveillanceDescription
    }</h2>
                      <iframe src="${
                        element.VideoStreamURL
                      }" style="min-width: 100%; min-height: 100%;" frameborder="0" allowfullscreen></iframe>
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
    var popContent = `    <div style="width:200px;height:100px;background='green'">
          <h3> ${element.ScenicSpotName}</h3>
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
    var popContent = `    <div style="width:200px;height:300px;background='green'">
            <h3> ${element.AttractionName}</h3>
            <p>  ${element.Description.substring(0, 100) + " ......"}  </p>
            <img src='${
              element.Images[0].URL
            }'  style="max-width: 100%; max-height: 100%;"/>
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
const getactivity = (group) => {
  fetch(`${flask_ip}/attractions_activity`)
    .then((response) => response.json())
    .then((data) => {
      parseactivity(data, group);
    })
    .catch((error) => console.error("Error fetching data:", error));
};
const parseactivity = (data, group) => {
  var layerGroup = L.featureGroup();

  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "green",
  });
  data.forEach((element) => {
    // // console.log(element);
    // if (isDateInThePast(element.startTime)) {
    //   //   console.log(element.startTime);
    // } else console.log("ddd");
    var popContent = `    <div style="width:200px;height:100px;background='green'">
              <h5> ${element.ActivityName}</h5>
              <p>  ${
                element.Description == "無"
                  ? ""
                  : element.Description.substring(0, 100) + " ......"
              }  </p>
              </div>`;
    var marker = L.marker(
      [element.Position.PositionLat, element.Position.PositionLon],
      {
        icon: redMarkerIcon,
      }
    );
    marker.bindPopup(popContent, {
      maxWidth: 1800,
      lazy: true,
    });
    marker.addTo(group);
    //layerGroup.addLayer(marker);
  });
};

const isDateInThePast = (dateString) => {
  var inputDate = new Date(dateString);
  var now = new Date();
  //   console.log(inputDate);
  //   console.log(now);
  return inputDate < now;
};

// 獲取數據並更新熱圖
const updateHeatmap = (data) => {
  if (heatLayer) {
    map.removeLayer(heatLayer);
  }
  heatLayer = L.heatLayer(data, { radius: 60 }).addTo(map);
};

const clickAPI = (event) => {
  alert(event.latlng);
  const clickLatLng = event.latlng;
  const markersWithin10Km = [];

  highway_Group.eachLayer((layer) => {
    const markerLatLng = layer.getLatLng();
    const distance = map.distance(clickLatLng, markerLatLng);

    if (distance <= 10000) {
      // 10公里範圍內
      markersWithin10Km.push(layer);
    }

    // 清除以前的標示
    highway_Group.eachLayer((layer) => {
      layer.setIcon(new L.Icon.Default());
    });

    // 標示10公里範圍內的點
    markersWithin10Km.forEach((marker) => {
      marker.setIcon(
        new L.Icon({
          iconUrl: "https://leafletjs.com/examples/custom-icons/leaf-red.png",
          shadowUrl:
            "https://leafletjs.com/examples/custom-icons/leaf-shadow.png",
          iconSize: [38, 95], // size of the icon
          shadowSize: [50, 64], // size of the shadow
          iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
          shadowAnchor: [4, 62], // the same for the shadow
          popupAnchor: [-3, -76], // point from which the popup should open relative to the iconAnchor
        })
      );
    });
  });
};

const clickSearch = (event) => {
  const lat = event.latlng.lat.toFixed(5);
  const lng = event.latlng.lng.toFixed(5);
  alert(`搜尋位置\n經度 ： ${lat}\n緯度 ： ${lng}`);

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

  //fetch heatdata
  fetch(`${flask_ip}/heatdata?lat=${lat}&lng=${lng}`)
    .then((response) => response.json())
    .then((data) => {
      updateHeatmap(data, heatLayer);
    })
    .catch((error) => console.error("Error fetching heatdata data:", error));
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
