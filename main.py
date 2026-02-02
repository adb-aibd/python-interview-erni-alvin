from typing import Union

from flask import Flask, request
from datetime import date, datetime
from dataclasses import dataclass
import uuid
# from pydantic import BaseModel

app = Flask(__name__)



@dataclass
class Rate:
    id: int
    rate_date: date
    base_currency: str
    quote_currency: str
    side: str
    rate: float
    def __json__(self):
        return {
            "id": self.id,
            "rate_date": self.rate_date,
            "base_currency": self.base_currency,
            "quote_currency": self.quote_currency,
            "side": self.side,
            "rate": "%.10f" % self.rate,
        }

@dataclass
class Transaction:
    transaction_id: str
    timestamp: datetime
    base_currency: str
    quote_currency: str
    side: str
    rate_used: int
    base_amount: float
    foreign_amount: float
    rounding_adjustment: float

transactions = []
rates = [
    Rate(id=0, rate_date=date(2026, 1, 1), base_currency="PHP", quote_currency="USD", side="SELL", rate=1),
    Rate(id=1, rate_date=date(2026, 1, 1), base_currency="PHP", quote_currency="USD", side="BUY", rate=2),
]

@app.route("/rates", methods=["GET"])
def get_rates():
    return rates

@app.route("/rates", methods=["POST"])
def update_rates():
    data = request.get_json()
    # todo: validation
    data["id"] = len(rates)
    rates.append(data)
    return "", 200

@app.route("/transactions", methods=["GET"])
def get_transactions():
    return transactions

@app.route("/transaction", methods=["POST"])
def create_transaction():
    data = request.get_json()
    timestamp = datetime.fromisoformat(data["timestamp"])
    date_timestamp = timestamp.date()
    base_amount = data.get("base_amount")
    foreign_amount = data.get("foreign_amount")
    if (base_amount is None) == (foreign_amount is None):
        return {
            "error": "You must specify only one of 'base_amount' and 'foreign_amount'"
        }, 400
        
    for rate in rates:
        correct_pair = rate.base_currency == data["base_currency"] and rate.quote_currency == data["quote_currency"]

        if not (correct_pair and rate.side == data["side"]):
            continue
        if rate.side == "SELL":
            if foreign_amount is not None:
                base_amount = foreign_amount / rate.rate
            else:
                foreign_amount = base_amount * rate.rate
            transaction_id = uuid.uuid4().hex
            rounded_version = int(foreign_amount * 100) / 100
            rounding_adjustment = foreign_amount - rounded_version
            foreign_amount = rounded_version
            transactions.append(Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                base_currency=rate.base_currency,
                quote_currency=rate.quote_currency,
                side=rate.side,
                rate_used=rate.id,
                base_amount=base_amount,
                foreign_amount=foreign_amount,
                rounding_adjustment=rounding_adjustment,
            ))
            return 
        elif rate.side == "BUY":
            return {"error": "Unimplemented"}, 400


    return {"error": "No existing rates for the given currency pair and side"}, 400