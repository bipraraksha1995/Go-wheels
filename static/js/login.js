document.addEventListener('DOMContentLoaded', function() {
    const phoneStep = document.getElementById('phone-step');
    const otpStep = document.getElementById('otp-step');
    const registerStep = document.getElementById('register-step');
    
    const phoneForm = document.getElementById('phone-form');
    const otpForm = document.getElementById('otp-form');
    const registerForm = document.getElementById('register-form');
    
    const phoneInput = document.getElementById('phone');
    const phoneDisplay = document.getElementById('phone-display');
    const otpInputs = document.querySelectorAll('.otp-input');
    const profilePhotoInput = document.getElementById('profile-photo');
    
    let currentPhone = '';
    
    // Phone form submission
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPhone = phoneInput.value;
        
        if (validatePhone(currentPhone)) {
            phoneDisplay.textContent = currentPhone;
            
            // Send OTP request to backend
            fetch('/send-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ phone: currentPhone })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('OTP sent to your mobile. Please check your SMS.');
                    showStep(otpStep);
                } else {
                    alert(data.error || 'Failed to send OTP');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to send OTP. Please try again.');
            });
        } else {
            alert('Please enter a valid 10-digit phone number');
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
                    alert(data.error || 'Invalid OTP. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
        } else {
            alert('Please enter complete 6-digit OTP');
        }
    });
    
    // Registration form submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fullName = document.getElementById('full-name').value;
            const pincode = document.getElementById('pincode').value;
            
            if (fullName && pincode) {
                alert('Registration successful! Welcome to GoWheels!');
                window.location.href = '/user-dashboard/';
            } else {
                alert('Please fill all required fields');
            }
        });
    }
    
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
        
        // Prevent paste
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text');
            if (pastedData.length === 6 && /^\d+$/.test(pastedData)) {
                otpInputs.forEach((inp, idx) => {
                    inp.value = pastedData[idx] || '';
                });
            }
        });
    });
    
    // Profile photo preview
    if (profilePhotoInput) {
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
    }
    
    // Resend OTP
    const resendBtn = document.getElementById('resend-otp');
    if (resendBtn) {
        resendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Send OTP request to backend
            fetch('/send-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ phone: currentPhone })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('OTP resent to your mobile. Please check your SMS.');
                } else {
                    alert(data.error || 'Failed to resend OTP');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to resend OTP. Please try again.');
            });
        });
    }
    function showStep(step) {
        document.querySelectorAll('.login-step').forEach(s => s.classList.remove('active'));
        step.classList.add('active');
    }
    
    function validatePhone(phone) {
        const phoneRegex = /^[6-9]\d{9}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
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
