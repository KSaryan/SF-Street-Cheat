function completed(result){
    if (result == "True"){
        alert("Message sent");
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

    $.post('/send_text', message, completed);
}


$('#gettext').on('submit', sendText);