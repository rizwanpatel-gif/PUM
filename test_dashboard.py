import requests
import json
import time

def test_api_connectivity():
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 Testing API Connectivity...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    try:
        response = requests.get(f"{base_url}/dashboard/summary", timeout=5)
        print(f"✅ Dashboard summary: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Recent upgrades: {len(data.get('recent_upgrades', []))}")
            print(f"   Total upgrades: {data.get('total_upgrades', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Dashboard summary failed: {e}")
    
    try:
        response = requests.get(f"{base_url}/analytics/risk-distribution", timeout=5)
        print(f"✅ Risk distribution: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Risk distribution: {data.get('risk_distribution', {})}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Risk distribution failed: {e}")
    
    try:
        response = requests.get(f"{base_url}/analytics/volatility-trends", timeout=5)
        print(f"✅ Volatility trends: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Trends count: {len(data.get('overall_trends', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Volatility trends failed: {e}")
    
    for network in ["ethereum", "polygon", "arbitrum"]:
        try:
            response = requests.get(f"{base_url}/events/{network}", timeout=5)
            print(f"✅ {network.capitalize()} events: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Events count: {len(data.get('events', []))}")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ {network.capitalize()} events failed: {e}")

def test_dashboard_access():
    print("\n🌐 Testing Dashboard Access...")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8050", timeout=5)
        print(f"✅ Dashboard access: {response.status_code}")
        if response.status_code == 200:
            print("   Dashboard is accessible!")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Dashboard access failed: {e}")
        print("   Make sure the dashboard is running with: python app/ui/dashboard.py")

def main():
    print("🚀 PUM Dashboard Debug Test")
    print("=" * 50)
    
    test_api_connectivity()
    
    test_dashboard_access()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. If API tests fail, check if FastAPI is running on port 8000")
    print("2. If dashboard test fails, check if dashboard is running on port 8050")
    print("3. Open browser console (F12) and look for JavaScript errors")
    print("4. Try accessing http://localhost:8050 in your browser")
    print("5. Check if graphs appear after 30 seconds (auto-refresh interval)")

if __name__ == "__main__":
    main() 