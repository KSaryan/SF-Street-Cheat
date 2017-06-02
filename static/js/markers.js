var allMarkers = []


function removeMarkers(){
  for(i=0; i<allMarkers.length; i++){
      allMarkers[i].setMap(null);
  }
  allMarkers=[];
}

function showLocations(result){
  removeMarkers();
  for (key in result){
      var text = result[key]['message']
      var myLatLng = {lat: result[key]['coordinates'][1], lng: result[key]['coordinates'][0]};
      
      if (allMarkers.length != 0) {
        for (i=0; i < allMarkers.length; i++){
          var existingMarker = allMarkers[i];
          var lat = existingMarker.getPosition().lat();
          var lng = existingMarker.getPosition().lng();
          if (myLatLng['lat'] == lat && myLatLng['lng'] == lng) {
            var newLat = myLatLng['lat'] + .00005;
            var newLng = myLatLng['lng'] + .00005;
            myLatLng = new google.maps.LatLng(newLat,newLng);
          }
        }
      }
      var marker = new google.maps.Marker({map: map,
                                           position: myLatLng,
                                           title: text.toString(),
                                           category: 0
                                          });
      allMarkers.push(marker)

      var infowindow = new google.maps.InfoWindow({
          content: text.toString()
      });

      $('#placescol').prepend('<button>' + text.toString() + "</button>")

      google.maps.event.addListener(marker,'click', (function(marker,text,infowindow){ 
        return function() {
          infowindow.setContent(text);
          infowindow.open(map,marker);
      };

      })(marker,text.toString(),infowindow)); 
    }

  var bounds = new google.maps.LatLngBounds();
  for (var i = 0; i < allMarkers.length; i++) {
    bounds.extend(allMarkers[i].getPosition());
}
  map.setOptions({ minZoom: 13, maxZoom: 20});
  map.fitBounds(bounds);
}


function getLocations(){
    var address = $('#address').val();
    var street = $('#street').val();
    var side =$('#side').val();
    var address_info = {"address": address,
                       "street": street,
                       "side":side
    };
    $.get('/nearby_cleanings.json', address_info, showLocations);
}

$('#locationsbtn').on('click', getLocations);