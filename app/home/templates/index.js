$(document).ready(load_db());
const btn_element = document.querySelector("#action_btn");

console.log('curr_user_name')

function cancel_job(id) {

    // prevent anonimous users from changing database
    if (curr_user_name == 'Guest') {
        alert('users must be registered in order to cancel job')
        return;
    }

    let text = "Cancel Job id " + String(id) + " ?\nEither OK or Cancel.";
    if (confirm(text) == true) {

        const request = new XMLHttpRequest();
        const formData = new FormData();
        console.log(`canceling job: ${id} by user ${curr_user_name}`)

        request.onreadystatechange = () => {
            if (request.readyState === 4 && request.status === 200) {
                console.log(request.responseText);
            }
        };

        API_ENDPOINT = `/web/job/${id}/cancel/`

        // send http request to trigger inference 
        request.open("POST", API_ENDPOINT, true);
        formData.append("user_name", curr_user_name);
        request.send(formData);

        location.reload()
    }
}


function download_job(id) {

    var base_url = window.location.origin;
    console.log(`download job: ${id} by user ${curr_user_name}`);
    window.location.href = `${base_url}/web/job/${id}/download`;
}


function load_db() {
    jQuery(function($) {

        $('#data_table').DataTable({
            ajax: '/web/data',
            serverSide: true,
            columns: [
                { data: 'id' },
                { data: 'usr_email' },
                { data: 'project' },
                { data: 'status', orderable: false },
                { data: 'created_date' },
                { data: 'confidence', orderable: false },
                { data: 'duration', orderable: false },
            ],
            order: [
                [4, 'desc']
            ],
            pageLength: 4,
            responsive: true,
            scrollCollapse: true,
            retrieve: true,
        });
    });
}


var table = $('#data_table').DataTable({
    ajax: '/web/data',
    serverSide: true,
    columns: [
        { data: 'id' },
        { data: 'usr_email' },
        { data: 'project' },
        { data: 'status', orderable: false },
        { data: 'created_date' },
        { data: 'confidence', orderable: false },
        { data: 'duration', orderable: false },
        {
            "data": 'id',
            "render": function(id, type, row, meta) {
                log_link = `<a href="web/job/${id}/log/console">view log</a>`
                return log_link;
            }
        },
        {
            // "data": { 'job_id': 'id', 'job_status': 'status' },
            "data": { 'job_id': 'id', 'job_status': 'status' },
            "render": function(data, type, row, meta) {
                job_id = data['id']
                job_status = data['status']
                if (job_status == 'in progress' || job_status == 'pending') {
                    button = `<button id="action_btn" 
                    style="background-color:tomato; 
                    font-weight:bold; 
                    border: none;
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;" 
                    onClick="cancel_job(${job_id})">Cancel</button>`
                    return button
                } else if (job_status == 'completed') {
                    button = `<button id="action_btn" 
                    style="background-color: #04AA6D; 
                    font-weight:bold; 
                    border: none;
                    border-radius: 12px;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;"
                    onClick="download_job(${job_id})">Download</button>`
                    return button

                } else {
                    return `<label id="place-holder-label" style="display: none;"></label>`;
                }
            }
        },

    ],
    order: [
        [4, 'desc']
    ],
    retrieve: true,
    pageLength: 4,
    responsive: true,
    scrollCollapse: true,
});

setInterval(function() {
    table.p
    table.ajax.reload(null, false);
}, 3500);



$(document).ready(function() {
    $.ajax({
        url: "/web/data",
        method: "GET",
        success: function(records) {
            console.log(records.data);


            var project_count = {};
            var project_count_completed = {};
            var project_count_failed_or_canceled = {};

            for (var i in project_name_list) {
                project_count_completed[project_name_list[i]] = 0
                project_count_failed_or_canceled[project_name_list[i]] = 0
            }

            for (var i in records.data) {
                record = records.data[i]
                if (record['status'] == 'completed') {
                    project_count_completed[record['project']] += 1
                } else if (record['status'] == 'failed') {
                    project_count_failed_or_canceled[record['project']] += 1
                } else if (record['status'] == 'canceled') {
                    project_count_failed_or_canceled[record['project']] += 1
                }


            }

            var project_label_list = [];
            var project_occurence_list_completed = [];
            var project_occurence_list_failed_or_canceled = [];


            for (const [key, value] of Object.entries(project_count_completed)) {
                project_label_list.push(key);
                project_occurence_list_completed.push(value);
            }
            for (const [key, value] of Object.entries(project_count_failed_or_canceled)) {
                project_occurence_list_failed_or_canceled.push(value);
            }


            var myData = {
                labels: project_label_list,
                datasets: [{
                        label: 'completed',
                        backgroundColor: '#18DB5E', //'#28C962',
                        fill: false,
                        borderColor: 'black',
                        data: project_occurence_list_completed,
                    },

                    {
                        label: 'aborted',
                        backgroundColor: '#FF3333',
                        fill: false,
                        borderColor: 'black',
                        data: project_occurence_list_failed_or_canceled,
                    }
                ]
            };


            var myoption = {
                title: {
                    display: true,
                    text: 'Job Request'
                },
                tooltips: {
                    mode: 'index',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        stacked: true,
                        displayStackLabel: true
                    }],
                    yAxes: [{
                        display: true,
                        stacked: true
                    }],
                },
                legend: {
                    position: 'bottom'
                },
            };
            // Code to draw Chart
            var ctx = document.getElementById('myCanvas').getContext('2d');
            var myChart = new Chart(ctx, {
                type: 'horizontalBar', // Define chart type
                data: myData, // Chart data
                options: myoption // Chart Options [This is optional paramenter use to add some extra things in the chart].
            });

        },
        error: function(data) {
            console.log(data);
        }
    });
});