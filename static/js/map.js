var map, infoWindow;
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: -34.397, lng: 150.644},
    zoom: 17,
    zoomControl: false
  });
  infoWindow = new google.maps.InfoWindow;
  console.log(infoWindow);

  // Try HTML5 geolocation.
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };

      infoWindow.setPosition(pos);
      infoWindow.setContent('Parking');
      infoWindow.open(map);
      map.setCenter(pos);
    }, function(posError) {
      console.log(posError);
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

  function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
  infoWindow.open(map);
}

function showLocations(result){
    debugger;
    // $('#locations').html(result["1"]['loc_id']);
    // var map = new google.maps.Map(document.getElementById('map'));
    // var map =  ????
    for (key in result){
        console.log(result[key]['loc_id'])
        var text = result[key]['message']
        var myLatLng = {lat: result[key]['coordinates'][1], lng: result[key]['coordinates'][0]};
        console.log(myLatLng)
        var marker = new google.maps.Marker({
          position: myLatLng,
          map: map,
          title: text.toString()
      });
    }
}

function getLocations(){
    var address = $('#address').val();
    var street = $('#street').val();
    var side =$('#side').val();
    var address_info = {"address": address,
                       "street": street,
                       "side":side
    };
    $.get('/nearby_cleanings', address_info, showLocations);
}

$('#locationsbtn').on('click', getLocations);
