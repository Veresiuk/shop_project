from models import Cart, StoreCatalog, InventoryItem
from repositories import InMemoryRepository, ProductPayload
from services import (
    ConsoleNotifier,
    MockCardPaymentGateway,
    PercentageDiscount,
    StoreService,
)


def main() -> None:
    # Ініціалізація інфраструктури
    catalog = StoreCatalog()
    inventory_repo = InMemoryRepository[InventoryItem]()
    notifier = ConsoleNotifier()
    payment_gw = MockCardPaymentGateway()
    discount = PercentageDiscount(percent=10.0)  # Знижка 10%

    service = StoreService(
        catalog=catalog,
        inventory_repo=inventory_repo,
        payment_gateway=payment_gw,
        notifier=notifier,
        discount_policy=discount,
    )

    # Додавання товарів через TypedDict
    p1_data: ProductPayload = {
        "id": 1,
        "name": "Ноутбук ASUS ROG",
        "category_id": 101,
        "category_name": "Ноутбуки",
        "price": 45000.0,
        "currency": "UAH",
    }
    p2_data: ProductPayload = {
        "id": 2,
        "name": "Миша Logitech MX Master 3S",
        "category_id": 102,
        "category_name": "Периферія",
        "price": 4200.0,
        "currency": "UAH",
    }
    p3_data: ProductPayload = {
        "id": 3,
        "name": "Клавіатура Keychron Q1",
        "category_id": 102,
        "category_name": "Периферія",
        "price": 7800.0,
        "currency": "UAH",
    }

    laptop = service.register_product_from_payload(p1_data, initial_stock=5)
    mouse = service.register_product_from_payload(p2_data, initial_stock=15)
    keyboard = service.register_product_from_payload(p3_data, initial_stock=8)

    print("--- 1. Облік залишків та оцінка складу ---")
    print(f"Загальна вартість усіх запасів на складі: {service.calculate_total_inventory_value()}")

    print("\n--- 2. Пошук та фільтрація в каталозі ---")
    peripherals = catalog.filter_by_category("Периферія")
    print(f"Товари у категорії 'Периферія': {[p.name for p in peripherals]}")

    most_expensive = catalog.find_most_expensive()
    if most_expensive:
        print(f"Найдорожчий товар: {most_expensive.name} ({most_expensive.price})")

    print("\n--- 3. Робота з кошиком (Dunder methods) ---")
    cart = Cart()
    cart.add(laptop, quantity=1)
    cart.add(mouse, quantity=2)

    print(f"Кількість одиниць товару в кошику (__len__): {len(cart)}")
    print(f"Чи є ноутбук (id=1) в кошику (__contains__): {1 in cart}")
    print(f"Початкова сума кошика: {cart.total}")

    print("\n--- 4. Оформлення замовлення (Checkout) ---")
    final_paid = service.checkout(customer_email="student@univ.edu.ua", cart=cart)
    print(f"Підсумкова сплачена сума зі знижкою: {final_paid}")

    # Перевірка списання зі складу
    laptop_stock = inventory_repo.get(laptop.id)
    print(f"Залишок ноутбуків після покупки: {laptop_stock.quantity if laptop_stock else 0} шт.")


if __name__ == "__main__":
    main()