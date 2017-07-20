$('#gettext').toggle();
$('#locationsbtn').toggle();
$('#logintextbtn').toggle();
// $('#timepanel').toggle();
// $('#towingpanel').toggle();


function displayStreetCleaningResults(result){
    // displays street cleaningtime and get text button 

    if(result["info_message"] == "today" || result["info_message"] == "another day"){
        $('#cleaningtime').val(result["cleaning_time"]);
        $('#gettext').fadeIn();
        $('#locationsbtn').fadeIn();
        $('#logintextbtn').fadeIn();
    }
    if ((result["towing"]).length < 1){
        var towmsg = "No towing coming up at this location.";
    }else{
        var towmsg = result["towing"];
    }
    var towingmsg 
    $('#timeleft').html('<img id="carImg" src="/static/img/041-car.png" />' + result["message"]);
    $('#towingdiv').html('<img id="towImg" src="/static/img/tow-truck.png" />' + towmsg);
    $('#towImg')[0].style.width = '60px';
    // var latlng = {'lat': result['geolocation']['lat'], 
    //               'lng': result['geolocation']['lng']}
    // map.setCenter(latlng);
    // infoWindow.setPosition(latlng);
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


function findingSides2(result){
    // $('#sidediv').fadeOut();
    $('.sides').addClass('hidden');
    if (result != "no sides"){
        var listOfSides = result["sides"];
        for (var i=0; i< listOfSides.length; i++){
            var sideId = '#' + listOfSides[i];
            $(sideId).removeClass('hidden'); 
        }
    }
    // $('#sidediv').fadeIn();
}

        
function streetSide2(){
     var addressInputs = {
        "address": $('#address').val(),
        "street": $('#street').val(),
    };
    $.get('/find_sides.json', addressInputs, findingSides2); 
}

$('#addres').change(streetSide2);
$('#street').change(streetSide2);


function displayLocationResults(result){
    $("#address").val(result["address"]);
    $("#street").val(result["street"]);
    findingSides2(result);
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

$(document).ready(getCordinates)