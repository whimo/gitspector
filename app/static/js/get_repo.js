$(document).ready(function() {
    $('#repo_search').on('submit', function(ev) {
        ev.preventDefault();
        
        $.ajax({
            url: '/test',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                url: $('#repo_search input').val()
            }),
            timeout: 1000
        }).done(function (data){
            console.log(data);
        }).fail(function (jqXHR, status) {
            console.log(status);
        });
    });
    
    $('#repo_upload').click(function() {
        alert('click');
    });
});