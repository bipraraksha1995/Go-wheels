#!/usr/bin/env python
"""
Quick Performance Test
Tests response times and throughput
"""
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"


def test_endpoint(url, num_requests=100):
    """Test endpoint performance"""
    print(f"\nTesting: {url}")
    print(f"Requests: {num_requests}")
    
    response_times = []
    errors = 0
    
    start_time = time.time()
    
    for i in range(num_requests):
        try:
            req_start = time.time()
            response = requests.get(url, timeout=10)
            req_end = time.time()
            
            response_times.append((req_end - req_start) * 1000)  # ms
            
            if response.status_code != 200:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"Error: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Calculate statistics
    if response_times:
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        min_time = min(response_times)
        max_time = max(response_times)
        rps = num_requests / duration
        
        print(f"\nResults:")
        print(f"  Total time: {duration:.2f}s")
        print(f"  Requests/sec: {rps:.2f}")
        print(f"  Errors: {errors} ({errors/num_requests*100:.1f}%)")
        print(f"  Response times:")
        print(f"    Min: {min_time:.2f}ms")
        print(f"    Avg: {avg_time:.2f}ms")
        print(f"    Median: {median_time:.2f}ms")
        print(f"    p95: {p95_time:.2f}ms")
        print(f"    p99: {p99_time:.2f}ms")
        print(f"    Max: {max_time:.2f}ms")
        
        # Performance rating
        if avg_time < 200:
            print(f"  Rating: ✅ Excellent")
        elif avg_time < 500:
            print(f"  Rating: ✓ Good")
        elif avg_time < 1000:
            print(f"  Rating: ⚠ Acceptable")
        else:
            print(f"  Rating: ❌ Poor")


def test_concurrent(url, num_requests=100, concurrency=10):
    """Test with concurrent requests"""
    print(f"\nConcurrent Test: {url}")
    print(f"Requests: {num_requests}, Concurrency: {concurrency}")
    
    response_times = []
    errors = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for i in range(num_requests):
            future = executor.submit(requests.get, url, timeout=10)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                req_start = time.time()
                response = future.result()
                req_end = time.time()
                
                response_times.append((req_end - req_start) * 1000)
                
                if response.status_code != 200:
                    errors += 1
            except Exception as e:
                errors += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    if response_times:
        avg_time = statistics.mean(response_times)
        rps = num_requests / duration
        
        print(f"\nResults:")
        print(f"  Total time: {duration:.2f}s")
        print(f"  Requests/sec: {rps:.2f}")
        print(f"  Avg response time: {avg_time:.2f}ms")
        print(f"  Errors: {errors}")


if __name__ == '__main__':
    print("GoWheels Performance Test")
    print("=" * 50)
    
    # Test health endpoint
    test_endpoint(f"{BASE_URL}/health/", num_requests=100)
    
    # Test vehicles list
    test_endpoint(f"{BASE_URL}/api/v1/vehicles/?page=1&limit=20", num_requests=50)
    
    # Test with pagination
    test_endpoint(f"{BASE_URL}/get-vehicles/?page=1", num_requests=50)
    
    # Concurrent test
    test_concurrent(f"{BASE_URL}/health/", num_requests=100, concurrency=10)
    
    print("\n" + "=" * 50)
    print("Performance test complete!")
