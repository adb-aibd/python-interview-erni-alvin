import requests

resp = requests.post(
    "http://localhost:5000/rates",
    json={
        "rate_date": "2026-02-01",
        "base_currency": "PHP",
        "quote_currency": "USD",
        "side": "SELL",
        "rate": "1.0",
    },
    headers={"Content-Type": "application/json"},
)

print(resp.content)
