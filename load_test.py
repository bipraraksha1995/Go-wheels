"""
Load Testing with Locust
Tests API endpoints under load
"""
from locust import HttpUser, task, between, events
import random
import logging

logger = logging.getLogger(__name__)


class GoWheelsUser(HttpUser):
    """Simulated GoWheels user"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when user starts"""
        self.phone = f"73056752{random.randint(10, 99)}"
        self.register_and_login()
    
    def register_and_login(self):
        """Register and login user"""
        # Register
        self.client.post("/register/", {
            "phone": self.phone,
            "name": "Load Test User",
            "pincode": "600001"
        })
        
        # Send OTP (in real test, would need actual OTP)
        self.client.post("/send-otp/", json={"phone": self.phone})
    
    @task(10)
    def list_vehicles(self):
        """List vehicles (most common operation)"""
        page = random.randint(1, 5)
        categories = ['car', 'bike', 'truck', '']
        category = random.choice(categories)
        
        params = {'page': page, 'limit': 20}
        if category:
            params['cat'] = category
        
        with self.client.get("/get-vehicles/", params=params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(5)
    def view_vehicle(self):
        """View vehicle details"""
        vehicle_id = random.randint(1, 100)
        self.client.get(f"/api/v1/vehicles/{vehicle_id}/")
    
    @task(3)
    def search_vehicles(self):
        """Search vehicles"""
        brands = ['Toyota', 'Honda', 'Yamaha', 'Mahindra']
        brand = random.choice(brands)
        
        self.client.get("/get-vehicles/", params={'br': brand})
    
    @task(2)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health/")
    
    @task(1)
    def create_vehicle(self):
        """Create vehicle listing"""
        self.client.post("/seller-dashboard-form/", {
            "selected_category": "car",
            "selected_brand": "Toyota",
            "selected_model": "Camry",
            "year": "2024",
            "hourly_price": "500",
            "pincode": "600001",
            "village": "Chennai",
            "owner_name": "Test User"
        })


class AdminUser(HttpUser):
    """Simulated admin user"""
    
    wait_time = between(2, 5)
    
    @task
    def admin_dashboard(self):
        """Access admin dashboard"""
        self.client.get("/super-admin-panel/")
    
    @task
    def approve_vehicles(self):
        """Approve pending vehicles"""
        self.client.get("/get-pending-approvals/")


class APIUser(HttpUser):
    """API-only user"""
    
    wait_time = between(0.5, 2)
    host = "http://localhost:8000"
    
    @task(10)
    def api_list_vehicles(self):
        """API: List vehicles"""
        self.client.get("/api/v1/vehicles/", params={'page': 1, 'limit': 20})
    
    @task(5)
    def api_get_vehicle(self):
        """API: Get vehicle"""
        vehicle_id = random.randint(1, 100)
        self.client.get(f"/api/v1/vehicles/{vehicle_id}/")
    
    @task(2)
    def api_metrics(self):
        """API: Metrics endpoint"""
        self.client.get("/metrics/")


# Event listeners for custom metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 2000:  # > 2 seconds
        logger.warning(f"Slow request: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    logger.info("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    logger.info("Load test completed")
    
    # Print statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Total failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time}ms")
    logger.info(f"RPS: {stats.total.total_rps}")


# Run with: locust -f load_test.py --host=http://localhost:8000
# Web UI: http://localhost:8089
