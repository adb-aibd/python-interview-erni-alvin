from typing import (
    Optional,
)

from fastapi import FastAPI
from datetime import date, datetime

# from pydantic import BaseModel
from decimal import Decimal

app = FastAPI()

from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

from sqlalchemy import (
    ForeignKey,
    Enum,
    Numeric,
    String,
)

import enum

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from pydantic import (
    BaseModel,
    Field,
)


class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currency"
    id: Mapped[int] = mapped_column(primary_key=True)
    iso: Mapped[str] = mapped_column(String(3), nullable=False)


class SideEnum(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Rate(Base):
    __tablename__ = "rate"
    id: Mapped[int] = mapped_column(primary_key=True)
    rate_date: Mapped[date] = mapped_column(nullable=False)
    base_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id"), nullable=False
    )
    base_currency: Mapped[Currency] = relationship(foreign_keys=[base_currency_id])
    quote_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id"), nullable=False
    )
    quote_currency: Mapped[Currency] = relationship(foreign_keys=[quote_currency_id])

    side: Mapped[SideEnum] = mapped_column(Enum(SideEnum), nullable=False)
    rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )


class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column()
    rate_used_id: Mapped[int] = mapped_column(ForeignKey("rate.id"))
    rate_used: Mapped[Rate] = relationship()
    base_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )
    foreign_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )
    rounding_adjustment: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )


# with engine.connect() as conn:
#     result = conn.execute(text("select 'hello world'"))
#     print(result.all())


def make_currency_iso_field():
    return Field(pattern=r"[A-Z]{3}")


def make_currency_value_field(nullable: bool = False):
    if nullable:
        return Field(max_digits=20, decimal_places=10, gt=Decimal(0), default=None)
    else:
        return Field(max_digits=20, decimal_places=10, gt=Decimal(0))


class RateCreate(BaseModel):
    rate_date: date
    base_currency: str = make_currency_iso_field()
    quote_currency: str = make_currency_iso_field()
    side: SideEnum
    rate: Optional[Decimal] = make_currency_value_field()


class TransactionCreate(BaseModel):
    _transaction_id: str | None = None

    timestamp: datetime
    base_currency: str = make_currency_iso_field()
    quote_currency: str = make_currency_iso_field()
    side: SideEnum
    base_amount: Optional[Decimal] = make_currency_value_field(nullable=True)
    foreign_amount: Optional[Decimal] = make_currency_value_field(nullable=True)

    def model_post_init(self, ctx):
        print("post init????", self.base_amount, self.foreign_amount)
        if (self.base_amount is None) == (self.foreign_amount is None):
            raise ValueError(
                "Exactly one of `base_amount` and `foreign_amount` must be set."
            )


# transactions = []
rates = [
    RateCreate(
        rate_date=date(2026, 1, 1),
        base_currency="PHP",
        quote_currency="USD",
        side=SideEnum.SELL,
        rate=Decimal("1.12"),
    ),
    RateCreate(
        rate_date=date(2026, 1, 1),
        base_currency="PHP",
        quote_currency="USD",
        side=SideEnum.BUY,
        rate=Decimal("2.13"),
    ),
]

# transactions = [
#     TransactionCreate(base_currency="PHP", quote_currency="USD", side=SideEnum.SELL, timestamp=datetime(2026, 1, 1), base_amount=Decimal("1.012345"), foreign_amount=Decimal("2")),
# ]

# print(transactions)


@app.route("/rates", methods=["GET"])
def get_rates():
    return rates


# @app.route("/rates", methods=["POST"])
# def update_rates():
#     data = request.get_json()
#     # todo: validation
#     data["id"] = len(rates)
#     rates.append(data)
#     return "", 200

# @app.route("/transactions", methods=["GET"])
# def get_transactions():
#     return transactions

# @app.route("/transaction", methods=["POST"])
# def create_transaction():
#     data = request.get_json()
#     timestamp = datetime.fromisoformat(data["timestamp"])
#     date_timestamp = timestamp.date()
#     base_amount = data.get("base_amount")
#     foreign_amount = data.get("foreign_amount")
#     if (base_amount is None) == (foreign_amount is None):
#         return {
#             "error": "You must specify only one of 'base_amount' and 'foreign_amount'"
#         }, 400

#     for rate in rates:
#         correct_pair = rate.base_currency == data["base_currency"] and rate.quote_currency == data["quote_currency"]

#         if not (correct_pair and rate.side == data["side"]):
#             continue
#         if rate.side == "SELL":
#             if foreign_amount is not None:
#                 base_amount = foreign_amount / rate.rate
#             else:
#                 foreign_amount = base_amount * rate.rate
#             transaction_id = uuid.uuid4().hex
#             rounded_version = int(foreign_amount * 100) / 100
#             rounding_adjustment = foreign_amount - rounded_version
#             foreign_amount = rounded_version
#             transactions.append(Transaction(
#                 transaction_id=transaction_id,
#                 timestamp=timestamp,
#                 base_currency=rate.base_currency,
#                 quote_currency=rate.quote_currency,
#                 side=rate.side,
#                 rate_used=rate.id,
#                 base_amount=base_amount,
#                 foreign_amount=foreign_amount,
#                 rounding_adjustment=rounding_adjustment,
#             ))
#             return
#         elif rate.side == "BUY":
#             return {"error": "Unimplemented"}, 400


#     return {"error": "No existing rates for the given currency pair and side"}, 400
