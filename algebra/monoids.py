"""Примеры моноидов.

Моноид — это тройка (M, ∘, e):
    * M — множество (носитель);
    * ∘ — бинарная операция M × M → M, которая ассоциативна:
          (a ∘ b) ∘ c = a ∘ (b ∘ c);
    * e — нейтральный элемент: e ∘ a = a ∘ e = a для любого a из M.

Коммутативность (a ∘ b = b ∘ a) не требуется — среди примеров есть
и коммутативные, и некоммутативные моноиды.

Каждый пример умеет разобрать элементы из строки, ввести операцию,
вернуть нейтральный элемент и отформатировать значение для вывода.
Общая логика (свёртка, проверка аксиом) лежит в MonoidDemo.
"""

from typing import Any


MAX_ELEMENTS = 10
EMPTY_STRING_MARK = "ε"


class Monoid:
    """Базовый класс примера моноида."""

    key = ""
    title = ""
    commutative = False

    def parse(self, raw: str) -> Any:
        """Разобрать один элемент из введённой строки (ValueError — при ошибке)."""
        raise NotImplementedError

    def combine(self, left: Any, right: Any) -> Any:
        """Операция моноида."""
        raise NotImplementedError

    def identity(self, elements: list) -> Any:
        """Нейтральный элемент (для некоторых моноидов зависит от размерности элементов)."""
        raise NotImplementedError

    def format(self, value: Any) -> str:
        """Представить элемент в виде строки для отображения."""
        return str(value)

    def validate(self, elements: list) -> None:
        """Дополнительная проверка набора элементов (например, одинаковая длина)."""


class StringConcatMonoid(Monoid):
    """(Σ*, конкатенация, ε) — свободный моноид слов над алфавитом.

    Именно в нём живут закодированные сообщения: кодирование префиксным
    кодом — гомоморфизм моноидов φ(uv) = φ(u)φ(v).
    """

    key = "strings"
    title = "Строки и конкатенация"

    def parse(self, raw: str) -> str:
        return "" if raw == EMPTY_STRING_MARK else raw

    def combine(self, left: str, right: str) -> str:
        return left + right

    def identity(self, elements: list) -> str:
        return ""

    def format(self, value: str) -> str:
        return f"«{value}»" if value else EMPTY_STRING_MARK


class NaturalAdditionMonoid(Monoid):
    """(ℕ₀, +, 0) — натуральные числа с нулём по сложению."""

    key = "addition"
    title = "Натуральные числа и сложение"
    commutative = True

    def parse(self, raw: str) -> int:
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"«{raw}» — не целое число") from None
        if value < 0:
            raise ValueError(f"{value} — отрицательное число, а носитель — ℕ₀")
        return value

    def combine(self, left: int, right: int) -> int:
        return left + right

    def identity(self, elements: list) -> int:
        return 0


class ModularMultiplicationMonoid(Monoid):
    """(ℤₙ, · mod n, 1) — остатки по модулю n с умножением.

    Это моноид, но, как правило, не группа: у 0 (и у делителей нуля)
    нет обратного элемента.
    """

    key = "modular"
    title = "Умножение по модулю n"
    commutative = True

    MIN_MODULUS = 2
    MAX_MODULUS = 100
    MAX_CAYLEY_MODULUS = 12

    def __init__(self, modulus: int = 10):
        if not self.MIN_MODULUS <= modulus <= self.MAX_MODULUS:
            raise ValueError(f"Модуль n должен быть от {self.MIN_MODULUS} до {self.MAX_MODULUS}")
        self.modulus = modulus

    def parse(self, raw: str) -> int:
        try:
            value = int(raw)
        except ValueError:
            raise ValueError(f"«{raw}» — не целое число") from None
        return value % self.modulus

    def combine(self, left: int, right: int) -> int:
        return (left * right) % self.modulus

    def identity(self, elements: list) -> int:
        return 1 % self.modulus

    def cayley_table(self) -> list[list[int]] | None:
        """Таблица Кэли (таблица умножения) — только для небольших n."""
        if self.modulus > self.MAX_CAYLEY_MODULUS:
            return None
        return [[self.combine(a, b) for b in range(self.modulus)] for a in range(self.modulus)]


class BitXorMonoid(Monoid):
    """({0,1}ᵏ, ⊕, 00…0) — битовые векторы длины k с побитовым XOR.

    Основа линейных кодов (Хэмминга, Адамара): сумма кодовых слов — снова
    кодовое слово, а ошибка канала — это XOR с вектором ошибки.
    """

    key = "xor"
    title = "Битовые векторы и XOR"
    commutative = True

    MAX_LENGTH = 32

    def parse(self, raw: str) -> str:
        if not raw or any(bit not in "01" for bit in raw):
            raise ValueError(f"«{raw}» — не битовая строка (допустимы только 0 и 1)")
        if len(raw) > self.MAX_LENGTH:
            raise ValueError(f"Длина вектора не больше {self.MAX_LENGTH} бит")
        return raw

    def validate(self, elements: list) -> None:
        lengths = {len(element) for element in elements}
        if len(lengths) > 1:
            raise ValueError("Все битовые векторы должны быть одной длины k")

    def combine(self, left: str, right: str) -> str:
        return "".join("1" if a != b else "0" for a, b in zip(left, right))

    def identity(self, elements: list) -> str:
        length = len(elements[0]) if elements else 4
        return "0" * length


