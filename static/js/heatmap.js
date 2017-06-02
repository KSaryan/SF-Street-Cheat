heatmapData = []
function makeHeatMap(result){
    for (i=0; i<(result['all_geos']).length; i++){
        var lngLat = result['all_geos'][i];
        heatmapData.push(new google.maps.LatLng(lngLat[1], lngLat[0]))
}

    var sanFrancisco = new google.maps.LatLng(37.774546, -122.433523);

    map = new google.maps.Map(document.getElementById('map2'), {
      center: sanFrancisco,
      zoom: 13,
      mapTypeId: 'satellite'
    });

    var heatmap = new google.maps.visualization.HeatmapLayer({
      data: heatmapData
    });
    heatmap.setMap(map);
}


data = {}

$.get('/get_all_locations.json', data, makeHeatMap);

//  $.get('/nearby_cleanings.json', address_info, showLocations);
// }










