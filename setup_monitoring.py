"""
Quick setup script for logging and monitoring
Run this to integrate monitoring into your GoWheels project
"""

import os
import sys


def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"✅ Created {logs_dir}/ directory")
    else:
        print(f"✅ {logs_dir}/ directory already exists")


def update_settings():
    """Instructions for updating settings.py"""
    print("\n" + "="*60)
    print("📝 MANUAL STEP: Update settings.py")
    print("="*60)
    print("\nAdd these lines to gowheels_project/settings.py:\n")
    
    print("# At the top of the file:")
    print("from gowheels.logging_config import LOGGING_CONFIG\n")
    
    print("# Add logging configuration:")
    print("LOGGING = LOGGING_CONFIG\n")
    
    print("# Update MIDDLEWARE list (add these 4 lines):")
    print("MIDDLEWARE = [")
    print("    'django.middleware.security.SecurityMiddleware',")
    print("    'gowheels.monitoring_middleware.CorrelationIdMiddleware',  # ADD")
    print("    'corsheaders.middleware.CorsMiddleware',")
    print("    # ... rest of middleware ...")
    print("    'gowheels.monitoring_middleware.RequestLoggingMiddleware',  # ADD")
    print("    'gowheels.monitoring_middleware.SecurityEventMiddleware',  # ADD")
    print("    'gowheels.monitoring_middleware.MetricsCollectionMiddleware',  # ADD")
    print("]\n")


def update_urls():
    """Instructions for updating urls.py"""
    print("\n" + "="*60)
    print("📝 MANUAL STEP: Update urls.py")
    print("="*60)
    print("\nAdd these lines to gowheels/urls.py:\n")
    
    print("from gowheels import monitoring_views\n")
    
    print("urlpatterns = [")
    print("    # ... existing patterns ...")
    print("    ")
    print("    # Health checks")
    print("    path('health/', monitoring_views.health_check, name='health'),")
    print("    path('health/ready/', monitoring_views.readiness_check, name='readiness'),")
    print("    path('health/live/', monitoring_views.liveness_check, name='liveness'),")
    print("    ")
    print("    # Metrics")
    print("    path('metrics/', monitoring_views.metrics_endpoint, name='metrics'),")
    print("    path('metrics/sli-slo/', monitoring_views.sli_slo_status, name='sli_slo'),")
    print("    path('metrics/performance/', monitoring_views.performance_metrics, name='performance'),")
    print("]\n")


def install_dependencies():
    """Instructions for installing dependencies"""
    print("\n" + "="*60)
    print("📦 INSTALL DEPENDENCIES")
    print("="*60)
    print("\nRun this command:")
    print("pip install psutil==5.9.8\n")


def test_setup():
    """Instructions for testing the setup"""
    print("\n" + "="*60)
    print("🧪 TEST THE SETUP")
    print("="*60)
    print("\n1. Start the server:")
    print("   python manage.py runserver\n")
    
    print("2. Test health check:")
    print("   curl http://localhost:8000/health/\n")
    
    print("3. Test metrics:")
    print("   curl http://localhost:8000/metrics/\n")
    
    print("4. Test SLI/SLO:")
    print("   curl http://localhost:8000/metrics/sli-slo/\n")
    
    print("5. View logs:")
    print("   tail -f logs/gowheels.log\n")


def main():
    print("\n" + "="*60)
    print("🚀 GoWheels Logging & Monitoring Setup")
    print("="*60)
    
    # Step 1: Create logs directory
    create_logs_directory()
    
    # Step 2: Update settings.py
    update_settings()
    
    # Step 3: Update urls.py
    update_urls()
    
    # Step 4: Install dependencies
    install_dependencies()
    
    # Step 5: Test setup
    test_setup()
    
    print("\n" + "="*60)
    print("✅ Setup instructions complete!")
    print("="*60)
    print("\nRead LOGGING_MONITORING_COMPLETE.md for full documentation.\n")


if __name__ == '__main__':
    main()
