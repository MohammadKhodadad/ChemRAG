import requests
try:
    resp = requests.post(
        f"http://localhost:5000/ask",
        json={"query": "Tell me about polymers."}
    )
    print("\n=== TEST QUERY RESPONSE ===\n", resp.json())
except Exception as e:
    print(f"Test query failed: {e}")