var allMarkers = []
var allNums = []

function removeMarkers(){
  for(i=0; i<allMarkers.length; i++){
      allMarkers[i].setMap(null);
  }
  allMarkers=[];
  $('#' + (i).toString()).hide()
  allNums = []
}

function adjustMap(){
  var bounds = new google.maps.LatLngBounds();
  for (var i = 0; i < allMarkers.length; i++) {
    bounds.extend(allMarkers[i].getPosition());
  }
  // map.setOptions({ minZoom: 13, maxZoom: 20});
  map.fitBounds(bounds);
}

function createButton(num, text){
  $('#placesdiv').prepend('<button class="btn-default markerbtn placebtnclass" id =' + num + ' >' + text + "</button><br>"); 
  allNums.push(num);
}

function addInfoWindow(text, marker){
  var infowindow = new google.maps.InfoWindow({
          content: text
      });

  google.maps.event.addListener(marker,'click', (function(marker,text,infowindow){ 
    return function() {
      infowindow.setContent(text);
      infowindow.open(map,marker);
  };

  })(marker,text,infowindow)); 
}

function showLocations(result){
  removeMarkers();
  var latLngs = new Set([]);
  for (key in result){
      var text = (result[key]['message']).toString();
      var num = (result[key]['num']).toString();
      var newLat = result[key]['coordinates'][1];
      var newLng = result[key]['coordinates'][0];
      if (latLngs.has((newLat, newLng))){
        var newLat = newLat + .00005;
        var newLng = newLng + .00005;
      }
      myLatLng = new google.maps.LatLng(newLat,newLng);
      latLngs.add((newLat, newLng));
      
      var marker = new google.maps.Marker({map: map,
                                           animation: google.maps.Animation.DROP,
                                           position: myLatLng,
                                           title: text.toString(),
                                           category: 0,
                                           num: num,
                                           icon: '/static/img/red_MarkerP.png'
                                          });

      allMarkers.push(marker)

      addInfoWindow(text, marker)

      createButton(num, text);
  }
  adjustMap();
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