document.addEventListener('DOMContentLoaded', function() {
    // Toggle dark mode
    const themeToggleButton = document.getElementById('theme-toggle');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
        });
    }

    // Handle form submission
    const form = document.getElementById('process-form');
    const submitButton = document.getElementById('process-button');
    const resultDiv = document.getElementById('result');
    const resultMessage = document.getElementById('result-message');
    const resultOutput = document.getElementById('result-output');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the default form submission

            // Disable the submit button
            submitButton.disabled = true;
            submitButton.textContent = 'Processing...';

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                // Replace the current page's HTML with the response
                document.open();
                document.write(html);
                document.close();
            })
            .catch(error => {
                console.error('Error:', error);
                resultDiv.classList.remove('is-hidden');
                resultMessage.textContent = 'An error occurred while processing.';
                resultOutput.textContent = '';
            })
            .finally(() => {
                // Re-enable the submit button after processing
                submitButton.disabled = false;
                submitButton.textContent = 'Process';
            });
        });
    }

    // Optional: Hide the result notification when the close button is clicked
    if (resultDiv) {
        const closeButton = document.querySelector('#result .delete');
        if (closeButton) {
            closeButton.addEventListener('click', function () {
                resultDiv.classList.add('is-hidden');
            });
        }
    }

    // Toggle between web search and file upload options
    const webSearchOptions = document.getElementById('web-search-options');
    const fileUploadOption = document.getElementById('file-upload-option');
    const processTypeInputs = document.querySelectorAll('input[name="process_type"]');
    const fileInput = document.querySelector('#file-upload-option input[type="file"]');

    processTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value === 'web') {
                webSearchOptions.style.display = 'block';
                fileUploadOption.style.display = 'none';
                fileInput.removeAttribute('required');
            } else {
                webSearchOptions.style.display = 'none';
                fileUploadOption.style.display = 'block';
                fileInput.setAttribute('required', '');
            }
        });
    });

    // Ensure correct initial state
    const initialProcessType = document.querySelector('input[name="process_type"]:checked');
    if (initialProcessType) {
        if (initialProcessType.value === 'web') {
            webSearchOptions.style.display = 'block';
            fileUploadOption.style.display = 'none';
            fileInput.removeAttribute('required');
        } else {
            webSearchOptions.style.display = 'none';
            fileUploadOption.style.display = 'block';
            fileInput.setAttribute('required', '');
        }
    }

    // Search Engine Management
    const searchEnginesContainer = document.getElementById('search-engines');
    const addSearchEngineButton = document.getElementById('add-search-engine');

    if (searchEnginesContainer && addSearchEngineButton) {
        // Function to create a new search engine entry
        function createSearchEngineEntry(name = '', url = '') {
            const entry = document.createElement('div');
            entry.className = 'field has-addons search-engine-entry';
            entry.innerHTML = `
                <div class="control">
                    <input class="input" type="text" name="search_engine_name[]" value="${name}" placeholder="Name" required>
                </div>
                <div class="control">
                    <input class="input" type="text" name="search_engine_url[]" value="${url}" placeholder="URL" required>
                </div>
                <div class="control">
                    <button type="button" class="button is-danger remove-search-engine">Remove</button>
                </div>
            `;
            return entry;
        }

        // Add a new search engine entry
        addSearchEngineButton.addEventListener('click', function() {
            const newEntry = createSearchEngineEntry();
            searchEnginesContainer.appendChild(newEntry);
        });

        // Remove a search engine entry
        searchEnginesContainer.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-search-engine')) {
                const entry = e.target.closest('.search-engine-entry');
                if (entry) {
                    entry.remove();
                }
            }
        });

        // Prevent form submission if there are no search engines
        const configForm = document.getElementById('config-form');
        if (configForm) {
            configForm.addEventListener('submit', function(e) {
                const searchEngineEntries = searchEnginesContainer.querySelectorAll('.search-engine-entry');
                if (searchEngineEntries.length === 0) {
                    e.preventDefault();
                    alert('Please add at least one search engine.');
                }
            });
        }
    }
});