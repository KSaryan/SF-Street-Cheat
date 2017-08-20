function findingSides(result){
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

        
function streetSide(){
     var addressInputs = {
        "address": $('#address').val(),
        "street": $('#street').val(),
    };
    $.get('/find_sides.json', addressInputs, findingSides); 
}

$('#address').change(streetSide);
$('#street').change(streetSide);


function displayLocationResults(result){
    $("#address").val(result["address"]);
    $("#street").val(result["street"]);
    findingSides(result);
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