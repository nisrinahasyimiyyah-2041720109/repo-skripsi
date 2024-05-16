$(document).ready( () => {

    let color = ['#7ec2e7', '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de', '#f64f2c', '#117ea6', '#82e4de'];

    reqBarData = () => {
        $.ajax({
            url: '/api/count/labels/pred',
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
            url: '/api/count/words/pred',
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
        // Mengubah label sesuai dengan kebutuhan
        const updatedLabels = label.map(lbl => {
            if (lbl === 0) {
                return "Negatif";
            } else if (lbl === 1) {
                return "Netral";
            } else if (lbl === 2) {
                return "Positif";
            }
        });
    
        let chart = new Chart($(id)[0].getContext('2d'), {
            type: 'pie',
            data: {
                labels: updatedLabels, // Menggunakan label yang sudah diperbarui
                datasets: [{
                    data: value,
                    backgroundColor: [
                        '#00a65a', // Warna untuk label "Positif"
                        '#f56954', // Warna untuk label "Negatif"
                        '#7ec2e7', // Warna untuk label "Netral"
                        // Anda dapat menambahkan lebih banyak warna sesuai kebutuhan
                    ],
                }]
            },
            options: {
                legend: { 
                    display: true,
                },
                maintainAspectRatio : false,
                responsive : true,
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

    $('#btn_prediksi_sentimen').on('click', () => {
        $.ajax({
            url: '/api/predict/file',
            type: 'POST',
            contentType: false,
            cache: false,
            processData: false,
        }).done((resp) => {
            // Display success Swal.fire
            Swal.fire({
                title: 'prediksi selesai',
                icon: 'success',
                showConfirmButton: true, // Show confirm button
                showCloseButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
            }).then((result) => {
                if (result.isConfirmed) {
                    // Reload the page after successful upload
                    location.reload(true); // This will force a reload of the page
                }
            });
        });       
    });

    $('#btn_download_prediksi').on('click', () => {
        window.location.href = '/api/predict/file/download';
    });    

    $('#reloadData').click( () => {
        reqBarData();
        reqPieData();
    });

    reqBarData();
    reqPieData();

});