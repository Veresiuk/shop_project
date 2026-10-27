from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from value_objects import Money


class HasId(Protocol):
    id: int


@runtime_checkable
class Notifier(Protocol):
    def send(self, recipient: str, message: str) -> None:
        ...


@runtime_checkable
class PaymentGateway(Protocol):
    def process_payment(self, amount: Money) -> str:
        ...


class DiscountPolicy(ABC):
    """Абстрактний базовий клас для стратегії знижок."""

    @abstractmethod
    def apply(self, total: Money) -> Money:
        ...