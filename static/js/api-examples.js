// GET Request - Fetch Vehicles
async function fetchVehicles() {
    try {
        const response = await fetch('/api/vehicles/');
        const data = await response.json();
        console.log(data.vehicles);
        return data.vehicles;
    } catch (error) {
        console.error('Error:', error);
    }
}

// POST Request - Add Vehicle
async function addVehicle(vehicleData) {
    try {
        const response = await fetch('/api/vehicles/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(vehicleData)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// GET User Profile
async function getUserProfile(userId) {
    try {
        const response = await fetch(`/api/user/${userId}/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// jQuery AJAX Example
function loadVehicles() {
    $.ajax({
        url: '/api/vehicles/',
        method: 'GET',
        success: function(data) {
            console.log(data.vehicles);
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
}