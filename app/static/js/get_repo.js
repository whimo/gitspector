$(document).ready(function() {
    const regex = /^(https?:\/\/)?((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))(\:\d+)?(\/[-a-z\d%_.~+]*)*(\?[;&a-z\d%_.~+=-]*)?(\#[-a-z\d_]*)?$/i;
    const pattern = new RegExp(regex);
    
    function validURL(str) {
        return pattern.test(str);
    }
    
    function handleError(error) {
        switch (error){
            case 'timeout':
                console.log('handleError: timeout');
                break;
            case 'not-url':
                console.log('handleError: not-url');
                break;
            default:
                console.log('handleError: default');
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
        
        $.ajax({
            url: '/repo_url',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                url: url
            }),
            timeout: 1000
        }).done(function (data){            
            console.log(data);
        }).fail(function (jqXHR, status) {
            handleError(status);
        });
    });
    
    $('#repo_upload').click(function() {
        alert('click');
    });
});