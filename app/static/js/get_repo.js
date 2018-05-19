$(document).ready(function() {
    const regex = /^(https?:\/\/)?((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))(\:\d+)?(\/[-a-z\d%_.~+]*)*(\?[;&a-z\d%_.~+=-]*)?(\#[-a-z\d_]*)?$/i;
    const pattern = new RegExp(regex);
    
    function validURL(str) {
        return pattern.test(str);
    }
    
    function show_message(type, header, body)
    {
        const message = $('<div class="ui ' + type + ' message"><i class="close icon"></i><div class="header">' + header +'</div><p>' + body + '</p></div>').hide();
        message.fadeIn().appendTo('#message_div');
    }
    
    function handleError(error) {
        switch (error){
            case 'timeout':
                show_message('negative', 'Error', 'Timed out on your request. Please check your Internet connection.');
                break;
            case 'not-url':
                show_message('negative', 'Error', 'Please specify a valid git repository URL.');
                break;
            default:
                show_message('negative', 'Error', 'Something went wrong. Please try again later.');
                break;
        }
    }
    
    $('#repo_search').on('submit', function(ev) {
        ev.preventDefault();
        
        let url = $('#repo_search input').val();
        if (!validURL(url)) {
            handleError('not-url');
            return;
        }
        
        $('.ui .dimmer').dimmer('show');
        
        $.ajax({
            url: '/repo_url',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                url: url
            }),
            timeout: 5000,
        }).done(function (data){            
            $('#content_div').empty();
            // Insert new data
        }).fail(function (jqXHR, status) {
            handleError(status);
        }).always(function() {
            $('.ui .dimmer').dimmer('hide');
        });
    });
    
    $('#repo_upload').click(function() {
        alert('click');
    });
});