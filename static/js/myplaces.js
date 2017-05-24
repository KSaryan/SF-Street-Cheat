$('#recentbtn').on('click', function(){$('#recentform').removeClass();$('#recentbtn').addClass('hidden');})
$('#workbtn').on('click', function(){$('#workform').removeClass();$('#workbtn').addClass('hidden');})
$('#homebtn').on('click', function(){$('#homeform').removeClass();$('#homebtn').addClass('hidden');})


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

$('#homeaddress').change(function(){streetSide('#homesidediv', '#homeaddress', '#homestreet', '.home');});
$('#homestreet').change(function(){streetSide('#homesidediv', '#homeaddress', '#homestreet', '.home');});

$('#workaddress').change(function(){streetSide('#worksidediv', '#workaddress', '#workstreet', '.work');});
$('#workstreet').change(function(){streetSide('#worksidediv', '#workaddress', '#workstreet', '.work');});

$('#recentaddress').change(function(){streetSide('#recentsidediv', '#recentaddress', '#recentstreet', '.recent');});
$('#recentstreet').change(function(){streetSide('#recentsidediv', '#recentaddress', '#recentstreet', '.recent');});
