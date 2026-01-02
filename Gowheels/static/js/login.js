document.addEventListener('DOMContentLoaded', function() {
    const phoneStep = document.getElementById('phone-step');
    const otpStep = document.getElementById('otp-step');
    const registerStep = document.getElementById('register-step');
    
    const phoneForm = document.getElementById('phone-form');
    const otpForm = document.getElementById('otp-form');
    const registerForm = document.getElementById('register-form');
    
    const phoneInput = document.getElementById('phone');
    const phoneDisplay = document.getElementById('phone-display');
    const regPhoneInput = document.getElementById('reg-phone');
    const otpInputs = document.querySelectorAll('.otp-input');
    const profilePhotoInput = document.getElementById('profile-photo');
    
    let currentPhone = '';
    let currentOTP = '';
    
    // Get phone number from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const phoneFromUrl = urlParams.get('phone');
    if (phoneFromUrl) {
        phoneInput.value = phoneFromUrl;
        currentPhone = phoneFromUrl;
        phoneDisplay.textContent = phoneFromUrl;
        
        // Auto-generate OTP and show OTP step
        currentOTP = '123456';
        alert(`OTP sent to ${phoneFromUrl}. Your OTP is: ${currentOTP}`);
        
        setTimeout(() => {
            autoFillOTP(currentOTP);
        }, 2000);
        
        showStep(otpStep);
    }
    
    // Phone form submission
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPhone = phoneInput.value;
        
        if (validatePhone(currentPhone)) {
            phoneDisplay.textContent = currentPhone;
            
            // Generate and display OTP
            currentOTP = '123456'; // Demo OTP
            console.log('Generated OTP:', currentOTP);
            alert(`OTP sent to ${currentPhone}. Your OTP is: ${currentOTP}`);
            
            // Auto-fill OTP after 2 seconds
            setTimeout(() => {
                autoFillOTP(currentOTP);
            }, 2000);
            
            showStep(otpStep);
        } else {
            alert('Please enter a valid phone number');
        }
    });
    
    // OTP form submission
    otpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length === 6) {
            // Send OTP to backend for verification
            fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `phone=${currentPhone}&otp=${otp}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.unique_id) {
                        alert(`Login successful! Your User ID: ${data.unique_id}`);
                    } else {
                        alert('Login successful! Welcome back!');
                    }
                    window.location.href = '/user-dashboard/';
                } else {
                    alert(data.error || 'Login failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
        } else {
            alert('Please enter complete OTP');
        }
    });
    
    // Registration form submission
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fullName = document.getElementById('full-name').value;
        const pincode = document.getElementById('pincode').value;
        const profilePhoto = profilePhotoInput.files[0];
        
        if (fullName && pincode) {
            // Simulate registration
            console.log('Registration data:', {
                name: fullName,
                phone: currentPhone,
                pincode,
                profilePhoto: profilePhoto ? profilePhoto.name : 'No photo'
            });
            
            alert('Registration successful! Welcome to GoWheels!');
            window.location.href = '/user-dashboard/';
        } else {
            alert('Please fill all required fields');
        }
    });
    
    // OTP input handling
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && this.value === '' && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });
    
    // Profile photo preview
    profilePhotoInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const placeholder = document.querySelector('.photo-placeholder');
                placeholder.innerHTML = `<img src="${e.target.result}" class="photo-preview" alt="Profile">`;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Resend OTP
    document.getElementById('resend-otp').addEventListener('click', function(e) {
        e.preventDefault();
        currentOTP = generateOTP();
        console.log('Resending OTP to:', currentPhone);
        console.log('New OTP:', currentOTP);
        alert(`OTP resent to ${currentPhone}. Your new OTP is: ${currentOTP}`);
        
        // Auto-fill new OTP after 2 seconds
        setTimeout(() => {
            autoFillOTP(currentOTP);
        }, 2000);
    });
    
    // Show register form from phone step
    document.getElementById('direct-register').addEventListener('click', function(e) {
        e.preventDefault();
        showStep(registerStep);
    });
    
    // Show register form
    document.getElementById('show-register').addEventListener('click', function(e) {
        e.preventDefault();
        showStep(registerStep);
    });
    
    // Helper functions
    function showStep(step) {
        document.querySelectorAll('.login-step').forEach(s => s.classList.remove('active'));
        step.classList.add('active');
    }
    
    function validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }
    
    function verifyOTP(otp) {
        // Simulate OTP verification (accept any 6-digit code for demo)
        return otp.length === 6;
    }
    
    function isExistingUser(phone) {
        // Simulate user check (return false for demo to show registration)
        return false;
    }
    
    function generateOTP() {
        return Math.floor(100000 + Math.random() * 900000).toString();
    }
    
    function autoFillOTP(otp) {
        otpInputs.forEach((input, index) => {
            input.value = otp[index] || '';
        });
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});