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
    
        // Object to map labels to their data values and colors
        let labelDataMap = {
            'Positif': 2,
            'Negatif': 0,
            'Netral': 1
        };

        // Fill the object with actual data values
        updatedLabels.forEach((label, index) => {
            if (labelDataMap.hasOwnProperty(label)) {
                labelDataMap[label] = value[index];
            }
        });

        // Ensure labels and data are ordered as desired
        let orderedLabels = ['Positif', 'Negatif', 'Netral'];
        let orderedData = orderedLabels.map(label => labelDataMap[label]);
        let labelColorMap = {
            'Positif': '#00a65a', // Hijau untuk label "Positif"
            'Negatif': '#f56954', // Merah untuk label "Negatif"
            'Netral': '#7ec2e7'  // Biru untuk label "Netral"
        };
        let orderedColors = orderedLabels.map(label => labelColorMap[label]);

        let chart = new Chart($(id)[0].getContext('2d'), {
            type: 'pie',
            data: {
                labels: orderedLabels,
                datasets: [{
                    data: orderedData,
                    backgroundColor: orderedColors
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
        // Function to check if preprocessed dataset file exists
        function checkPreprocessedDatasetExists() {
            return $.ajax({
                url: '/api/check_preprocessed_dataset', // URL endpoint to check if preprocessed dataset file exists
                type: 'GET'
            });
        }
    
        checkPreprocessedDatasetExists().done((response) => {
            if (response.exists) {
                // Proceed with prediction if preprocessed dataset exists
                $.ajax({
                    url: '/api/predict/file',
                    type: 'POST',
                    contentType: false,
                    cache: false,
                    processData: false,
                }).done((resp) => {
                    // Display success Swal.fire
                    Swal.fire({
                        title: 'Prediksi selesai',
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
            } else {
                // Display warning if preprocessed dataset does not exist
                Swal.fire({
                    title: 'Error',
                    html: 'Anda harus melakukan <b>preprocessing data</b> terlebih dahulu di <b>menu proses data</b>',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
            }
        });
    });
    

    $('#btn_download_prediksi').on('click', () => {
        // Function to check if predicted file exists
        function checkPredictedFileExists() {
            return $.ajax({
                url: '/api/check_predicted_file', // URL endpoint to check if preprocessed dataset file exists
                type: 'GET'
            });
        }

        checkPredictedFileExists().done((response) => {
            if (response.exists) {
                window.location.href = '/api/predict/file/download';
            } else {
                // Display warning if predicted file does not exist
                Swal.fire({
                    title: 'Error',
                    html: 'Anda harus melakukan <b>prediksi</b> terlebih dahulu dengan <b>klik tombol prediksi</b>',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
            }
        }); 
    });    

    $('#reloadData').click( () => {
        reqBarData();
        reqPieData();
    });

    reqBarData();
    reqPieData();

});