"""
Comprehensive performance tests for Malta Tax AI Backend
Tests for load handling, response times, and scalability
"""
import pytest
import requests
import time
import threading
import statistics
import concurrent.futures
from datetime import datetime, timedelta


class TestPerformanceBaseline:
    """Baseline performance tests for individual endpoints"""
    
    BASE_URL = "http://localhost:5004"
    
    @classmethod
    def setup_class(cls):
        """Setup test class - ensure API is running"""
        try:
            response = requests.get(f"{cls.BASE_URL}/health")
            if response.status_code != 200:
                pytest.skip("API server not running")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not accessible")
    
    def test_health_endpoint_performance(self):
        """Test health endpoint response time"""
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = requests.get(f"{self.BASE_URL}/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Health endpoint should be very fast
        assert avg_response_time < 0.1  # 100ms average
        assert max_response_time < 0.5   # 500ms maximum
        
        print(f"Health endpoint - Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")
    
    def test_income_tax_calculation_performance(self):
        """Test income tax calculation performance"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        response_times = []
        
        for _ in range(20):
            start_time = time.time()
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=payload
            )
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        max_response_time = max(response_times)
        
        # Tax calculation should be reasonably fast
        assert avg_response_time < 0.5   # 500ms average
        assert p95_response_time < 1.0   # 1s for 95th percentile
        assert max_response_time < 2.0   # 2s maximum
        
        print(f"Income tax calculation - Avg: {avg_response_time:.3f}s, P95: {p95_response_time:.3f}s, Max: {max_response_time:.3f}s")
    
    def test_comprehensive_tax_calculation_performance(self):
        """Test comprehensive tax calculation performance"""
        payload = {
            "annual_income": 50000,
            "marital_status": "single",
            "has_property": True,
            "property_value": 200000,
            "business_income": 10000,
            "investment_income": 5000
        }
        
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = requests.post(
                f"{self.BASE_URL}/api/tax/comprehensive",
                json=payload
            )
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Comprehensive calculation may take longer but should still be reasonable
        assert avg_response_time < 1.0   # 1s average
        assert max_response_time < 3.0   # 3s maximum
        
        print(f"Comprehensive tax calculation - Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")
    
    def test_form_generation_performance(self):
        """Test form generation performance"""
        payload = {
            "template_id": "fs3",
            "data": {
                "taxpayer_name": "John Doe",
                "id_number": "123456M",
                "annual_income": 45000,
                "tax_year": 2025
            }
        }
        
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = requests.post(
                f"{self.BASE_URL}/api/forms/create",
                json=payload
            )
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Form generation should be reasonably fast
        assert avg_response_time < 1.0   # 1s average
        assert max_response_time < 2.0   # 2s maximum
        
        print(f"Form generation - Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")


class TestLoadTesting:
    """Load testing with multiple concurrent users"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_concurrent_tax_calculations(self):
        """Test concurrent tax calculations"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.BASE_URL}/api/tax/income-tax",
                    json=payload,
                    timeout=10
                )
                end_time = time.time()
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 20 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results)
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
        else:
            avg_response_time = float('inf')
            p95_response_time = float('inf')
        
        # Performance requirements
        assert success_rate >= 0.95  # 95% success rate
        assert avg_response_time < 2.0  # 2s average response time
        assert p95_response_time < 5.0  # 5s for 95th percentile
        
        print(f"Concurrent load test - Success rate: {success_rate:.2%}, Avg response: {avg_response_time:.3f}s, P95: {p95_response_time:.3f}s")
        
        if failed_requests:
            print(f"Failed requests: {len(failed_requests)}")
            for req in failed_requests[:5]:  # Show first 5 failures
                print(f"  - Status: {req['status_code']}, Error: {req.get('error', 'Unknown')}")
    
    def test_sustained_load(self):
        """Test sustained load over time"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        results = []
        start_time = time.time()
        duration = 30  # 30 seconds test
        
        def make_requests():
            while time.time() - start_time < duration:
                try:
                    request_start = time.time()
                    response = requests.post(
                        f"{self.BASE_URL}/api/tax/income-tax",
                        json=payload,
                        timeout=5
                    )
                    request_end = time.time()
                    
                    results.append({
                        "timestamp": request_start,
                        "response_time": request_end - request_start,
                        "status_code": response.status_code,
                        "success": response.status_code == 200
                    })
                    
                    time.sleep(0.1)  # 10 requests per second per thread
                    
                except Exception as e:
                    results.append({
                        "timestamp": time.time(),
                        "response_time": 0,
                        "status_code": 0,
                        "success": False,
                        "error": str(e)
                    })
        
        # Run with 5 concurrent threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Analyze sustained load results
        successful_requests = [r for r in results if r["success"]]
        total_requests = len(results)
        success_rate = len(successful_requests) / total_requests if total_requests > 0 else 0
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            throughput = len(successful_requests) / duration
        else:
            avg_response_time = float('inf')
            throughput = 0
        
        # Performance requirements for sustained load
        assert success_rate >= 0.90  # 90% success rate under sustained load
        assert avg_response_time < 3.0  # 3s average response time
        assert throughput >= 10  # At least 10 requests per second
        
        print(f"Sustained load test ({duration}s) - Success rate: {success_rate:.2%}, Avg response: {avg_response_time:.3f}s, Throughput: {throughput:.1f} req/s")
    
    def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively under load"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        # Make many requests to test for memory leaks
        for i in range(100):
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=payload
            )
            
            if i % 20 == 0:  # Check memory every 20 requests
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable
                assert memory_growth < 100  # Less than 100MB growth
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Growth: {total_growth:.1f}MB")


