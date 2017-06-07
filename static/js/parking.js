
function changeView(evt){
    evt.preventDefault();
    $('#section1').toggle('slide');
    $('#section2').toggle('slide');
    $('#section2').removeClass('hidden');
    $('#title').html('<h1>Choose a Street Side</h1>')
}
$('#usethisaddress').on('click', changeView);

function changeView2(){
    $('#section2').toggle('slide');
    $('#section3').toggle('slide');
    $('#section3').removeClass('hidden');
    $('#title').html('<h1>Street Cleaning Info</h1>')
}
$('#addressbtn').on('click', changeView2);


function changeView3(){
    $('#section3').toggle('slide');
    $('#section4').toggle('slide');
    $('#section4').removeClass('hidden');
    $('#title').html('<h1>Explore Other Options</h1>')
}
$('#locationsbtn').on('click', changeView3);


function changeMarkers(num){
    console.log("Here");
    for (var i = 0; i<allMarkers.length; i++){
        if (allMarkers[i].num == num){
            allMarkers[i].setIcon('/static/img/green_MarkerP.png');
        }else{
            allMarkers[i].setIcon('/static/img/red_MarkerP.png');
        }
    }
}

$(document).on('click','.placebtnclass', function(){changeMarkers(this.id);});

function changeMap(result){
    var latlng = {'lat': result['lat'], 
                  'lng': result['lng']}
    map.setCenter(latlng);
    infoWindow.setPosition(latlng);
}

function getGeoForMap(){
    var data = {
        "address": $('#address').val(),
        "street": $("#street").val()
    }

    $.get('/geo_for_map', data, changeMap)
}
$('#usethisaddress').on('click', getGeoForMap)
