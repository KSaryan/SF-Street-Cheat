function displayResults(result){
    $('#timeleft').html(result)
}

function submitAddress(evt){
    evt.preventDefault();

    var addressInputs = {
        "address": $('#address').val(),
        "street": $('#street').val(),
        "side": $('#side').val()
    };

    $.get('/street_cleaning', addressInputs, displayResults);
}


$('#address-btn').on('click', submitAddress)


// function displaySides(result){
//     if (result){
//         $('#sidebtn').html(hello)
               
// function streetside(){
//     alert("hello")
//     var addressInputs = {
//         "address": $('#address').val(),
//         "street": $('#street').val()
//     }

//     $.get('/side_decider', addressInputs, displaySides)
// }

// $('#street').on('click', streetside)