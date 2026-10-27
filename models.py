from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterator
from value_objects import Money


@dataclass(frozen=True)
class Category:
    id: int
    name: str
    description: str = ""


class Product:
    def __init__(self, product_id: int, name: str, category: Category, price: Money) -> None:
        self.id = product_id
        self.name = name
        self.category = category
        self._price = price

    @property
    def price(self) -> Money:
        return self._price

    @price.setter
    def price(self, new_price: Money) -> None:
        if new_price.amount <= 0:
            raise ValueError("Ціна товару повинна бути більшою за нуль.")
        self._price = new_price

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name!r}, price={self.price})"

    def __str__(self) -> str:
        return f"{self.name} [{self.category.name}] - {self.price}"


@dataclass
class InventoryItem:
    id: int
    product: Product
    _quantity: int = 0

    def __post_init__(self) -> None:
        if self._quantity < 0:
            raise ValueError("Початкова кількість на складі не може бути від'ємною.")

    @property
    def quantity(self) -> int:
        return self._quantity

    def restock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Кількість для поповнення має бути більшою за нуль.")
        self._quantity += amount

    def deduct(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Кількість для списання має бути більшою за нуль.")
        if amount > self._quantity:
            raise ValueError(f"Недостатньо залишку товару '{self.product.name}'. Залишок: {self._quantity}")
        self._quantity -= amount

    @property
    def total_value(self) -> Money:
        return self.product.price * self._quantity


@dataclass
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Кількість у кошику має бути більшою за нуль.")

    @property
    def subtotal(self) -> Money:
        return self.product.price * self.quantity


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)

    def add(self, product: Product, quantity: int = 1) -> None:
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product=product, quantity=quantity))

    def clear(self) -> None:
        self.items.clear()

    def __len__(self) -> int:
        return sum(item.quantity for item in self.items)

    def __iter__(self) -> Iterator[CartItem]:
        return iter(self.items)

    def __contains__(self, product_id: int) -> bool:
        return any(item.product.id == product_id for item in self.items)

    @property
    def total(self) -> Money:
        if not self.items:
            return Money(0.0)
        currency = self.items[0].product.price.currency
        total_amount = sum(item.subtotal.amount for item in self.items)
        return Money(round(total_amount, 2), currency)


class StoreCatalog:
    """Контейнер каталогу, що інкапсулює роботу з наявними товарами."""

    def __init__(self) -> None:
        self._products: dict[int, Product] = {}

    def add_product(self, product: Product) -> None:
        self._products[product.id] = product

    def get_by_id(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def filter_by_category(self, category_name: str) -> list[Product]:
        return [
            p for p in self._products.values()
            if p.category.name.casefold() == category_name.casefold()
        ]

    def find_most_expensive(self) -> Product | None:
        if not self._products:
            return None
        return max(self._products.values(), key=lambda p: p.price.amount)

    def __iter__(self) -> Iterator[Product]:
        return iter(self._products.values())

    def __len__(self) -> int:
        return len(self._products)