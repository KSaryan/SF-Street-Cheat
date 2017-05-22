// hiding gettest div
$('#gettext').toggle()


function displayStreetCleaningResults(result){
    // displays street cleaningtime and get text button 

    if(result["info_message"] == "today" || result["info_message"] == "another day"){
        $('#cleaningtime').val(result["cleaning_time"]);
        $('#gettext').fadeIn();
    }
        
    $('#timeleft').html(result["message"]);
    var latlng = {'lat': result['geolocation']['lat'], 
                  'lng': result['geolocation']['lng']}
    map.setCenter(latlng);
    infoWindow.setPosition(latlng);
}

function submitAddress(evt){
    evt.preventDefault();

    var addressInputs = {
        "address": $('#address').val(),
        "street": $('#street').val(),
        "side": $('#side').val()
    };
    $.get('/street_cleaning.json', addressInputs, displayStreetCleaningResults);
}

$('#addressbtn').on('click', submitAddress)


function findingSides(list_of_sides){
    $('#sidediv').fadeOut();
    $('.sides').addClass('hidden');
    for (var i=0; i< list_of_sides.length; i++){
        var sideId = '#' + list_of_sides[i];
        $(sideId).removeClass('hidden'); 
    }
    $('#sidediv').fadeIn();
}


function displaySides(result){
    findingSides(result["sides"]);
}
        
function streetSide(){
     var addressInputs = {
        "address": $('#address').val(),
        "street": $('#street').val(),
    };
    $.get('/find_sides.json', addressInputs, displaySides); 
}

$('#addres').change(streetSide);
$('#street').change(streetSide);


function displayLocationResults(result){
    $("#address").val(result["address"]);
    $("#street").val(result["street"]);
    findingSides(result["sides"]);
}

function getCordinates(){
    navigator.geolocation.getCurrentPosition(function(position) {
          var pos = {
            'lat': position.coords.latitude,
            'lng': position.coords.longitude
          };
    $.get('/current_location.json', pos, displayLocationResults);
})
}

$('#currentlocation').on('click', getCordinates)