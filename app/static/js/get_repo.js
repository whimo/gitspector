$(document).ready(function() {
    const regex = /^(https?:\/\/)?((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|((\d{1,3}\.){3}\d{1,3}))(\:\d+)?(\/[-a-z\d%_.~+]*)*(\?[;&a-z\d%_.~+=-]*)?(\#[-a-z\d_]*)?$/i;
    const pattern = new RegExp(regex);
    
    function format_date(date) {
        let d = new Date(date);
        let month = '' + (d.getMonth() + 1);
        let day = '' + d.getDate();
        let year = '' + d.getFullYear();
        
        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;
        
        return [year, month, day].join('-');
    }
    
    function validURL(str) {
        return pattern.test(str);
    }
    
    function show_message(type, header, body) {
        const message = $('<div class="ui ' + type + ' message"><i class="close icon"></i><div class="header">' + header +'</div><p>' + body + '</p></div>').hide();
        message.fadeIn().appendTo('#message_div');
    }
    
    function pie_chart_click(chart, ev) {
        let active_points = chart.getElementsAtEvent(ev);
        if (active_points.length > 0) {
            let clicked_index = active_points[0]['_index'];
            let label = chart.data.labels[clicked_index];
            show_modal('New Work', {'New Work': [{hash: '080b288', desc: 'Repo contributions list'}, {hash: '624f480', desc: 'A couple of helper functions '}]});
        }
    }
    
    function show_modal(key, commits_dict) {
        let html = [`
            <div class="ui modal">
                <div class="header">
                    Commits for `, key, `
                </div>
                <div class="scrolling content">
                    <p style="white-space: pre;">`, commits_dict[key].map(function (current) {return current['hash'] + '\t' + current['desc'];}).join('\n'), `</p>
                </div>
                <div class="actions">
                    <div class="ui ok button">OK</div>
                </div>
            </div>
        `].join('');
        
        $('#modal_div').append(html);
        $('.ui.modal').modal({
            onApprove: function() {
                $('.ui.modal').modal('hide');
                $('.ui.modal').remove();
                return true;
            }
        }).modal('show');
    }
    
    function redraw_contributor_canvases(repo_name) {
        let start_date = $('#start_date').calendar('get date');
        let end_date = $('#end_date').calendar('get date');

        let text = $('.ui.dropdown').dropdown('get text');
        
        if (!start_date || start_date === '')
        {
            show_message('negative', 'Error', 'Please specify a valid period start date.');
            return;
        }
        if (!end_date || end_date === '')
        {
            show_message('negative', 'Error', 'Please specify a valid period end date.');
            return;
        }
        if (start_date > end_date)
        {
            show_message('negative', 'Error', 'Please specify a valid period range.');
            return;
        }
        if (!text || text === '')
        {
            show_message('negative', 'Error', 'Please specify a valid contributor.');
            return;
        }
        
        start_date = format_date(start_date);
        end_date = format_date(end_date);
        
        $('.ui .dimmer').dimmer('show');
        
        $.ajax({
            url: '/repos/'+ repo_name +'/stats',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                username: text,
                from_date: start_date,
                to_date: end_date
            }),
            timeout: 90000,
        }).done(function (data){
            if (data['status'] === 'error')
            {
                show_message('negative', 'Error', data['error_text']);
                return;
            }
            
            $('#contributor_canvas').remove();
            $('#contributor_risk_canvas').remove();
            
            $('#canvases_div').append('<canvas id="contributor_canvas" width="500" height="500" style="width: 470px; height: 470px;"></canvas>');
            $('#canvases_div').append('<canvas id="contributor_risk_canvas" width="500" height="500" style="width: 470px; height: 470px;"></canvas>');
            
            let contributor_ctx = $('#contributor_canvas')[0].getContext('2d');
            let contributor_labels = ['New Work', 'Refactoring', 'Helping Others', 'Code Churn'];
            let contributor_chart = new Chart(contributor_ctx, {
                type: 'doughnut',
                data: {
                    labels: contributor_labels,
                    datasets: [{
                        label: text,
                        data: contributor_labels.map(function (current) {
                            return data['commits_by_type'][current].length;
                        }),
                        backgroundColor: ['rgb(0, 204, 204)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)', 'rgb(102, 204, 0)']
                    }]
                },
                options: {
                    responsive: false
                }
            });
            $('#contributor_canvas').click(function (ev){
                pie_chart_click(contributor_chart, ev);
            });
            
            let contributor_risk_ctx = $('#contributor_risk_canvas')[0].getContext('2d');
            let risk_labels = ['High Risk', 'Medium Risk', 'Low Risk'];
            let contributor_risk_chart = new Chart(contributor_risk_ctx, {
                type: 'doughnut',
                data: {
                    labels: risk_labels,
                    datasets: [{
                        label: text,
                        data: risk_labels.map(function (current) {
                            return data['commits_by_risk'][current].length;
                        }),
                        backgroundColor: ['rgb(255, 0, 0)', 'rgb(255, 102, 102)', 'rgb(255, 204, 204)']
                    }]
                },
                options: {
                    responsive: false
                }
            });
            
            $('#contributor_risk_canvas').click(function (ev){
                pie_chart_click(contributor_risk_chart, ev);
            });
        }).fail(function (jqXHR, status, errorThrown) {
            handleError(status);
        }).always(function () {
            $('.ui .dimmer').dimmer('hide');
        });        
    }
    
    function show_data(repo_name) {
        $('.ui .dimmer').dimmer('show');
        
        $.ajax({
            url: '/repos/'+ repo_name + '/contributors',
            type: 'GET',
            dataType: 'json',
            timeout: 90000,
        }).done(function (data){
            if (data['status'] == 'error')
            {
                show_message('negative', 'Error', data['error_text']);
                return;
            }
            
            let html = `
                <div class="ui centered grid">
                    <div class="row">
                        <h3>Contributors data</h3>
                    </div>
                </div>
                
                <div class="ui form row">
                    <div class="two fields">
                        <div class="field">
                            <div id="start_date" class="ui calendar">
                                <div class="ui fluid input left icon">
                                    <i class="calendar icon"></i>
                                    <input type="text" placeholder="Start Date">
                                </div>
                            </div>
                        </div>
                        
                        <div class="field">
                            <div id="end_date" class="ui calendar">
                                <div class="ui fluid input left icon">
                                    <i class="calendar icon"></i>
                                    <input type="text" placeholder="End Date">
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="field">
                        <div class="ui fluid search selection dropdown">
                            <input name="contributor" type="hidden">
                            <i class="dropdown icon"></i>
                            <div class="default text">Choose a contributor</div>
                            <div class="menu">` +
                                data['contributors'].map(function (current) {return '<div class="item">' + current + '</div>'}).join('') +
                            `</div>
                        </div>
                    </div>
                    
                    <button id="apply_filters_button" class="ui basic button">Apply filters</button>
                </div>
                
                <div class="ui centered grid">
                    <div id="canvases_div" class="row"></div>
                </div>
            `
            $(html).appendTo('#content_div').fadeIn();
            
            let d = new Date();
            let strDate = d.getFullYear() + "/" + (d.getMonth()+1) + "/" + d.getDate();
            $('.ui.calendar').calendar({
                type: 'date'
            }).calendar('set date', strDate);
            
            $('.ui.dropdown').dropdown();
            
            $('#apply_filters_button').click(function () {
                redraw_contributor_canvases(repo_name);
            });
        }).fail(function (jqXHR, status, errorThrown) {
            handleError(status);
        }).always(function() {
            $('.ui .dimmer').dimmer('hide');
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
        console.log(url);
        if (!validURL(url)) {
            handleError('not-url');
            return;
        }
        
        $('.ui .dimmer').dimmer('show');
        
        $.ajax({
            url: '/new_repo',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                url: url
            }),
            timeout: 90000,
        }).done(function (data){
            if (data['status'] == 'error')
            {
                show_message('negative', 'Error', data['error_text']);
                return;
            }
            
            $('#content_div').empty();
            
            let repo_name = url.split('/').slice(-1)[0].split('.')[0];
            $('.ui .dimmer').dimmer('hide');
            show_data(repo_name);
        }).fail(function (jqXHR, status, errorThrown) {
            $('.ui .dimmer').dimmer('hide');
            handleError(status);
        });
    });
    
    $('#repo_upload').click(function() {
        alert('click');
    });
});