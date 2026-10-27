from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
    amount: float
    currency: str = "UAH"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Грошова сума не може бути від'ємною.")

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"Невідповідність валют: {self.currency} != {other.currency}"
            )
        return Money(round(self.amount + other.amount, 2), self.currency)

    def __mul__(self, factor: float | int) -> Money:
        if factor < 0:
            raise ValueError("Множник не може бути від'ємним.")
        return Money(round(self.amount * factor, 2), self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    def __repr__(self) -> str:
        return f"Money(amount={self.amount!r}, currency={self.currency!r})"