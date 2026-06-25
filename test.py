
import requests

payload = {
    "action": "opened",
    "issue": {
        "number": 42,
        "title": "Bug: divide_numbers crashes",
        "body": "ZeroDivisionError when denominator is 0"
    }
}

r = requests.post("http://localhost:8000/webhook", json=payload)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")


