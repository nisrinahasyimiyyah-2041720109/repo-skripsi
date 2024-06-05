let currentPage = 1; // Current page
const rowsPerPage = 10; // Number of rows per page

$(document).ready(() => {

    let color = ['#7ec2e7', '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de', '#f64f2c', '#117ea6', '#82e4de'];

    reqBarData = () => {
        $.ajax({
            url: '/api/count/labels/dataset',
            type: 'POST',
            dataType: 'JSON',
            success: (data) => {
                $('#panjangDF').text(data.length_df);
                const totalUlasan = data.length_df;
                $('#totalUlasan').text(`Total Data Ulasan : ${totalUlasan}`); // Update elemen h3
            },
        });
    }
    
    // Function to handle CSV file upload and display data
    const handleCSVUpload = () => {
        if ($('#form_upload_dataset')[0].files.length === 0) {
            Swal.fire({
                title: 'File Tidak Ditemukan',
                icon: 'error',
                showCloseButton: true,
                showConfirmButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
            });
        } else {
            const form_data = new FormData($('#upload_file_dataset')[0]);
            $.ajax({
                url: '/api/file/dataset',
                type: 'POST',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: (resp) => {
                    console.log(resp.result);
                    if (resp.result === 'upload success') {
                        // Display success Swal.fire
                        Swal.fire({
                            title: 'Upload Berhasil',
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

                        console.log("Success callback executed");
                        console.log("CSV Data:", resp.csvData); // Print CSV data to console
                        localStorage.setItem('csvData', JSON.stringify(resp.csvData));
                        console.log("Data has been saved to Local Storage:", resp.csvData);
                        storedData = localStorage.getItem('csvData');
                        console.log("Retrieved data from Local Storage:", storedData);
                        if (storedData) {
                            // Ambil data dari Local Storage
                            csvData = JSON.parse(storedData);
                            // Panggil fungsi untuk menampilkan data di tabel
                            populateTable(csvData);
                        }                                            
                    } else {
                        Swal.fire({
                            title: 'Upload Failed',
                            text: resp.result,
                            icon: 'error',
                            showCloseButton: true,
                            showConfirmButton: false,
                            allowEscapeKey: false,
                            allowOutsideClick: false,
                        });
                    }
                },
                error: (xhr, status, error) => {
                    alert('Error: ' + xhr.responseText);
                }
            });
        }
    };

    // Fungsi untuk menampilkan data pada halaman tertentu
    const displayDataScraping = (data) => {
        // Calculate the start and end index of data to be displayed for the current page
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = Math.min(startIndex + rowsPerPage, data.length);

        // Clear existing table rows
        $('#DataUlasanBody').empty();

        // Counter for numbering rows
        let counter = startIndex + 1;

        // Iterate over each row in the data for the current page and append it to the table
        for (let i = startIndex; i < endIndex; i++) {
            const rowData = data[i];
            $('#DataUlasanBody').append(`
                <tr>
                    <td>${counter}</td> <!-- Nomor baris -->
                    <td>${rowData[0]}</td> <!-- Mengakses kolom "text_string_lemma" -->
                    <!-- Anda dapat menambahkan kolom tambahan di sini sesuai kebutuhan -->
                </tr>
            `);

            // Increment the counter
            counter++;
        }
    };

    const handleScraping = (url) => {
        const scrapingToast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timerProgressBar: true,
            onOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });

        scrapingToast.fire({
            icon: 'info',
            title: 'Scraping data...',
            timer: 0, // Set initial timer to 0
            didOpen: () => {
                // Start timer when the toast opens
                const timerInterval = setInterval(() => {
                    // You can replace this condition with your logic to check if preprocessing is done
                    if (preprocessingIsDone()) {
                        // Clear the interval and close the toast
                        clearInterval(timerInterval);
                        scrapingToast.close();
                    }
                }, 1000); // Check every second
            }
        });

        $.ajax({
            url: '/scrape_data',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ url: url }),
            cache: false,
        }).done((resp) => {
            // Close loading popup
            Swal.close();

            // Display success Swal.fire
            Swal.fire({
                title: 'Scraping Selesai',
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
            // Parse the response
            const scrapedData = JSON.parse(resp);
            console.log("Scraped Data:", scrapedData);

            // Save data to local storage
            localStorage.setItem('scrapedData', JSON.stringify(scrapedData.data));
            console.log("Data has been saved to Local Storage:", scrapedData.data);

            // Tampilkan data
            displayDataScraping(scrapedData.data);

            // Hitung jumlah halaman yang diperlukan
            const totalPages = Math.ceil(scrapedData.data.length / rowsPerPage);

            // Tampilkan informasi paginasi
            $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);

            // Event handler for Next button
            $('#nextPage').on('click', () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    $('#DataUlasanBody').empty();
                    displayData(parsedResponse.data);
                    $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);
                }
            });

            // Event handler for Previous button
            $('#prevPage').on('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    $('#DataUlasanBody').empty();
                    displayData(parsedResponse.data);
                    $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);
                }
            });
        });
    };
    
    
    // Event handler for Scrape data button
    $('#btn_scrape_data').on('click', () => {
        const url = $('#input_url').val(); // Ambil URL dari input
        
        // Regex untuk memvalidasi URL dengan skema http:// atau https:// wajib dan diakhiri dengan /review
        const urlPattern = /^(https?:\/\/)([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/review$/;

        if (url && urlPattern.test(url)) {
            // Check if dataset exists before scraping
            checkDatasetExists((exists) => {
                if (exists) {
                    Swal.fire({
                        title: 'Warning',
                        text: 'Dataset sudah ada. Hapus dataset terlebih dahulu sebelum melakukan scraping data baru.',
                        icon: 'warning',
                        showConfirmButton: true,
                        showCloseButton: true,
                        allowEscapeKey: false,
                        allowOutsideClick: false,
                    });
                } else {
                    handleScraping(url);
                }
            });
        } else {
            Swal.fire({
                title: 'URL tidak valid',
                text: 'Harap masukkan URL Halaman Review Toko di Tokopedia \n ()',
                icon: 'error',
                showCloseButton: true,
                showConfirmButton: false,
                allowEscapeKey: false,
                allowOutsideClick: false,
            });
        }
    });            

    // Cek apakah ada data yang disimpan di local storage
    const storedDataScraping = localStorage.getItem('scrapedData');
    if (storedDataScraping) {
        const scrapedData = JSON.parse(storedDataScraping);

        // Tampilkan data
        displayDataScraping(scrapedData);

        // Hitung jumlah halaman yang diperlukan
        const totalPages = Math.ceil(scrapedData.length / rowsPerPage);

        // Tampilkan informasi paginasi
        $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);

        // Event handler for Next button
        $('#nextPage').on('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                $('#DataUlasanBody').empty();
                displayData(scrapedData);
                $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);
            }
        });

        // Event handler for Previous button
        $('#prevPage').on('click', () => {
            if (currentPage > 1) {
                currentPage--;
                $('#DataUlasanBody').empty();
                displayData(scrapedData);
                $('#paginationInfo').text('Page ' + currentPage + ' of ' + totalPages);
            }
        });
    }

    // Function to display data in the table for the current page
    const displayData = (csvData) => {
        const tbody = $('#DataUlasanBody');
        tbody.empty(); // Clear existing table rows
    
        // Calculate the start and end index of data to be displayed for the current page
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = Math.min(startIndex + rowsPerPage, csvData.length);
    
        // Counter for numbering rows
        let counter = startIndex + 1;
    
        // Iterate over each row in the CSV data for the current page
        for (let i = startIndex; i < endIndex; i++) {
            const row = csvData[i];
            const tr = $('<tr>');
    
            // Create a new table data cell for the number and append it to the row
            const numberCell = $('<td>').text(counter);
            tr.append(numberCell);
    
            // Iterate over each column in the row
            row.forEach(cell => {
                // Create a new table data cell and append it to the row
                const td = $('<td>').text(cell);
                tr.append(td);
            });
    
            // Append the row to the table body
            tbody.append(tr);
    
            // Increment the counter
            counter++;
        }
    };    

    // Function to populate table with CSV data
    const populateTable = (csvData) => {
        console.log("populateTable called");
        currentPage = 1; // Reset currentPage to 1 when repopulating table
        displayData(csvData);
    
        // Update pagination when page changes
        const updatePagination = () => {
            $('#paginationInfo').text(`Page ${currentPage} of ${Math.ceil(csvData.length / rowsPerPage)}`);
        };
    
        // Event handler for Next button
        $('#nextPage').on('click', () => {
            if (currentPage < Math.ceil(csvData.length / rowsPerPage)) {
                currentPage++;
                displayData(csvData);
                updatePagination();
            }
        });
    
        // Event handler for Previous button
        $('#prevPage').on('click', () => {
            if (currentPage > 1) {
                currentPage--;
                displayData(csvData);
                updatePagination();
            }
        });
    
        // Display initial pagination info
        updatePagination();
    };

    // Function to check if dataset exists
    const checkDatasetExists = (callback) => {
        $.ajax({
            url: '/api/check_dataset',
            type: 'GET',
            success: (response) => {
                callback(response.exists);
            },
            error: (xhr, status, error) => {
                Swal.fire({
                    title: 'Error',
                    text: 'Gagal mengecek keberadaan dataset.',
                    icon: 'error',
                    showCloseButton: true,
                    showConfirmButton: false,
                    allowEscapeKey: false,
                    allowOutsideClick: false,
                });
                callback(false);
            }
        });
    };

    // Event handler for CSV upload button
    $('#btn_upload_dataset').on('click', () => {
        checkDatasetExists((exists) => {
            if (exists) {
                Swal.fire({
                    title: 'Warning',
                    text: 'Dataset sudah ada. Hapus dataset terlebih dahulu sebelum mengupload yang baru.',
                    icon: 'warning',
                    showConfirmButton: true,
                    showCloseButton: true,
                    allowEscapeKey: false,
                    allowOutsideClick: false,
                });
            } else {
                handleCSVUpload();
            }
        });
    });

    const storedData = localStorage.getItem('csvData');
    if (storedData) {
        const csvData = JSON.parse(storedData);
        populateTable(csvData);
    }

    $('#btn_hapus_dataset').on('click', () => {
        Swal.fire({
            title: 'Apakah Anda Yakin?',
            text: "Data yang dihapus tidak dapat dikembalikan!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ya, hapus!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: '/api/delete_datasets',
                    type: 'DELETE',
                }).done((response) => {
                    if (response.result === 'success') {
                        // Clear local storage
                        localStorage.removeItem('csvData');
                        localStorage.removeItem('preprocessData');
                        localStorage.removeItem('scrapedData');
                        Swal.fire(
                            'Dihapus!',
                            'Dataset telah dihapus.',
                            'success'
                        ).then(() => {
                            location.reload(true); // Reload the page to reflect changes
                        });
                    } else {
                        Swal.fire(
                            'Error!',
                            'Terjadi kesalahan saat menghapus dataset.',
                            'error'
                        );
                    }
                });
            }
        });
    });

    // Your existing code for reloading data
    $('#reloadData').click(() => {
        reqBarData();
        populateTable(csvData);
        displayDataScraping(data);
    });

    reqBarData();
    
});