class MatrixMultiplicationMonoid(Monoid):
    """(M₂(ℤ), ·, E) — целочисленные матрицы 2×2 с умножением.

    Классический некоммутативный моноид: AB ≠ BA в общем случае.
    """

    key = "matrices"
    title = "Матрицы 2×2 и умножение"

    def parse(self, raw: str) -> tuple:
        rows = [row.split() for row in raw.split("/")]
        if len(rows) != 2 or any(len(row) != 2 for row in rows):
            raise ValueError(f"«{raw}» — матрицу 2×2 записывают как «a b / c d»")
        try:
            return tuple(tuple(int(value) for value in row) for row in rows)
        except ValueError:
            raise ValueError(f"«{raw}» — элементы матрицы должны быть целыми числами") from None

    def combine(self, left: tuple, right: tuple) -> tuple:
        return tuple(
            tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2))
            for i in range(2)
        )

    def identity(self, elements: list) -> tuple:
        return ((1, 0), (0, 1))

    def format(self, value: tuple) -> str:
        return " / ".join(" ".join(str(item) for item in row) for row in value)


MONOID_CLASSES = {
    cls.key: cls
    for cls in (
        StringConcatMonoid,
        NaturalAdditionMonoid,
        ModularMultiplicationMonoid,
        BitXorMonoid,
        MatrixMultiplicationMonoid,
    )
}


def create_monoid(key: str, modulus: int | None = None) -> Monoid:
    if key not in MONOID_CLASSES:
        raise ValueError(f"Неизвестный пример моноида: {key}")
    if key == ModularMultiplicationMonoid.key:
        return ModularMultiplicationMonoid(modulus if modulus is not None else 10)
    return MONOID_CLASSES[key]()


class MonoidDemo:
    """Свёртка элементов и пошаговая проверка аксиом моноида."""

    def __init__(self, monoid: Monoid):
        self.monoid = monoid

    def parse_elements(self, raw_elements: list[str]) -> list:
        if not raw_elements:
            raise ValueError("Введите хотя бы один элемент")
        if len(raw_elements) > MAX_ELEMENTS:
            raise ValueError(f"Не больше {MAX_ELEMENTS} элементов")

        elements = [self.monoid.parse(raw) for raw in raw_elements]
        self.monoid.validate(elements)
        return elements

    def run(self, raw_elements: list[str]) -> dict:
        monoid = self.monoid
        elements = self.parse_elements(raw_elements)
        identity = monoid.identity(elements)
        fmt = monoid.format

        # Свёртка начинается с нейтрального элемента: e ∘ a₁ ∘ a₂ ∘ … ∘ aₙ.
        fold_steps = []
        accumulator = identity
        for element in elements:
            result = monoid.combine(accumulator, element)
            fold_steps.append({"left": fmt(accumulator), "right": fmt(element), "result": fmt(result)})
            accumulator = result

        identity_checks = []
        for element in elements:
            left = monoid.combine(identity, element)
            right = monoid.combine(element, identity)
            identity_checks.append({
                "element": fmt(element),
                "left": fmt(left),
                "right": fmt(right),
                "holds": left == element and right == element,
            })

        associativity = None
        if len(elements) >= 3:
            a, b, c = elements[:3]
            ab = monoid.combine(a, b)
            bc = monoid.combine(b, c)
            ab_c = monoid.combine(ab, c)
            a_bc = monoid.combine(a, bc)
            associativity = {
                "a": fmt(a), "b": fmt(b), "c": fmt(c),
                "ab": fmt(ab), "bc": fmt(bc),
                "ab_c": fmt(ab_c), "a_bc": fmt(a_bc),
                "holds": ab_c == a_bc,
            }

        commutativity = None
        if len(elements) >= 2:
            a, b = elements[:2]
            ab = monoid.combine(a, b)
            ba = monoid.combine(b, a)
            commutativity = {
                "a": fmt(a), "b": fmt(b),
                "ab": fmt(ab), "ba": fmt(ba),
                "holds": ab == ba,
            }

        result = {
            "example": monoid.key,
            "title": monoid.title,
            "commutative": monoid.commutative,
            "elements": [fmt(element) for element in elements],
            "identity": fmt(identity),
            "fold_steps": fold_steps,
            "fold_result": fmt(accumulator),
            "identity_checks": identity_checks,
            "associativity": associativity,
            "commutativity": commutativity,
            "cayley": None,
        }

        if isinstance(monoid, ModularMultiplicationMonoid):
            result["modulus"] = monoid.modulus
            result["cayley"] = monoid.cayley_table()

        return result
