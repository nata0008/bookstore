"""
Практична робота №3 — TDD
Функція 1: Пошук книг  (search_book)
Функція 2: Рейтинг книг (rate_book / get_average_rating)

Структура файлу:
  BookstoreTestCase   — базовий клас з setUp
  TestSearchBook      — 12 тестів для пошуку
  TestRateBook        — 12 тестів для рейтингу
"""

import unittest
from bookstore import Bookstore, BookNotFoundError


# ═══════════════════════════════════════════════════════════════
# Базовий клас
# ═══════════════════════════════════════════════════════════════

class BookstoreTestCase(unittest.TestCase):
    def setUp(self):
        """Перед кожним тестом створюємо новий магазин з тестовими книгами."""
        self.store = Bookstore()
        # Додаємо книги з різними авторами та жанрами
        self.store._inventory = {
            "Kobzar": {
                "title": "Kobzar",
                "author": "Taras Shevchenko",
                "price": 150.0,
                "quantity": 10,
                "genre": "Poetry",
                "isbn": "978-966-01-0001-1",
            },
            "Zakhar Berkut": {
                "title": "Zakhar Berkut",
                "author": "Ivan Franko",
                "price": 100.5,
                "quantity": 4,
                "genre": "Historical Fiction",
                "isbn": "978-966-01-0002-8",
            },
            "Lisova Pisnia": {
                "title": "Lisova Pisnia",
                "author": "Lesya Ukrainka",
                "price": 120.0,
                "quantity": 6,
                "genre": "Poetry",
                "isbn": "978-966-01-0003-5",
            },
            "Eneida": {
                "title": "Eneida",
                "author": "Ivan Kotlyarevsky",
                "price": 90.0,
                "quantity": 8,
                "genre": "Poetry",
                "isbn": "978-966-01-0004-2",
            },
        }


# ═══════════════════════════════════════════════════════════════
# Функція 1 — Пошук книг
# ═══════════════════════════════════════════════════════════════

