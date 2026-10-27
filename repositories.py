from typing import Generic, TypeVar, TypedDict
from protocols import HasId

T = TypeVar("T", bound=HasId)


class InMemoryRepository(Generic[T]):
    """Універсальний репозиторій для сутностей з ідентифікатором."""

    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, item: T) -> None:
        self._items[item.id] = item

    def get(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def all(self) -> list[T]:
        return list(self._items.values())

    def remove(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None


class ProductPayload(TypedDict):
    id: int
    name: str
    category_id: int
    category_name: str
    price: float
    currency: str