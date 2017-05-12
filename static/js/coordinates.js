function displayResults(result){
    console.log(result);
}

function getCordinates(){
    navigator.geolocation.getCurrentPosition(function(position) {
          var pos = {
            'lat': position.coords.latitude,
            'lng': position.coords.longitude
          };
          console.log(pos['lat']);
    $.get('/current_location', pos, displayResults);
})

}


$('#currentlocation').on('click', getCordinates)