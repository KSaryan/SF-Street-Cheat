$('#gettext').toggle();
$('#locationsbtn').toggle();
$('#logintextbtn').toggle();


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

    var addressInputs = $( this ).serialize() 

    $.get('/street_cleaning.json', addressInputs, displayStreetCleaningResults);
}

$('#addressinfo').on('submit', submitAddress)
