// Main JavaScript file for the Hotel Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            if (passwordInput) {
                // Toggle password visibility
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    this.innerHTML = '<i class="bi bi-eye-slash"></i>';
                } else {
                    passwordInput.type = 'password';
                    this.innerHTML = '<i class="bi bi-eye"></i>';
                }
            }
        });
    });

    // Validate forms with the 'needs-validation' class
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Date range picker initialization for booking dates
    if (document.getElementById('check_in_date') && document.getElementById('check_out_date')) {
        const checkInDate = document.getElementById('check_in_date');
        const checkOutDate = document.getElementById('check_out_date');
        
        // Set min dates to today
        const today = new Date().toISOString().split('T')[0];
        checkInDate.setAttribute('min', today);
        
        // Update checkout min date when checkin changes
        checkInDate.addEventListener('change', function() {
            checkOutDate.setAttribute('min', this.value);
            if (checkOutDate.value && new Date(checkOutDate.value) <= new Date(this.value)) {
                // If checkout date is before or same as checkin, set it to the day after checkin
                const nextDay = new Date(this.value);
                nextDay.setDate(nextDay.getDate() + 1);
                checkOutDate.value = nextDay.toISOString().split('T')[0];
            }
        });
    }

    // Password confirmation validation
    if (document.getElementById('password') && document.getElementById('password_confirm')) {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('password_confirm');
        
        function validatePassword() {
            if (password.value != confirmPassword.value) {
                confirmPassword.setCustomValidity("Passwords don't match");
            } else {
                confirmPassword.setCustomValidity('');
            }
        }
        
        password.addEventListener('change', validatePassword);
        confirmPassword.addEventListener('keyup', validatePassword);
    }

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.forEach(function (popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Global date picker behavior for check-in/check-out fields
    const checkInInputs = document.querySelectorAll('input[name="check_in"], input[name="check_in_date"]');
    const checkOutInputs = document.querySelectorAll('input[name="check_out"], input[name="check_out_date"]');
    
    // Set minimum date to today for all check-in fields
    const today = new Date().toISOString().split('T')[0];
    checkInInputs.forEach(input => {
        if (input) {
            input.min = today;
            
            // Update check-out min date when check-in changes
            input.addEventListener('change', function() {
                const relatedCheckOutId = this.id.replace('check_in', 'check_out').replace('check-in', 'check-out');
                const checkOutInput = document.getElementById(relatedCheckOutId);
                
                if (checkOutInput) {
                    checkOutInput.min = this.value;
                    
                    // If check-out date is earlier than check-in, update it
                    if (checkOutInput.value && checkOutInput.value < this.value) {
                        checkOutInput.value = this.value;
                    }
                }
            });
        }
    });
    
    // Set minimum date to today for all check-out fields
    checkOutInputs.forEach(input => {
        if (input) {
            input.min = today;
        }
    });
    
    // Handle discount code validation
    const discountCodeInputs = document.querySelectorAll('input[name="discount_code"]');
    discountCodeInputs.forEach(input => {
        if (input) {
            input.addEventListener('blur', function() {
                if (this.value.trim() !== '') {
                    validateDiscountCode(this.value);
                }
            });
        }
    });
    
    // Validate discount code via AJAX
    function validateDiscountCode(code) {
        fetch('/api/validate_discount', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ discount_code: code }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Show success message
                showAlert('success', `Discount code applied! You'll receive ${data.percentage}% off your booking.`);
                
                // Update price if on a booking page
                const totalAmountElement = document.getElementById('total-amount');
                const subtotalElement = document.getElementById('subtotal');
                const discountRow = document.getElementById('discount-row');
                const discountAmountElement = document.getElementById('discount-amount');
                
                if (totalAmountElement && subtotalElement && discountRow && discountAmountElement) {
                    const subtotal = parseFloat(subtotalElement.textContent.replace('₹', ''));
                    const discountAmount = (subtotal * data.percentage) / 100;
                    const finalTotal = subtotal - discountAmount;
                    
                    discountAmountElement.textContent = '-₹' + discountAmount.toFixed(2);
                    totalAmountElement.textContent = '₹' + finalTotal.toFixed(2);
                    discountRow.classList.remove('d-none');
                }
            } else {
                // Show error message
                showAlert('danger', 'Invalid discount code. Please try again.');
                
                // Reset discount if on a booking page
                const discountRow = document.getElementById('discount-row');
                if (discountRow) {
                    discountRow.classList.add('d-none');
                }
            }
        })
        .catch(error => {
            console.error('Error validating discount code:', error);
        });
    }
    
    // Check room availability
    const availabilityForm = document.getElementById('availability-form');
    if (availabilityForm) {
        availabilityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const roomTypeId = this.querySelector('input[name="room_type_id"]').value;
            const checkIn = this.querySelector('input[name="check_in"]').value;
            const checkOut = this.querySelector('input[name="check_out"]').value;
            
            checkAvailability(roomTypeId, checkIn, checkOut);
        });
    }
    
    // Check availability via AJAX
    function checkAvailability(roomTypeId, checkIn, checkOut) {
        fetch('/api/check_availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                room_type_id: roomTypeId,
                check_in: checkIn,
                check_out: checkOut
            }),
        })
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('availability-results');
            if (!resultsContainer) return;
            
            let html = '';
            
            if (data.available) {
                html += `<div class="alert alert-success">
                    <strong>Great!</strong> We have ${data.room_count} rooms available for your selected dates.
                </div>`;
                
                // Display available rooms
                if (data.available_rooms && data.available_rooms.length > 0) {
                    html += `<div class="mt-3">
                        <h6>Available Rooms:</h6>
                        <ul class="list-group">`;
                    
                    data.available_rooms.forEach(room => {
                        html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <strong>Room ${room.number}</strong><br>
                                <small class="text-muted">Floor ${room.floor} | ${room.capacity} Guests</small>
                            </div>
                            <a href="/book-room/${room.id}?check_in=${checkIn}&check_out=${checkOut}" class="btn btn-sm btn-outline-primary">Select</a>
                        </li>`;
                    });
                    
                    html += `</ul></div>`;
                }
                
                // Show booked rooms if any exist
                if (data.booked_rooms && data.booked_rooms.length > 0) {
                    html += `<div class="mt-3">
                        <h6>Currently Booked Rooms:</h6>
                        <ul class="list-group">`;
                    
                    data.booked_rooms.forEach(room => {
                        html += `<li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                            <div>
                                <strong>Room ${room.number}</strong><br>
                                <small class="text-muted">Floor ${room.floor} | ${room.capacity} Guests</small>
                            </div>
                            <span class="badge bg-secondary">Booked</span>
                        </li>`;
                    });
                    
                    html += `</ul></div>`;
                }
                
                // Show pending rooms if any exist
                if (data.pending_rooms && data.pending_rooms.length > 0) {
                    html += `<div class="mt-3">
                        <h6>Pending Reservation Rooms:</h6>
                        <ul class="list-group">`;
                    
                    data.pending_rooms.forEach(room => {
                        html += `<li class="list-group-item list-group-item-warning d-flex justify-content-between align-items-center">
                            <div>
                                <strong>Room ${room.number}</strong><br>
                                <small class="text-muted">Floor ${room.floor} | ${room.capacity} Guests</small>
                            </div>
                            <span class="badge bg-warning text-dark">Pending</span>
                        </li>`;
                    });
                    
                    html += `</ul></div>`;
                }
            } else {
                html += `<div class="alert alert-warning">
                    <strong>Sorry!</strong> No rooms are available for the selected dates.`;
                
                // Show if there are pending rooms that might become available
                if (data.pending_rooms && data.pending_rooms.length > 0) {
                    html += `<p class="mt-2 mb-0">There are ${data.pending_rooms.length} rooms with pending reservations that may become available.</p>`;
                }
                
                html += `</div>`;
                
                // Still show the booked/pending rooms for information
                if (data.booked_rooms && data.booked_rooms.length > 0) {
                    html += `<div class="mt-3">
                        <h6>Currently Booked Rooms:</h6>
                        <ul class="list-group">`;
                    
                    data.booked_rooms.forEach(room => {
                        html += `<li class="list-group-item list-group-item-secondary d-flex justify-content-between align-items-center">
                            <div>
                                <strong>Room ${room.number}</strong><br>
                                <small class="text-muted">Floor ${room.floor} | ${room.capacity} Guests</small>
                            </div>
                            <span class="badge bg-secondary">Booked</span>
                        </li>`;
                    });
                    
                    html += `</ul></div>`;
                }
                
                if (data.pending_rooms && data.pending_rooms.length > 0) {
                    html += `<div class="mt-3">
                        <h6>Pending Reservation Rooms:</h6>
                        <ul class="list-group">`;
                    
                    data.pending_rooms.forEach(room => {
                        html += `<li class="list-group-item list-group-item-warning d-flex justify-content-between align-items-center">
                            <div>
                                <strong>Room ${room.number}</strong><br>
                                <small class="text-muted">Floor ${room.floor} | ${room.capacity} Guests</small>
                            </div>
                            <span class="badge bg-warning text-dark">Pending</span>
                        </li>`;
                    });
                    
                    html += `</ul></div>`;
                }
            }
            
            resultsContainer.innerHTML = html;
        })
        .catch(error => {
            console.error('Error checking availability:', error);
            showAlert('danger', 'An error occurred while checking availability. Please try again.');
        });
    }
    
    // Show alert message
    function showAlert(type, message) {
        const alertPlaceholder = document.getElementById('alert-placeholder');
        if (!alertPlaceholder) return;
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertPlaceholder.append(wrapper);
        
        // Auto-close alert after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(wrapper.firstChild);
            alert.close();
        }, 5000);
    }
    
    // Handle room booking form
    const bookRoomBtns = document.querySelectorAll('.book-now-btn');
    bookRoomBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                const roomTypeId = this.getAttribute('data-room-type-id');
                window.location.href = `/room_details/${roomTypeId}`;
            });
        }
    });
    
    // Feedback form star rating
    const ratingInputs = document.querySelectorAll('.rating-input');
    ratingInputs.forEach(input => {
        if (input) {
            input.addEventListener('change', function() {
                const value = this.value;
                const stars = document.querySelectorAll('.rating-star');
                
                stars.forEach((star, index) => {
                    if (index < value) {
                        star.classList.add('active');
                    } else {
                        star.classList.remove('active');
                    }
                });
            });
        }
    });
    
    // Handle star rating systems
    const ratingStars = document.querySelectorAll('.rating-star');
    if (ratingStars.length > 0) {
        const ratingInput = document.getElementById('rating');
        const ratingText = document.querySelector('.rating-text');
        
        const ratingDescriptions = [
            'Click to rate',
            'Poor',
            'Fair',
            'Good',
            'Very Good',
            'Excellent'
        ];
        
        ratingStars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                if (ratingInput && ratingText) {
                    ratingInput.value = rating;
                    ratingText.textContent = ratingDescriptions[rating];
                    
                    ratingStars.forEach((s, index) => {
                        if (index < rating) {
                            s.classList.add('active');
                        } else {
                            s.classList.remove('active');
                        }
                    });
                }
            });
        });
    }
    
    // Handle service ratings
    const serviceRatings = document.querySelectorAll('.service-rating');
    serviceRatings.forEach(container => {
        const stars = container.querySelectorAll('i');
        
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.getAttribute('data-rating'));
                
                stars.forEach((s, index) => {
                    if (index < rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });
    });
    
    // Handle newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            
            // Here you would typically send this to a backend endpoint
            // For demo purposes, we'll just show a success message
            showAlert('success', `Thank you for subscribing with ${email}! You'll receive our latest offers and updates.`);
            this.reset();
        });
    }
}); 