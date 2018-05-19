$(document).ready(function(){
    $('#message_div').on('click', '.message .close', function (ev){
        let message = $(ev.currentTarget).closest('.message');
        message.fadeOut(400, function() {message.remove();});
    });
});