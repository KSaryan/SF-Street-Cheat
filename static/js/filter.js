
$('#filterbtn').on('click', function(){$('#filterform').removeClass('hidden'); $('#filterbtn').hide();});
$('#locationsbtn').on('click', function(){$('#filterbtn').removeClass('hidden');})

function categorizeMarkers(){
    // give categories to all existing markers
    for(i=0; i<allMarkers.length; i++){
        $('#' + (i).toString()).show()
        allMarkers[i].setMap(map);
        text = allMarkers[i]['title'];
        if (text.includes("hours")){
            var category = 2;
            if (text.includes(" 0 ") || text.includes(" 1 ")){
            var category = 1;
            }
        }else if (text.includes("tomorrow")) {
                var category = 2;
        }else if (text.includes("days")){
            if (text.includes(" 1 ")){
                var category = 3;
            }else if  (text.includes(" 2 ") || text.includes(" 3 ") || text.includes(" 4 ") || text.includes(" 5 ") || text.includes(" 6 ")){
                var category = 4;
            }
        }
        allMarkers[i]['category'] = category
    }
}

function removeSomeMarkers(num){
    categorizeMarkers();
    // Remove markers and correspondin buttons
    for(i=1; i<=num; i++){
        for(j=0; j<allMarkers.length; j++){
            if (parseInt(allMarkers[j]['category']) == i){
                allMarkers[j].setMap(null);
                var id = allMarkers[j].num;
                $('#' + (id).toString()).hide();
    }
        }
}
}

function getRidOfMarkers(evt){
    evt.preventDefault();
    var num = parseInt($('#filteroptions').val());
    removeSomeMarkers(num);

}

$('#filterform').on('submit', getRidOfMarkers);