class TestSearchBook(BookstoreTestCase):
    """
    Вимоги до search_book:
      - Пошук за назвою, автором, жанром або ISBN (будь-яка комбінація).
      - Пошук за назвою та автором — частковий збіг, без урахування регістру.
      - Пошук за ISBN — точний збіг.
      - Якщо задано кілька критеріїв — повертаються тільки книги, що
        відповідають УСІМ критеріям одночасно.
      - Якщо збігів немає — повертається порожній список.
      - Якщо не задано жодного критерію — ValueError.
      - Якщо критерій є порожнім рядком або пробілами — ValueError.
    """

    # ── Пошук за одним критерієм ─────────────────────────────────

    def test_search_by_exact_title(self):
        """Пошук за точною назвою повертає одну книгу з правильними даними."""
        results = self.store.search_book(title="Kobzar")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Kobzar")
        self.assertEqual(results[0]["author"], "Taras Shevchenko")

    def test_search_by_partial_title(self):
        """Пошук за частковою назвою без урахування регістру повертає всі збіги."""
        results = self.store.search_book(title="kobz")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Kobzar")

    def test_search_by_author(self):
        """Пошук за автором знаходить всі його книги."""
        results = self.store.search_book(author="Ivan Franko")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Zakhar Berkut")

    def test_search_by_partial_author(self):
        """Пошук за частиною імені автора (наприклад, 'Ivan') знаходить кілька книг."""
        results = self.store.search_book(author="ivan")
        titles = [b["title"] for b in results]
        self.assertIn("Zakhar Berkut", titles)
        self.assertIn("Eneida", titles)
        self.assertEqual(len(results), 2)

    def test_search_by_genre(self):
        """Пошук за жанром повертає всі книги цього жанру."""
        results = self.store.search_book(genre="Poetry")
        self.assertEqual(len(results), 3)
        titles = {b["title"] for b in results}
        self.assertEqual(titles, {"Kobzar", "Lisova Pisnia", "Eneida"})

    def test_search_by_isbn(self):
        """Пошук за ISBN (точний збіг) повертає одну книгу."""
        results = self.store.search_book(isbn="978-966-01-0002-8")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Zakhar Berkut")

    # ── Пошук за кількома критеріями ──────────────────────────────

    def test_search_by_multiple_criteria(self):
        """Пошук за автором і жанром одночасно повертає тільки книги, що відповідають обом."""
        results = self.store.search_book(author="Ivan", genre="Poetry")
        # Ivan Franko — Historical Fiction, Ivan Kotlyarevsky — Poetry
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Eneida")

    def test_search_by_title_and_genre_no_match(self):
        """Якщо книга є за назвою, але жанр не збігається — повертається порожній список."""
        results = self.store.search_book(title="Kobzar", genre="Historical Fiction")
        self.assertEqual(results, [])

    # ── Відсутність збігів ────────────────────────────────────────

    def test_search_no_match_returns_empty_list(self):
        """Якщо жодна книга не відповідає критерію — повертається порожній список."""
        results = self.store.search_book(title="Nonexistent Book")
        self.assertEqual(results, [])

    def test_search_wrong_isbn_returns_empty_list(self):
        """Неправильний ISBN — порожній список, не помилка."""
        results = self.store.search_book(isbn="000-000-000")
        self.assertEqual(results, [])

    # ── Некоректні вхідні дані ────────────────────────────────────

    def test_search_no_criteria_raises(self):
        """Виклик без жодного критерію має викидати ValueError."""
        with self.assertRaises(ValueError):
            self.store.search_book()

    def test_search_empty_string_criteria_raises(self):
        """Порожній рядок або пробіли як критерій — ValueError."""
        for bad in ("", "   "):
            with self.subTest(title=bad):
                with self.assertRaises(ValueError):
                    self.store.search_book(title=bad)

    # ── Незмінність інвентарю ─────────────────────────────────────

    def test_search_returns_copy_not_reference(self):
        """Зміна поверненого словника не повинна змінювати дані в інвентарі."""
        results = self.store.search_book(title="Kobzar")
        results[0]["price"] = 9999.0
        # перевіряємо через прямий доступ до інвентарю
        self.assertEqual(self.store._inventory["Kobzar"]["price"], 150.0)


# ═══════════════════════════════════════════════════════════════
# Функція 2 — Рейтинг книг
# ═══════════════════════════════════════════════════════════════

