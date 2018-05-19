$(document).ready(function() {
    $('#repo_search').click(function() {
        $.ajax({
            url: '/test',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                text: 'sosi'
            }),
            success: function (response) {
                alert(response);
                console.log(response);
            },
            error: function () {
                alert('error');
            }
        });
    });
    
    $('#repo_upload').click(function() {
        alert('click');
    });
});