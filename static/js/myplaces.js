function findingSides(result, sideDiv, aClass){
    var listOfSides = result["sides"];
    $(sideDiv).fadeOut();
    $('.sides').addClass('hidden');
 
    for (var i=0; i< listOfSides.length; i++){
        var sideId = '#' + listOfSides[i] + aClass;
        $(sideId).removeClass('hidden'); 
    }
    $(sideDiv).fadeIn();
}
      
function streetSide(sideDiv, address, street, aClass){
    var addressInputs = {
        "address": $(address).val(),
        "street": $(street).val(),
    };
    $.get('/find_sides.json', addressInputs, function(result){findingSides(result, sideDiv, aClass);}); 
}
 
 
function setListeners(result){
    var favePlaces = result['fave_places']
    console.log(favePlaces)
    for (var place of favePlaces){
        place = place[0]
        $('#'+place+'btn').on('click', function(){$('#'+place+'form').removeClass();$('#'+place+'btn').addClass('hidden');})
        $('#'+place+'address').change(function(){streetSide('#'+place+'sidediv', '#'+place+'address', '#'+place+'street', '.'+place);});
        $('#'+place+'street').change(function(){streetSide('#'+place+'sidediv', '#'+place+'address', '#'+place+'street', '.'+place);});
    }
}
 
 
$(document).ready(function(){
    $.get('/get_fave_locs.json', setListeners);
});