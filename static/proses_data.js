$(document).ready(() => {
    let currentPage = 1; // Current page
    const rowsPerPage = 10; // Number of rows per page

    reqBarData = () => {
        $.ajax({
            url: '/api/count/data/preprocess',
            type: 'POST',
            dataType: 'JSON',
            success: (data) => {
                $('#panjangDF').text(data.length_df);
                const totalUlasanPreprocess = data.length_df;
                $('#totalUlasanPreprocess').text(`Total Data Ulasan Setelah Preprocessing : ${totalUlasanPreprocess}`); // Update elemen h3
            },
        });
    }

    // Fungsi untuk menampilkan data pada halaman tertentu
    const displayData = (data) => {
        // Calculate the start and end index of data to be displayed for the current page
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = Math.min(startIndex + rowsPerPage, data.length);

        // Clear existing table rows
        $('#DataUlasanPreprocessBody').empty();

        // Counter for numbering rows
        let counter = startIndex + 1;

        // Iterate over each row in the data for the current page and append it to the table
        for (let i = startIndex; i < endIndex; i++) {
            const rowData = data[i];
            $('#DataUlasanPreprocessBody').append(`
                <tr>
                    <td>${counter}</td> <!-- Nomor baris -->
                    <td>${rowData[6]}</td> <!-- Mengakses kolom "text_string_lemma" -->
                    <!-- Anda dapat menambahkan kolom tambahan di sini sesuai kebutuhan -->
                </tr>
            `);

            // Increment the counter
            counter++;
        }
    };

    $('#btn_proses_data').on('click', () => {
        // Function to check if dataset file exists
        function checkDatasetExists() {
            return $.ajax({
                url: '/api/check_dataset', // URL endpoint to check if dataset file exists
                type: 'GET'
            });
        }
    
        checkDatasetExists().done((response) => {
            if (response.exists) {
                // Proceed with preprocessing if dataset exists
                const preprocessingToast = Swal.mixin({
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timerProgressBar: true,
                    onOpen: (toast) => {
                        toast.addEventListener('mouseenter', Swal.stopTimer);
                        toast.addEventListener('mouseleave', Swal.resumeTimer);
                    }
                });
    
                preprocessingToast.fire({
                    icon: 'info',
                    title: 'Preprocessing data...',
                    timer: 0, // Set initial timer to 0
                    didOpen: () => {
                        // Start timer when the toast opens
                        const timerInterval = setInterval(() => {
                            // You can replace this condition with your logic to check if preprocessing is done
                            if (preprocessingIsDone()) {
                                // Clear the interval and close the toast
                                clearInterval(timerInterval);
                                preprocessingToast.close();
                            }
                        }, 1000); // Check every second
                    }
                });
    
                $.ajax({
                    url: '/api/proses/data',
                    type: 'POST',
                    contentType: false,
                    cache: false,
                    processData: false,
                }).done((resp) => {
                    // Close loading popup
                    Swal.close();
    
                    // Display success Swal.fire
                    Swal.fire({
                        title: 'preprocessing selesai',
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
                    // Parse respons JSON menjadi objek JavaScript
                    const parsedResponse = JSON.parse(resp);
    
                    // Simpan data ke local storage setiap kali tampilan data diperbarui
                    localStorage.setItem('preprocessData', JSON.stringify(parsedResponse.data));
                    console.log("Data has been saved to Local Storage:", parsedResponse.data);
    
                    // Tampilkan data
                    displayData(parsedResponse.data);
    
                    // Hitung jumlah halaman yang diperlukan
                    const totalPages = Math.ceil(parsedResponse.data.length / rowsPerPage);
    
                    // Tampilkan informasi paginasi
                    $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);
    
                    // Event handler for Next button
                    $('#nextPageP').on('click', () => {
                        if (currentPage < totalPages) {
                            currentPage++;
                            $('#DataUlasanPreprocessBody').empty();
                            displayData(parsedResponse.data);
                            $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);
                        }
                    });
    
                    // Event handler for Previous button
                    $('#prevPageP').on('click', () => {
                        if (currentPage > 1) {
                            currentPage--;
                            $('#DataUlasanPreprocessBody').empty();
                            displayData(parsedResponse.data);
                            $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);
                        }
                    });
                });
            } else {
                // Display warning if dataset does not exist
                Swal.fire({
                    title: 'Error',
                    html: 'Anda harus <b>mengunggah file dataset</b> terlebih dahulu di <b>menu dataset</b>',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
            }
        });
    });    

    // Cek apakah ada data yang disimpan di local storage
    const storedData = localStorage.getItem('preprocessData');
    if (storedData) {
        const preprocessData = JSON.parse(storedData);

        // Tampilkan data
        displayData(preprocessData);

        // Hitung jumlah halaman yang diperlukan
        const totalPages = Math.ceil(preprocessData.length / rowsPerPage);

        // Tampilkan informasi paginasi
        $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);

        // Event handler for Next button
        $('#nextPageP').on('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                $('#DataUlasanPreprocessBody').empty();
                displayData(preprocessData);
                $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);
            }
        });

        // Event handler for Previous button
        $('#prevPageP').on('click', () => {
            if (currentPage > 1) {
                currentPage--;
                $('#DataUlasanPreprocessBody').empty();
                displayData(preprocessData);
                $('#paginationInfoP').text('Page ' + currentPage + ' of ' + totalPages);
            }
        });
    }

    // Your existing code for reloading data
    $('#reloadData').click(() => {
        reqBarData();
    });

    reqBarData();

});


    // // Event handler for Next button
    // $('#nextPageP').on('click', () => {
    //     // Periksa apakah masih ada halaman berikutnya
    //     if (currentPage < Math.ceil(resp.length / rowsPerPage)) {
    //         currentPage++;
    //         updatePagination();
    //     }
    // });

    // // Event handler for Previous button
    // $('#prevPageP').on('click', () => {
    //     // Periksa apakah masih ada halaman sebelumnya
    //     if (currentPage > 1) {
    //         currentPage--;
    //         updatePagination();
    //     }
    // });

    // // Update pagination when page changes
    // const updatePagination = () => {
    //     $('#paginationInfoP').text('Page ' + currentPage + ' of ' + Math.ceil(resp.length / rowsPerPage));
    //     displayData(resp);
    // };

    // // Function to display data in the table for the current page
    // const displayData = (data) => { 
    //     // Calculate the start and end index of data to be displayed for the current page
    //     const startIndex = (currentPage - 1) * rowsPerPage;
    //     const endIndex = Math.min(startIndex + rowsPerPage, data.length);

    //     // Clear existing table rows
    //     $('#DataUlasanPreprocessBody').empty();

    //     // Iterate over each row in the data for the current page and append it to the table
    //     for (let i = startIndex; i < endIndex; i++) {
    //         $('#DataUlasanPreprocessBody').append(`
    //             <tr>
    //                 <td>${data[i].text_string_lemma}</td>
    //                 <!-- Tambahkan kolom tambahan di sini sesuai dengan struktur data -->
    //             </tr>
    //         `);
    //     }
    // };
// });
