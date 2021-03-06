
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


// Turns markers green when their button is clicked on
function changeMarkers(num){
    for (var i = 0; i<allMarkers.length; i++){
        if (allMarkers[i].num == num){
            allMarkers[i].setIcon('/static/img/green_MarkerP.png');
        }else{
            allMarkers[i].setIcon('/static/img/red_MarkerP.png');
        }
    }
}

$(document).on('click','.placebtnclass', function(){changeMarkers(this.id);});


// Changes map center when user chooses new location
function changeMap(result){
    var latlng = {'lat': result['lat'], 
                  'lng': result['lng']}
    map.setCenter(latlng);
    infoWindow.setPosition(latlng);
}

function getGeoForMap(){
    var data = $('#'+this.dataset.formId).serialize();

    $.get('/geo_for_map', data, changeMap)
}

$('#usethisaddress').on('click', getGeoForMap)

$('#registerbtn2').on('click', function(){$('#registerform2').removeClass('hidden');});