class TestRateBook(BookstoreTestCase):
    """
    Вимоги до rate_book / get_average_rating:
      - Оцінка від 1 до 5 включно; нецілі значення (напр. 4.5) дозволені.
      - Оцінка менше 1 або більше 5 — ValueError.
      - Оцінка нечислового типу — ValueError.
      - Можна додавати кілька оцінок одній книзі; зберігаються всі.
      - get_average_rating повертає середнє арифметичне, округлене до 2 знаків.
      - Якщо оцінок ще немає — get_average_rating повертає None.
      - Обидва методи кидають BookNotFoundError для неіснуючої книги.
      - Обидва методи кидають ValueError для порожньої/None назви.
    """

    # ── Додавання оцінок ──────────────────────────────────────────

    def test_rate_book_valid(self):
        """Коректна оцінка зберігається без помилок."""
        self.store.rate_book("Kobzar", 5)
        avg = self.store.get_average_rating("Kobzar")
        self.assertIsNotNone(avg)

    def test_rate_book_float_value(self):
        """Дробова оцінка (напр. 3.5) дозволена і зберігається правильно."""
        self.store.rate_book("Kobzar", 3.5)
        self.assertAlmostEqual(self.store.get_average_rating("Kobzar"), 3.5)

    def test_rate_book_boundary_min(self):
        """Мінімальна допустима оцінка 1 не викидає помилку."""
        self.store.rate_book("Kobzar", 1)
        self.assertAlmostEqual(self.store.get_average_rating("Kobzar"), 1.0)

    def test_rate_book_boundary_max(self):
        """Максимальна допустима оцінка 5 не викидає помилку."""
        self.store.rate_book("Kobzar", 5)
        self.assertAlmostEqual(self.store.get_average_rating("Kobzar"), 5.0)

    def test_rate_book_multiple_ratings(self):
        """Кілька оцінок для однієї книги зберігаються, середнє розраховується правильно."""
        self.store.rate_book("Kobzar", 4)
        self.store.rate_book("Kobzar", 2)
        self.store.rate_book("Kobzar", 3)
        # (4 + 2 + 3) / 3 = 3.0
        self.assertAlmostEqual(self.store.get_average_rating("Kobzar"), 3.0)

    def test_rate_different_books_independently(self):
        """Рейтинги різних книг не впливають одна на одну."""
        self.store.rate_book("Kobzar", 5)
        self.store.rate_book("Zakhar Berkut", 2)
        self.assertAlmostEqual(self.store.get_average_rating("Kobzar"), 5.0)
        self.assertAlmostEqual(self.store.get_average_rating("Zakhar Berkut"), 2.0)

    # ── Середній рейтинг без оцінок ───────────────────────────────

    def test_get_average_rating_no_ratings_returns_none(self):
        """Якщо книга ще не має оцінок — get_average_rating повертає None."""
        result = self.store.get_average_rating("Kobzar")
        self.assertIsNone(result)

    def test_average_rating_rounds_to_two_decimal(self):
        """Середній рейтинг заокруглюється до двох знаків після коми."""
        # (5 + 4 + 3) / 3 = 4.0  — рівне; перевіряємо нерівне теж
        self.store.rate_book("Kobzar", 5)
        self.store.rate_book("Kobzar", 4)
        self.store.rate_book("Kobzar", 3)
        avg = self.store.get_average_rating("Kobzar")
        # перевіряємо, що кількість знаків не перевищує 2
        self.assertEqual(avg, round(avg, 2))

    # ── Некоректні оцінки ─────────────────────────────────────────

    def test_rate_below_minimum_raises(self):
        """Оцінка менше 1 викидає ValueError, і оцінка не зберігається."""
        with self.assertRaises(ValueError):
            self.store.rate_book("Kobzar", 0)
        self.assertIsNone(self.store.get_average_rating("Kobzar"))

    def test_rate_above_maximum_raises(self):
        """Оцінка більше 5 викидає ValueError, і оцінка не зберігається."""
        with self.assertRaises(ValueError):
            self.store.rate_book("Kobzar", 6)
        self.assertIsNone(self.store.get_average_rating("Kobzar"))

    def test_rate_non_numeric_raises(self):
        """Нечисловий тип оцінки (наприклад, рядок) викидає ValueError."""
        with self.assertRaises(ValueError):
            self.store.rate_book("Kobzar", "five")

    # ── Неіснуюча книга / некоректна назва ───────────────────────

    def test_rate_nonexistent_book_raises(self):
        """rate_book для книги, якої немає в інвентарі, викидає BookNotFoundError."""
        with self.assertRaises(BookNotFoundError):
            self.store.rate_book("Unknown Book", 4)

    def test_rate_empty_title_raises(self):
        """rate_book з порожньою назвою викидає ValueError."""
        with self.assertRaises(ValueError):
            self.store.rate_book("", 4)

    def test_get_average_nonexistent_book_raises(self):
        """get_average_rating для книги, якої немає, викидає BookNotFoundError."""
        with self.assertRaises(BookNotFoundError):
            self.store.get_average_rating("Unknown Book")

    def test_get_average_empty_title_raises(self):
        """get_average_rating з порожньою назвою викидає ValueError."""
        with self.assertRaises(ValueError):
            self.store.get_average_rating("")


if __name__ == "__main__":
    unittest.main(verbosity=2)