class TestScalabilityTesting:
    """Scalability testing for different load patterns"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_increasing_load_pattern(self):
        """Test system behavior under increasing load"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        load_levels = [1, 5, 10, 15, 20]  # Concurrent users
        results = {}
        
        for load_level in load_levels:
            print(f"Testing with {load_level} concurrent users...")
            
            def make_request():
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.BASE_URL}/api/tax/income-tax",
                        json=payload,
                        timeout=10
                    )
                    end_time = time.time()
                    return {
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    }
                except Exception:
                    end_time = time.time()
                    return {
                        "response_time": end_time - start_time,
                        "success": False
                    }
            
            # Run concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=load_level) as executor:
                futures = [executor.submit(make_request) for _ in range(load_level * 3)]
                load_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful = [r for r in load_results if r["success"]]
            success_rate = len(successful) / len(load_results)
            
            if successful:
                avg_response_time = statistics.mean([r["response_time"] for r in successful])
            else:
                avg_response_time = float('inf')
            
            results[load_level] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_requests": len(load_results)
            }
            
            print(f"  Success rate: {success_rate:.2%}, Avg response: {avg_response_time:.3f}s")
        
        # Analyze scalability
        for load_level in load_levels:
            result = results[load_level]
            
            # Success rate should remain high
            assert result["success_rate"] >= 0.80  # 80% minimum
            
            # Response time should not degrade too much
            if load_level <= 10:
                assert result["avg_response_time"] < 2.0  # 2s for low load
            else:
                assert result["avg_response_time"] < 5.0  # 5s for high load
    
    def test_burst_load_handling(self):
        """Test handling of sudden burst loads"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        def burst_requests(num_requests):
            results = []
            
            def make_request():
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.BASE_URL}/api/tax/income-tax",
                        json=payload,
                        timeout=10
                    )
                    end_time = time.time()
                    return {
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    }
                except Exception:
                    end_time = time.time()
                    return {
                        "response_time": end_time - start_time,
                        "success": False
                    }
            
            # Create burst of concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [executor.submit(make_request) for _ in range(num_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            return results
        
        # Test different burst sizes
        burst_sizes = [10, 25, 50]
        
        for burst_size in burst_sizes:
            print(f"Testing burst of {burst_size} requests...")
            
            results = burst_requests(burst_size)
            successful = [r for r in results if r["success"]]
            success_rate = len(successful) / len(results)
            
            if successful:
                avg_response_time = statistics.mean([r["response_time"] for r in successful])
                max_response_time = max([r["response_time"] for r in successful])
            else:
                avg_response_time = float('inf')
                max_response_time = float('inf')
            
            # Burst handling requirements
            assert success_rate >= 0.70  # 70% success rate for bursts
            assert avg_response_time < 10.0  # 10s average for bursts
            assert max_response_time < 30.0  # 30s maximum for bursts
            
            print(f"  Burst {burst_size} - Success: {success_rate:.2%}, Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")


class TestResourceUtilization:
    """Test resource utilization and efficiency"""
    
    BASE_URL = "http://localhost:5004"
    
    def test_cpu_utilization(self):
        """Test CPU utilization under load"""
        import psutil
        
        # Monitor CPU usage during load test
        cpu_percentages = []
        
        def monitor_cpu():
            for _ in range(30):  # Monitor for 30 seconds
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_percentages.append(cpu_percent)
        
        def generate_load():
            payload = {
                "annual_income": 45000,
                "marital_status": "single"
            }
            
            for _ in range(100):
                requests.post(
                    f"{self.BASE_URL}/api/tax/income-tax",
                    json=payload
                )
                time.sleep(0.1)
        
        # Start monitoring and load generation
        monitor_thread = threading.Thread(target=monitor_cpu)
        load_thread = threading.Thread(target=generate_load)
        
        monitor_thread.start()
        time.sleep(1)  # Start monitoring first
        load_thread.start()
        
        monitor_thread.join()
        load_thread.join()
        
        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)
            
            print(f"CPU utilization - Average: {avg_cpu:.1f}%, Maximum: {max_cpu:.1f}%")
            
            # CPU should not be constantly maxed out
            assert avg_cpu < 80.0  # Average CPU under 80%
            assert max_cpu < 95.0  # Maximum CPU under 95%
    
    def test_response_time_consistency(self):
        """Test consistency of response times"""
        payload = {
            "annual_income": 45000,
            "marital_status": "single"
        }
        
        response_times = []
        
        # Collect response times over a period
        for _ in range(50):
            start_time = time.time()
            response = requests.post(
                f"{self.BASE_URL}/api/tax/income-tax",
                json=payload
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
            
            time.sleep(0.2)  # Small delay between requests
        
        if response_times:
            avg_time = statistics.mean(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            min_time = min(response_times)
            max_time = max(response_times)
            
            # Response times should be consistent
            coefficient_of_variation = std_dev / avg_time if avg_time > 0 else 0
            
            print(f"Response time consistency - Avg: {avg_time:.3f}s, StdDev: {std_dev:.3f}s, CV: {coefficient_of_variation:.3f}")
            print(f"  Min: {min_time:.3f}s, Max: {max_time:.3f}s")
            
            # Coefficient of variation should be reasonable (< 1.0 means std dev < mean)
            assert coefficient_of_variation < 1.0
            
            # No response should be extremely slow compared to average
            assert max_time < avg_time * 5  # Max should not be more than 5x average


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

