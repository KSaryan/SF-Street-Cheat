$('#sidediv').hide()

function changeView(){
    $('#section1').hide('slide', {direction: 'left'}, 1000);
    $('#sidediv').show('slide', {direction: 'left'}, 1000)
}
$('#usethisaddress').on('click', changeView)