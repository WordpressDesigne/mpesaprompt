/**
 * M-Pesa STK Push SaaS - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle sidebar toggle on mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }

    // Handle dropdown submenus
    document.querySelectorAll('.dropdown-menu a.dropdown-toggle').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const parent = this.parentElement;
            const submenu = this.nextElementSibling;
            
            if (submenu && submenu.classList.contains('dropdown-menu')) {
                // Close other open submenus
                document.querySelectorAll('.dropdown-submenu').forEach(function(item) {
                    if (item !== parent) {
                        item.classList.remove('show');
                    }
                });
                
                // Toggle current submenu
                parent.classList.toggle('show');
                submenu.classList.toggle('show');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.closest('.dropdown-menu') === null) {
            document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
                menu.classList.remove('show');
            });
            document.querySelectorAll('.dropdown-submenu').forEach(function(item) {
                item.classList.remove('show');
            });
        }
    });

    // Format phone numbers
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Remove all non-digit characters
            let phone = this.value.replace(/\D/g, '');
            
            // Format based on input length
            if (phone.length > 0) {
                // If it starts with 0, convert to 254
                if (phone.startsWith('0')) {
                    phone = '254' + phone.substring(1);
                } 
                // If it starts with +, remove it
                else if (phone.startsWith('+')) {
                    phone = phone.substring(1);
                }
                // If it's less than 9 digits, assume it's missing country code
                else if (phone.length < 9) {
                    phone = '254' + phone;
                }
                
                // Update the input value
                this.value = phone;
            }
        });
    });

    // Format currency inputs
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            let value = this.value.replace(/[^0-9.]/g, '');
            if (value) {
                // Format as currency
                value = parseFloat(value).toFixed(2);
                this.value = new Intl.NumberFormat('en-US', {
                    style: 'decimal',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
            }
        });
    });

    // Handle file upload preview
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0] ? this.files[0].name : 'Choose file';
            const label = this.nextElementSibling;
            if (label) {
                label.textContent = fileName;
            }
            
            // Image preview if it's an image
            if (this.files && this.files[0] && this.files[0].type.startsWith('image/')) {
                const preview = document.getElementById(this.dataset.preview);
                if (preview) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(this.files[0]);
                }
            }
        });
    });

    // Handle password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.setAttribute('aria-label', 'Show password');
            }
        });
    });

    // Handle data tables
    const dataTables = document.querySelectorAll('.data-table');
    if (dataTables.length > 0) {
        // Initialize DataTables if available
        if (typeof $.fn.DataTable === 'function') {
            dataTables.forEach(function(table) {
                $(table).DataTable({
                    responsive: true,
                    pageLength: 25,
                    order: [],
                    language: {
                        search: "_INPUT_",
                        searchPlaceholder: "Search...",
                        lengthMenu: "Show _MENU_ entries",
                        info: "Showing _START_ to _END_ of _TOTAL_ entries",
                        infoEmpty: "No entries found",
                        infoFiltered: "(filtered from _MAX_ total entries)",
                        paginate: {
                            first: "First",
                            last: "Last",
                            next: "Next",
                            previous: "Previous"
                        }
                    },
                    dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                         "<'row'<'col-sm-12'tr>>" +
                         "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>"
                });
            });
        }
    }

    // Handle form submission with loading state
    const formsWithLoading = document.querySelectorAll('.form-with-loading');
    formsWithLoading.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });

    // Handle tab state persistence
    const tabPanes = document.querySelectorAll('.tab-pane');
    if (tabPanes.length > 0) {
        // Show the first tab by default
        const firstTab = document.querySelector('.nav-tabs .nav-link:first-child');
        if (firstTab) {
            new bootstrap.Tab(firstTab).show();
        }
        
        // Handle tab clicks
        document.querySelectorAll('.nav-tabs .nav-link').forEach(function(tab) {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                const target = this.getAttribute('data-bs-target');
                if (target) {
                    // Update URL hash
                    window.location.hash = target;
                    
                    // Show the tab
                    const tab = new bootstrap.Tab(this);
                    tab.show();
                    
                    // Save tab state to localStorage
                    const tabContainer = this.closest('.nav-tabs');
                    if (tabContainer && tabContainer.id) {
                        localStorage.setItem(tabContainer.id, target);
                    }
                }
            });
        });
        
        // Restore tab state from localStorage or URL hash
        window.addEventListener('load', function() {
            let activeTabId = window.location.hash;
            
            // If no hash, try to get from localStorage
            if (!activeTabId) {
                const tabContainer = document.querySelector('.nav-tabs');
                if (tabContainer && tabContainer.id) {
                    activeTabId = localStorage.getItem(tabContainer.id);
                }
            }
            
            // If we have a valid tab ID, show it
            if (activeTabId) {
                const tab = document.querySelector(`.nav-tabs a[data-bs-target="${activeTabId}"]`);
                if (tab) {
                    new bootstrap.Tab(tab).show();
                }
            }
        });
    }
});

// Helper function to format numbers with commas
function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

// Helper function to format dates
function formatDate(dateString, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    return new Date(dateString).toLocaleDateString('en-US', mergedOptions);
}

// Helper function to show a toast notification
function showToast(options) {
    const defaultOptions = {
        title: '',
        message: '',
        type: 'info', // success, danger, warning, info
        position: 'top-end',
        delay: 5000
    };
    
    const toastOptions = { ...defaultOptions, ...options };
    
    // Create toast HTML
    const toastId = 'toast-' + Math.random().toString(36).substr(2, 9);
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${toastOptions.type} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${toastOptions.delay}">
            <div class="d-flex">
                <div class="toast-body">
                    ${toastOptions.title ? `<strong>${toastOptions.title}</strong><br>` : ''}
                    ${toastOptions.message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Add to container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed ' + 
            (toastOptions.position.includes('top') ? 'top-0' : 'bottom-0') + ' ' +
            (toastOptions.position.includes('start') ? 'start-0' : 
             toastOptions.position.includes('end') ? 'end-0' : 'start-50 translate-middle-x') + 
            ' p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHtml;
    toastContainer.appendChild(toastElement.firstElementChild);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastElement.firstElementChild);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.firstElementChild.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
    
    return toast;
}

// Export functions for use in other scripts
window.App = {
    formatNumber,
    formatDate,
    showToast
};
