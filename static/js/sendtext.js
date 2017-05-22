function completed(result){
    if (result["info_message"] == "True"){
        number ='(' + result["number"].slice(0, 3) + ')' + result["number"].slice(3, 6) + '-' + result["number"].slice(6,)
        alert("Message will be sent to " + number);
    }else{
        $(location).attr('href', '/user_info')
    }
}

function sendText(evt){
    evt.preventDefault();
    var cleaningtime = $('#cleaningtime').val();
    var message = {
        "cleaningtime": cleaningtime
    };

    $.post('/send_text.json', message, completed);
}


$('#gettext').on('submit', sendText);