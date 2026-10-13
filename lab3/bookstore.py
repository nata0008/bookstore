class BookNotFoundError(KeyError):
    """Книги немає в інвентарі."""


class InsufficientStockError(ValueError):
    """На складі недостатньо примірників."""


class Bookstore:
    def __init__(self):
        # ключ - назва книги, значення - словник з деталями
        self._inventory = {}

    @staticmethod
    def _validate_title(title):
        if title is None or not isinstance(title, str) or not title.strip():
            raise ValueError("Назва книги не може бути порожньою або None.")
        return title.strip()

    # ──────────────────────────────────────────────
    # Методи з ПР2 (залишені без змін)
    # ──────────────────────────────────────────────

    def add_book(self, title: str, author: str, price: float, quantity: int) -> None:
        """Додає книгу. Якщо вона вже є — збільшує кількість і оновлює ціну."""
        title = self._validate_title(title)
        if price < 0:
            raise ValueError("Ціна не може бути від'ємною.")
        if quantity < 0:
            raise ValueError("Кількість не може бути від'ємною.")
        if title in self._inventory:
            book = self._inventory[title]
            book["quantity"] += quantity
            book["price"] = price
        else:
            self._inventory[title] = {
                "title": title,
                "author": author,
                "price": price,
                "quantity": quantity,
            }

    def remove_book(self, title: str) -> bool:
        """Видаляє книгу. Повертає True, якщо видалено, False — якщо її не було."""
        title = self._validate_title(title)
        return self._inventory.pop(title, None) is not None

    def purchase_book(self, title: str, quantity: int) -> float:
        """Зменшує запас і повертає загальну вартість покупки."""
        title = self._validate_title(title)
        if quantity <= 0:
            raise ValueError("Кількість для покупки має бути додатною.")
        book = self._inventory.get(title)
        if book is None:
            raise BookNotFoundError(f"Книги '{title}' немає в інвентарі.")
        if quantity > book["quantity"]:
            raise InsufficientStockError(
                f"Запитано {quantity}, на складі лише {book['quantity']}."
            )
        book["quantity"] -= quantity
        return round(book["price"] * quantity, 2)

    def inventory_value(self) -> float:
        """Загальна вартість усіх книг на складі."""
        return round(
            sum(b["price"] * b["quantity"] for b in self._inventory.values()), 2
        )

    # ──────────────────────────────────────────────
    # Функція 1 (ПР3): Пошук книг
    # ──────────────────────────────────────────────

    def search_book(self, title: str = None, author: str = None,
                    genre: str = None, isbn: str = None) -> list:
        """
        Шукає книги за одним або кількома критеріями.

        Параметри (усі необов'язкові, але хоча б один має бути заданий):
          title  — часткова або повна назва (без урахування регістру)
          author — ім'я автора (без урахування регістру)
          genre  — жанр книги (без урахування регістру)
          isbn   — ISBN (точний збіг)

        Повертає список словників із даними книг, що відповідають
        усім заданим критеріям. Якщо збігів немає — порожній список.

        Виключення:
          ValueError — якщо жоден критерій не задано або критерій є
                       порожнім рядком чи рядком з пробілів.
        """
        criteria = {"title": title, "author": author, "genre": genre, "isbn": isbn}
        active = {k: v for k, v in criteria.items() if v is not None}

        if not active:
            raise ValueError("Необхідно задати хоча б один критерій пошуку.")

        for key, value in active.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Критерій '{key}' не може бути порожнім рядком або пробілами."
                )

        results = []
        for book in self._inventory.values():
            match = True
            if "title" in active and active["title"].strip().lower() not in book["title"].lower():
                match = False
            if "author" in active and active["author"].strip().lower() not in book.get("author", "").lower():
                match = False
            if "genre" in active and active["genre"].strip().lower() not in book.get("genre", "").lower():
                match = False
            if "isbn" in active and active["isbn"].strip() != book.get("isbn", ""):
                match = False
            if match:
                results.append(dict(book))

        return results

    # ──────────────────────────────────────────────
    # Функція 2 (ПР3): Рейтинг книг
    # ──────────────────────────────────────────────

    def rate_book(self, title: str, rating: float) -> None:
        """
        Додає оцінку книги від 1 до 5 зірок.

        Параметри:
          title  — назва книги (точний збіг після trim)
          rating — число від 1.0 до 5.0 включно

        Виключення:
          ValueError      — якщо title порожній/None або rating поза діапазоном
          BookNotFoundError — якщо книги немає в інвентарі
        """
        title = self._validate_title(title)
        if not isinstance(rating, (int, float)):
            raise ValueError("Оцінка повинна бути числом.")
        if rating < 1 or rating > 5:
            raise ValueError("Оцінка повинна бути від 1 до 5.")

        book = self._inventory.get(title)
        if book is None:
            raise BookNotFoundError(f"Книги '{title}' немає в інвентарі.")

        if "ratings" not in book:
            book["ratings"] = []
        book["ratings"].append(float(rating))

    def get_average_rating(self, title: str) -> float | None:
        """
        Повертає середній рейтинг книги або None, якщо оцінок ще немає.

        Виключення:
          ValueError      — якщо title порожній/None
          BookNotFoundError — якщо книги немає в інвентарі
        """
        title = self._validate_title(title)
        book = self._inventory.get(title)
        if book is None:
            raise BookNotFoundError(f"Книги '{title}' немає в інвентарі.")

        ratings = book.get("ratings", [])
        if not ratings:
            return None
        return round(sum(ratings) / len(ratings), 2)