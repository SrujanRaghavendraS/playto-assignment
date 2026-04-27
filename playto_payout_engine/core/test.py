import requests
import threading
import uuid

URL = "http://127.0.0.1:8000/api/v1/payouts/"

def make_request():
    headers = {
        "Idempotency-Key": str(uuid.uuid4()),
        "Content-Type": "application/json"
    }

    data = {
        "amount_paise": 10000,
        "bank_account_id": 3
    }

    response = requests.post(URL, json=data, headers=headers)
    print(response.json())


threads = []

for _ in range(2):
    t = threading.Thread(target=make_request)
    threads.append(t)
    t.start()

for t in threads:
    t.join()