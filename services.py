from protocols import DiscountPolicy, Notifier, PaymentGateway
from value_objects import Money
from models import Cart, StoreCatalog, InventoryItem, Product, Category
from repositories import InMemoryRepository, ProductPayload


class NoDiscount(DiscountPolicy):
    def apply(self, total: Money) -> Money:
        return total


class PercentageDiscount(DiscountPolicy):
    def __init__(self, percent: float) -> None:
        if not (0 <= percent <= 100):
            raise ValueError("Відсоток знижки має бути в діапазоні [0, 100].")
        self.percent = percent

    def apply(self, total: Money) -> Money:
        coefficient = 1.0 - (self.percent / 100.0)
        return Money(round(total.amount * coefficient, 2), total.currency)


class ConsoleNotifier:
    """Адаптер для Notifier без явного наслідування (Structural Typing)."""

    def send(self, recipient: str, message: str) -> None:
        print(f"[Сповіщення -> {recipient}]: {message}")


class MockCardPaymentGateway:
    """Адаптер для PaymentGateway."""

    def process_payment(self, amount: Money) -> str:
        print(f"[Платіжний шлюз]: Списано {amount}")
        return "TX-77491-SUCCESS"


class StoreService:
    """Application Service: оркеструє роботу каталогу, складу та замовлень (DIP/SRP)."""

    def __init__(
        self,
        catalog: StoreCatalog,
        inventory_repo: InMemoryRepository[InventoryItem],
        payment_gateway: PaymentGateway,
        notifier: Notifier,
        discount_policy: DiscountPolicy,
    ) -> None:
        self._catalog = catalog
        self._inventory = inventory_repo
        self._payment_gateway = payment_gateway
        self._notifier = notifier
        self._discount_policy = discount_policy

    def register_product_from_payload(self, payload: ProductPayload, initial_stock: int) -> Product:
        category = Category(id=payload["category_id"], name=payload["category_name"])
        product = Product(
            product_id=payload["id"],
            name=payload["name"],
            category=category,
            price=Money(payload["price"], payload["currency"]),
        )
        self._catalog.add_product(product)
        item = InventoryItem(id=product.id, product=product, _quantity=initial_stock)
        self._inventory.add(item)
        return product

    def calculate_total_inventory_value(self) -> Money:
        all_items = self._inventory.all()
        if not all_items:
            return Money(0.0)
        total = sum(item.total_value.amount for item in all_items)
        return Money(round(total, 2), all_items[0].total_value.currency)

    def checkout(self, customer_email: str, cart: Cart) -> Money:
        if len(cart) == 0:
            raise ValueError("Кошик порожній.")

        # Перевірка наявності на складі
        for cart_item in cart:
            stock = self._inventory.get(cart_item.product.id)
            if stock is None or stock.quantity < cart_item.quantity:
                available = stock.quantity if stock else 0
                raise ValueError(
                    f"Товар '{cart_item.product.name}' недоступний у кількості {cart_item.quantity} шт. (в наявності: {available})"
                )

        final_price = self._discount_policy.apply(cart.total)
        tx_id = self._payment_gateway.process_payment(final_price)

        # Списання зі складу
        for cart_item in cart:
            stock = self._inventory.get(cart_item.product.id)
            if stock:
                stock.deduct(cart_item.quantity)

        self._notifier.send(
            customer_email,
            f"Замовлення успішно оплачено на суму {final_price}. Код транзакції: {tx_id}",
        )
        cart.clear()
        return final_price