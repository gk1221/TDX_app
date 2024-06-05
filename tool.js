//pase CCTV
function getCCTV(url, group) {
  fetch(`http://127.0.0.1:5000/${url}`)
    .then((response) => response.json())
    .then((data) => {
      parseCCTV(data, group);
    })
    .catch((error) => console.error("Error fetching data:", error));
}

function parseCCTV(data, group) {
  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "facetime-video",
    markerColor: "lightgray",
  });
  //console.log(redMarkerIcon)
  data.forEach((element) => {
    var popContent = `<h2>${
      element.RoadName != ""
        ? element.RoadName
        : element.SurveillanceDescription
    }</h2>
                      <iframe src="${
                        element.VideoStreamURL
                      }" width="600" height="300" frameborder="0" allowfullscreen></iframe>`;

    var marker = L.marker([element.PositionLat, element.PositionLon], {
      icon: redMarkerIcon,
    });

    marker.bindPopup(popContent, {
      maxWidth: 2500,
      lazy: true,
    });

    marker.addTo(group);
  });

  //var layer2 = L.circle([51.508, -0.11], { color: 'red', radius: 500 }).bindPopup('I am layer 2.');
  //layer2.on('add', fitMapToLayer)
}

//風景位置get
function getscenic(group) {
  fetch("http://127.0.0.1:5000/scenicSpot")
    .then((response) => response.json())
    .then((data) => {
      parsescenic(data, group);
    })
    .catch((error) => console.error("Error fetching data:", error));
}
function parsescenic(data, group) {
  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "blue",
  });
  data.forEach((element) => {
    var popContent = `    <div style="width:200px;height:100px;background='green'">
          <h3> ${element.ScenicSpotName}</h3>
          <p>  ${element.DescriptionDetail.substring(0, 100) + " ......"}  </p>
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
  });
}
//景點位置get
function getattraction(group) {
  fetch("http://127.0.0.1:5000/attractions")
    .then((response) => response.json())
    .then((data) => {
      parseattractions(data, group);
    })
    .catch((error) => console.error("Error fetching data:", error));
}
function parseattractions(data, group) {
  var redMarkerIcon = L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: "orange",
  });
  data.forEach((element) => {
    var popContent = `    <div style="width:200px;height:100px;background='green'">
            <h3> ${element.AttractionName}</h3>
            <p>  ${element.Description.substring(0, 100) + " ......"}  </p>
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
}
//景點活動位置get
function getactivity(group) {
  fetch("http://127.0.0.1:5000/attractions_activity")
    .then((response) => response.json())
    .then((data) => {
      parseactivity(data, group);
    })
    .catch((error) => console.error("Error fetching data:", error));
}
function parseactivity(data, group) {
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
}

function isDateInThePast(dateString) {
  var inputDate = new Date(dateString);
  var now = new Date();
  //   console.log(inputDate);
  //   console.log(now);
  return inputDate < now;
}

// 獲取數據並更新熱圖
function updateHeatmap() {
  fetch("http://127.0.0.1:5000/busdata")
    .then((response) => response.json())
    .then((data) => {
      //console.log(data)
      if (heatLayer) {
        map.removeLayer(heatLayer);
      }
      heatLayer = L.heatLayer(data, { radius: 25 }).addTo(map);
    })
    .catch((error) => console.error("Error fetching data:", error));
}

function clickAPI(event) {
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
}
