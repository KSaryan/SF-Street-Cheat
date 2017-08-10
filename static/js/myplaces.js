$('#Recentbtn').on('click', function(){$('#Recentform').removeClass();$('#Recentbtn').addClass('hidden');})
$('#Workbtn').on('click', function(){$('#Workform').removeClass();$('#Workbtn').addClass('hidden');})
$('#Homebtn').on('click', function(){$('#Homeform').removeClass();$('#Homebtn').addClass('hidden');})


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

$('#Homeaddress').change(function(){streetSide('#Homesidediv', '#Homeaddress', '#Homestreet', '.Home');});
$('#Homestreet').change(function(){streetSide('#Homesidediv', '#Homeaddress', '#Homestreet', '.Home');});

$('#Workaddress').change(function(){streetSide('#Worksidediv', '#Workaddress', '#Workstreet', '.Work');});
$('#Workstreet').change(function(){streetSide('#Worksidediv', '#Workaddress', '#Workstreet', '.Work');});

$('#Recentaddress').change(function(){streetSide('#Recentsidediv', '#Recentaddress', '#Recentstreet', '.Recent');});
$('#Recentstreet').change(function(){streetSide('#Recentsidediv', '#Recentaddress', '#Recentstreet', '.Recent');});
