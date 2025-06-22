# services/external_api.py
import requests

def get_exchange_rate(base="KRW", target="USD"):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "base": base,
            "target": target,
            "rate": data["rates"].get(target),
            "date": data["date"]
        }
    except Exception as e:
        return {"error": str(e)}
