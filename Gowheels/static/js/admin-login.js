document.addEventListener('DOMContentLoaded', function() {
    const phoneStep = document.getElementById('admin-phone-step');
    const otpStep = document.getElementById('admin-otp-step');
    
    const phoneForm = document.getElementById('admin-phone-form');
    const otpForm = document.getElementById('admin-otp-form');
    
    const phoneInput = document.getElementById('admin-phone');
    const phoneDisplay = document.getElementById('admin-phone-display');
    const otpInputs = document.querySelectorAll('.otp-input');
    
    let currentPhone = '';
    let currentOTP = '';
    
    // Phone form submission
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPhone = phoneInput.value;
        
        if (validatePhone(currentPhone)) {
            phoneDisplay.textContent = currentPhone;
            
            // Generate and display OTP
            currentOTP = generateOTP();
            console.log('Admin OTP:', currentOTP);
            alert(`Admin OTP sent to ${currentPhone}. Your OTP is: ${currentOTP}`);
            
            // Auto-fill OTP after 2 seconds
            setTimeout(() => {
                autoFillOTP(currentOTP);
            }, 2000);
            
            showStep(otpStep);
        } else {
            alert('Please enter a valid admin phone number');
        }
    });
    
    // OTP form submission
    otpForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length === 6) {
            if (verifyOTP(otp)) {
                alert('Admin login successful!');
                window.location.href = '/super-admin-panel/';
            } else {
                alert('Invalid OTP. Please try again.');
            }
        } else {
            alert('Please enter complete OTP');
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
    
    // Resend OTP
    document.getElementById('admin-resend-otp').addEventListener('click', function(e) {
        e.preventDefault();
        currentOTP = generateOTP();
        console.log('Resending Admin OTP:', currentOTP);
        alert(`Admin OTP resent to ${currentPhone}. Your new OTP is: ${currentOTP}`);
        
        setTimeout(() => {
            autoFillOTP(currentOTP);
        }, 2000);
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
        return otp.length === 6;
    }
    
    function generateOTP() {
        return Math.floor(100000 + Math.random() * 900000).toString();
    }
    
    function autoFillOTP(otp) {
        otpInputs.forEach((input, index) => {
            input.value = otp[index] || '';
        });
    }
});