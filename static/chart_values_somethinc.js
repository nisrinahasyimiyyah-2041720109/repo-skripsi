$(document).ready( () => {

    let color = ['#7ec2e7', '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de', '#f64f2c', '#117ea6', '#82e4de'];

    reqBarData = () => {
        $.ajax({
            url: '/api/count/labels/somethinc',
            type: 'POST',
            dataType: 'JSON',
            success: (data) => {
                getTop10Words(data.index, data.values, '#pieChart');
                $('#panjangDF').text(data.length_df);
            },
        });
    }

    reqPieData = () => {
        $.ajax({
            url: '/api/count/words/somethinc',
            type: 'POST',
            dataType: 'JSON',
            success: (data) => {
                console.log(data);
                chartFunc(data.index, data.values);
                getWordsLabel(data.positive_words.value, data.positive_words.label, '#positiveWordChart');
                getWordsLabel(data.neutral_words.value, data.neutral_words.label, '#neutralWordChart');
                getWordsLabel(data.negative_words.value, data.negative_words.label, '#negativeWordChart');
                console.log(data.positive_words);
            },
        });
    }

    getWordsLabel = (value, label, id) => {
        let chart = new Chart($(id)[0].getContext('2d'), {
            type: 'horizontalBar',
            data: {
                labels: label,
                datasets: [{
                    data: value,
                    backgroundColor : color,
                }]
            },
            options: {
                legend: { 
                    display: false 
                },
                maintainAspectRatio : false,
                responsive : true,
            }
        });
    }

    getTop10Words = (label, value, id) => {
        let chart = new Chart($(id)[0].getContext('2d'), {
            type: 'pie',
            data: {
                labels: label,
                datasets: [{
                    data: value,
                    backgroundColor : color,
                }]
            },
            options: {
                legend: { 
                    display: true 
                },
                maintainAspectRatio : false,
                responsive : true,
            }
        });
    }

    getAllWords = () => {
        $.ajax({
            url: '/api/info/somethinc',
            type: 'GET',
            dataType: 'JSON',
            success: (resp) => {
                $('#allWords').text(resp.all_words);
                $('#getStopwords').text(resp.total_stopwords);
                $('#normalizationData').text(resp.total_normalization);
            }
        });
    }

    chartFunc = (label, value) => {
        let myBarChart = new Chart($('#stackedBarChart')[0].getContext('2d'), {
            type: 'bar',
            data: {
                labels: label,
                datasets: [{
                    data: value,
                    backgroundColor : color,
                }]
            },
            options: {
                legend: { 
                    display: false 
                },
                maintainAspectRatio : false,
                responsive : true,
            }
        });
    }

    $('#btn_upload_dataset_somethinc').on('click', () => {
        if($('#form_upload_dataset_somethinc')[0].files.length === 0){
            Swal.fire({
                title: 'File Not Found',
                icon: 'error',
                showCloseButton: true,
                showConfirmButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
            });
        } else {
            form_data = new FormData($('#upload_file_dataset_somethinc')[0]);
            $.ajax({
                url: '/api/file/dataset/somethinc',
                type: 'POST',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
            }).done( (resp) => {
                Swal.fire({
                    title: resp.result,
                    icon: 'success',
                    showConfirmButton: false,
                    showCloseButton: true,
                    allowEscapeKey: false,
                    allowOutsideClick: false,
                });
            });
        }
    });

    $('#btn_preprocess_somethinc').on('click', () => {
        $.ajax({
            url: '/api/preprocess/somethinc',
            type: 'POST',
            contentType: false,
            cache: false,
            processData: false,
        }).done( (resp) => {
            Swal.close();
            Swal.fire({
                title: resp.result,
                icon: 'success',
                showCloseButton: true,
                showConfirmButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
                html: `<center><table class="table table-bordered text-center"><thead><tr><th>`+resp.index[0]+`</th><th>`+resp.index[1]+`</th><th>`+resp.index[2]+`</th></tr></thead><tbody><tr><td>`+((resp.values[0]/resp.length_df)*100).toFixed(2)+`%</td><td>`+((resp.values[1]/resp.length_df)*100).toFixed(2)+`%</td><td>`+((resp.values[2]/resp.length_df)*100).toFixed(2)+`%</td></tr></tbody></table></center><br/>`+`<a id="btn_download" href="/api/preprocess/file/download" class="btn btn-success" target="blank">Download File</a>`,
            });
        });
    });

    $('#btn_sentistrength_somethinc').on('click', () => {
        $.ajax({
            url: '/api/sentistrength/somethinc',
            type: 'POST',
            contentType: false,
            cache: false,
            processData: false,
        }).done( (resp) => {
            Swal.close();
            Swal.fire({
                title: resp.result,
                icon: 'success',
                showCloseButton: true,
                showConfirmButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
                html: `<center><table class="table table-bordered text-center"><thead><tr><th>`+resp.index[0]+`</th><th>`+resp.index[1]+`</th><th>`+resp.index[2]+`</th></tr></thead><tbody><tr><td>`+((resp.values[0]/resp.length_df)*100).toFixed(2)+`%</td><td>`+((resp.values[1]/resp.length_df)*100).toFixed(2)+`%</td><td>`+((resp.values[2]/resp.length_df)*100).toFixed(2)+`%</td></tr></tbody></table></center><br/>`+`<a id="btn_download" href="/api/sentistrength/file/download" class="btn btn-success" target="blank">Download File</a>`,
            });
        });
    });

    $('#reloadData').click( () => {
        reqBarData();
        reqPieData();
        getAllWords();
    });

    getAllWords();
    reqBarData();
    reqPieData();
});