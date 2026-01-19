from prophet import Prophet
try:
    m = Prophet()
    print("SUCCESS: Prophet initialized")
except Exception as e:
    print(f"FAILURE: {e}")
