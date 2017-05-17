function showLocations(result){
    $('#locations').html(result)
}

function getLocations(){
    var address = $('#address').val();
    var street = $('#street').val();
    var address_info = {"address": address,
                       "street": street
    }
    $.get('/nearby_cleanings', address_info, showLocations)
}

$('#locationsbtn').on('click', getLocations);