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
    
    function show_data(json)
    {
        let html = `
            <div class="ui centered grid">
                <div class="row">
                    <h3>Contributors data</h3>
                </div>
            </div>
            <div class="ui grid">
                <div class="row">
                    <div class="ui basic segment" style="width: 100%;">
                        <div class="ui fluid search selection dropdown">
                            <input name="contributor" type="hidden">
                            <i class="dropdown icon"></i>
                            <div class="default text">Choose a contributor</div>
                            <div class="menu">
                                <div class="item">Qwertygid</div>
                                <div class="item">syn</div>
                                <div class="item">whimo</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="centered row">
                    <canvas id="contributor_canvas" width="500" height="500"></canvas>
                </div>
            </div>
            `
        $(html).appendTo('#content_div').fadeIn();
        $('.ui.dropdown').dropdown({
            onChange: function (value, text, $selectedItem){
                let ctx = $('#contributor_canvas')[0].getContext('2d');
                let chart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['New Work', 'Refactoring', 'Helping others', 'Code Churn'],
                        datasets: [{
                            label: text,
                            data: [41, 9, 17, 33],
                            backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)', 'rgb(255, 0, 255)']
                        }]
                    },
                    options: {
                        responsive: false
                    }
                });
            }
        });
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
            show_data('');
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