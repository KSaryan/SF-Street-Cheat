// function showLocations(result){
//     debugger;
//     // $('#locations').html(result["1"]['loc_id']);
//     // var map = new google.maps.Map(document.getElementById('map'));
//     var map =  ????
//     for (key in result){
//         console.log(result[key]['loc_id'])
//         var text = result[key]['loc_id']
//         var myLatLng = {lat: result[key]['coordinates'][1], lng: result[key]['coordinates'][1]};
//         console.log(myLatLng)
//         var marker = new google.maps.Marker({
//         position: myLatLng,
//         map: map,
//         title: str(text)
//       });
//     }
// }

// function getLocations(){
//     var address = $('#address').val();
//     var street = $('#street').val();
//     var side =$('#side').val();
//     var address_info = {"address": address,
//                        "street": street,
//                        "side":side
//     };
//     $.get('/nearby_cleanings', address_info, showLocations);
// }

// $('#locationsbtn').on('click', getLocations);