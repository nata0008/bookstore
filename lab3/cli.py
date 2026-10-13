"""
Книжковий магазин — термінальний інтерфейс (CLI)
Запуск: python cli.py
"""

from bookstore import Bookstore, BookNotFoundError, InsufficientStockError

store = Bookstore()

# Додаємо кілька книг одразу щоб не починати з порожнього магазину
store.add_book("Kobzar", "Taras Shevchenko", 150.0, 10)
store.add_book("Zakhar Berkut", "Ivan Franko", 100.5, 4)
store.add_book("Lisova Pisnia", "Lesya Ukrainka", 120.0, 6)
store.add_book("Eneida", "Ivan Kotlyarevsky", 90.0, 8)

# Додаємо жанри та ISBN вручну (бо add_book їх не приймає — спадщина ПР2)
store._inventory["Kobzar"].update({"genre": "Poetry", "isbn": "978-966-01-0001-1"})
store._inventory["Zakhar Berkut"].update({"genre": "Historical Fiction", "isbn": "978-966-01-0002-8"})
store._inventory["Lisova Pisnia"].update({"genre": "Poetry", "isbn": "978-966-01-0003-5"})
store._inventory["Eneida"].update({"genre": "Poetry", "isbn": "978-966-01-0004-2"})


# ─── допоміжні функції виводу ────────────────────────────────────────────────

def separator():
    print("─" * 52)

def print_book(book: dict):
    print(f"  Назва  : {book.get('title', '—')}")
    print(f"  Автор  : {book.get('author', '—')}")
    print(f"  Жанр   : {book.get('genre', '—')}")
    print(f"  ISBN   : {book.get('isbn', '—')}")
    print(f"  Ціна   : {book.get('price', 0):.2f} грн")
    print(f"  Кількість: {book.get('quantity', 0)} шт.")
    ratings = book.get("ratings", [])
    if ratings:
        avg = round(sum(ratings) / len(ratings), 2)
        print(f"  Рейтинг: {avg} ⭐  ({len(ratings)} оцінок)")
    else:
        print(f"  Рейтинг: оцінок ще немає")

def print_menu():
    separator()
    print("         КНИЖКОВИЙ МАГАЗИН")
    separator()
    print(" 1. Показати всі книги")
    print(" 2. Додати книгу")
    print(" 3. Видалити книгу")
    print(" 4. Купити книгу")
    print(" 5. Пошук книги")
    print(" 6. Оцінити книгу")
    print(" 7. Переглянути рейтинг книги")
    print(" 8. Загальна вартість інвентарю")
    print(" 0. Вийти")
    separator()


# ─── обробники пунктів меню ──────────────────────────────────────────────────

def show_all():
    books = store._inventory
    if not books:
        print("Магазин порожній.")
        return
    print(f"\nУсього книг: {len(books)}")
    separator()
    for book in books.values():
        print_book(book)
        separator()


def add_book():
    print("\n── Додавання книги ──")
    title  = input("Назва   : ").strip()
    author = input("Автор   : ").strip()
    genre  = input("Жанр    : ").strip()
    isbn   = input("ISBN    : ").strip()
    try:
        price    = float(input("Ціна    : "))
        quantity = int(input("Кількість: "))
    except ValueError:
        print("❌ Ціна і кількість мають бути числами.")
        return

    try:
        store.add_book(title, author, price, quantity)
        # зберігаємо жанр та ISBN окремо
        if title.strip() in store._inventory:
            store._inventory[title.strip()].update({
                "genre": genre,
                "isbn": isbn,
            })
        print(f"✅ Книгу «{title}» додано до інвентарю.")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def remove_book():
    print("\n── Видалення книги ──")
    title = input("Назва книги: ").strip()
    try:
        removed = store.remove_book(title)
        if removed:
            print(f"✅ Книгу «{title}» видалено.")
        else:
            print(f"⚠️  Книги «{title}» не було в інвентарі.")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def purchase_book():
    print("\n── Покупка книги ──")
    title = input("Назва книги : ").strip()
    try:
        qty = int(input("Кількість   : "))
    except ValueError:
        print("❌ Кількість має бути цілим числом.")
        return

    try:
        total = store.purchase_book(title, qty)
        print(f"✅ Куплено {qty} шт. «{title}».")
        print(f"   Сума до сплати: {total:.2f} грн")
    except BookNotFoundError:
        print(f"❌ Книги «{title}» немає в магазині.")
    except InsufficientStockError as e:
        print(f"❌ Недостатньо примірників: {e}")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def search_book():
    print("\n── Пошук книги ──")
    print("Залиш поле порожнім, щоб не використовувати критерій.")
    title  = input("Назва (часткова): ").strip() or None
    author = input("Автор (частковий): ").strip() or None
    genre  = input("Жанр             : ").strip() or None
    isbn   = input("ISBN (точний)    : ").strip() or None

    try:
        results = store.search_book(title=title, author=author,
                                    genre=genre, isbn=isbn)
        if results:
            print(f"\nЗнайдено: {len(results)} книг(и)")
            separator()
            for book in results:
                print_book(book)
                separator()
        else:
            print("⚠️  Нічого не знайдено за вказаними критеріями.")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def rate_book():
    print("\n── Оцінювання книги ──")
    title = input("Назва книги: ").strip()
    try:
        rating = float(input("Оцінка (1–5): "))
    except ValueError:
        print("❌ Оцінка має бути числом.")
        return

    try:
        store.rate_book(title, rating)
        avg = store.get_average_rating(title)
        print(f"✅ Оцінку збережено. Середній рейтинг «{title}»: {avg} ⭐")
    except BookNotFoundError:
        print(f"❌ Книги «{title}» немає в магазині.")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def show_rating():
    print("\n── Рейтинг книги ──")
    title = input("Назва книги: ").strip()
    try:
        avg = store.get_average_rating(title)
        if avg is None:
            print(f"⚠️  Книга «{title}» ще не має оцінок.")
        else:
            ratings = store._inventory[title].get("ratings", [])
            print(f"   Середній рейтинг: {avg} ⭐  (на основі {len(ratings)} оцінок)")
    except BookNotFoundError:
        print(f"❌ Книги «{title}» немає в магазині.")
    except ValueError as e:
        print(f"❌ Помилка: {e}")


def show_inventory_value():
    value = store.inventory_value()
    print(f"\n💰 Загальна вартість інвентарю: {value:.2f} грн")


# ─── головний цикл ───────────────────────────────────────────────────────────

ACTIONS = {
    "1": show_all,
    "2": add_book,
    "3": remove_book,
    "4": purchase_book,
    "5": search_book,
    "6": rate_book,
    "7": show_rating,
    "8": show_inventory_value,
}

def main():
    print("\nДобро пожаловати до книжкового магазину!")
    while True:
        print_menu()
        choice = input("Оберіть пункт: ").strip()
        if choice == "0":
            print("До побачення! 👋")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("❌ Невідомий пункт. Спробуйте ще раз.")


if __name__ == "__main__":
    main()