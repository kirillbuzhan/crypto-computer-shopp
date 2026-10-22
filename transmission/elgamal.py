"""Шифр Эль-Гамаля.

Ключи:
    p — большое простое число, g — первообразный корень по модулю p,
    x — секретный ключ (1 < x < p − 1), y = gˣ mod p — открытый ключ.
    Открытый ключ — тройка (p, g, y), секретный — x.

Шифрование символа с кодом M (0 ≤ M < p):
    выбирается случайный сеансовый ключ k, НОД(k, p − 1) = 1,
    a = gᵏ mod p,  b = yᵏ·M mod p — шифртекст — пара (a, b).

Расшифрование:
    s = aˣ mod p (= gˣᵏ = yᵏ — общий секрет),
    M = b·s⁻¹ mod p.

Каждый символ сообщения шифруется отдельно по своему коду Unicode,
поэтому p должно быть больше кода любого символа сообщения. Из-за
случайного k одинаковые символы дают разные пары (a, b) — шифр
вероятностный, а шифртекст вдвое длиннее открытого текста.

Простое p либо вводится вручную (до 10⁹, проверка пробным делением),
либо генерируется заданной битности с доказательством простоты по
критерию Поклингтона (algebra.pocklington). Сервер ничего не хранит:
сертификат простоты отдаётся клиенту вместе с ключами и присылается
обратно при шифровании, а сервер его перепроверяет. Из сертификата же
берётся разложение p − 1 — без него нельзя проверить, что g —
первообразный корень.
"""

import random
import re
from math import gcd

from algebra.congruences import factorize, factorization_text
from algebra.diophantine import extended_euclid, is_prime
from algebra.pocklington import MAX_BITS, MIN_BITS, chain_factors, generate_prime, parse_chain, verify_chain


MAX_PRIME = 10 ** 9
MIN_GENERATED_PRIME = 1000

PAIR_PATTERN = re.compile(r"\((\d+),\s*(\d+)\)")


def is_primitive_root(g: int, p: int, factors: list[tuple[int, int]] | None = None) -> bool:
    """g — первообразный корень по модулю простого p ⇔ g^((p−1)/q) ≢ 1 для всех простых q | p − 1."""
    if not 1 < g < p:
        return False
    factors = factors if factors is not None else factorize(p - 1)
    return all(pow(g, (p - 1) // q, p) != 1 for q, _ in factors)


def smallest_primitive_root(p: int, factors: list[tuple[int, int]] | None = None) -> int:
    factors = factors if factors is not None else factorize(p - 1)
    return next(g for g in range(2, p) if is_primitive_root(g, p, factors))


def generate_large_keys(bits: int, rng: random.Random | None = None) -> dict:
    """Ключи с bits-битным простым p, простота которого доказана по Поклингтону."""
    if not MIN_BITS <= bits <= MAX_BITS:
        raise ValueError(f"Размер p должен быть от {MIN_BITS} до {MAX_BITS} бит")
    rng = rng or random.SystemRandom()

    prime = generate_prime(bits, rng)
    p, factors = prime["p"], prime["factors"]

    while True:
        g = rng.randint(2, p - 2)
        if is_primitive_root(g, p, factors):
            break
    x = rng.randint(2, p - 2)
    return {"p": p, "g": g, "x": x, "bits": bits, "steps": len(prime["chain"]), "certificate": prime["chain"]}


def mod_inverse(value: int, p: int) -> int:
    return extended_euclid(value % p, p)["s"] % p


def generate_keys(message: str, rng: random.Random | None = None) -> dict:
    """Случайные учебные ключи: простое p больше кода любого символа сообщения."""
    rng = rng or random.SystemRandom()
    low = max(MIN_GENERATED_PRIME, max((ord(char) for char in message), default=0) + 1)
    while True:
        p = rng.randint(low, low * 3)
        if is_prime(p):
            break
    while True:
        g = rng.randint(2, p - 2)
        if is_primitive_root(g, p):
            break
    x = rng.randint(2, p - 2)
    return {"p": p, "g": g, "x": x}


class ElGamalCoder:
    """Посимвольное шифрование и расшифрование по схеме Эль-Гамаля."""

    def __init__(self, p: int, g: int, x: int, certificate: list | None = None):
        """certificate — сертификат Поклингтона для p (как его вернул generate_large_keys,
        большие числа могут быть строками); обязателен для p > MAX_PRIME."""
        self.chain = None
        if certificate and p > MAX_PRIME:
            chain = parse_chain(certificate)
            if chain[-1]["p"] != p or not verify_chain(chain):
                raise ValueError("Сертификат простоты не подходит к p: сгенерируйте ключи заново")
            self.chain = chain
            self.p_minus_1_factors = chain_factors(chain)
        elif p > MAX_PRIME:
            raise ValueError(
                f"p больше {MAX_PRIME} можно только сгенерировать кнопкой «Большое простое»: "
                "для такого p нужен сертификат Поклингтона и разложение p − 1"
            )
        elif p < 3 or not is_prime(p):
            raise ValueError(f"p = {p} должно быть простым числом от 3 до {MAX_PRIME}")
        else:
            self.p_minus_1_factors = factorize(p - 1)

        if not is_primitive_root(g, p, self.p_minus_1_factors):
            raise ValueError(
                f"g = {g} не первообразный корень по модулю {p} "
                f"(например, подойдёт g = {smallest_primitive_root(p, self.p_minus_1_factors)})"
            )
        if not 1 < x < p - 1:
            raise ValueError(f"Секретный ключ x должен быть в диапазоне 1 < x < {p - 1}")

        self.p = p
        self.g = g
        self.x = x
        self.y = pow(g, x, p)

    @property
    def keys(self) -> dict:
        return {"p": self.p, "g": self.g, "x": self.x, "y": self.y}

    def check_message(self, message: str) -> None:
        for char in message:
            if ord(char) >= self.p:
                raise ValueError(
                    f"Код символа «{char}» = {ord(char)} не меньше p = {self.p}: "
                    "выберите p больше или сгенерируйте ключи заново"
                )

    def random_session_key(self, rng: random.Random) -> int:
        while True:
            k = rng.randint(2, self.p - 2)
            if gcd(k, self.p - 1) == 1:
                return k

    def encode(self, message: str, rng: random.Random | None = None) -> dict:
        self.check_message(message)
        rng = rng or random.SystemRandom()

        blocks = []
        for char in message:
            m = ord(char)
            k = self.random_session_key(rng)
            a = pow(self.g, k, self.p)
            y_k = pow(self.y, k, self.p)
            b = y_k * m % self.p
            blocks.append({"char": char, "m": m, "k": k, "a": a, "y_k": y_k, "b": b})

        encoded = " ".join(f"({block['a']},{block['b']})" for block in blocks)
        return {"encoded": encoded, "blocks": blocks}

    def decode(self, encoded: str) -> dict:
        blocks = []
        for a_text, b_text in PAIR_PATTERN.findall(encoded):
            a, b = int(a_text), int(b_text)
            s = pow(a, self.x, self.p)
            s_inv = mod_inverse(s, self.p)
            m = b * s_inv % self.p
            blocks.append({"a": a, "b": b, "s": s, "s_inv": s_inv, "m": m, "char": chr(m)})

        return {"decoded": "".join(block["char"] for block in blocks), "blocks": blocks}

    def certificate_sections(self) -> list[dict]:
        """Сертификат Поклингтона: цепочка простых от маленького до p."""
        if not self.chain:
            return []

        rows = []
        for index, step in enumerate(self.chain):
            if step["method"] == "trial":
                rows.append([index, step["bits"], step["p"], "—", "—", "—",
                             "пробное деление до √n"])
            else:
                rows.append([
                    index, step["bits"], step["p"],
                    f"{step['q']} (шаг {index - 1})",
                    factorization_text(step["r_factors"]),
                    step["a"],
                    f"{step['a']}^(n−1) ≡ 1; НОД({step['a']}^R − 1, n) = 1; q² > n "
                    f"(кандидатов: {step['attempts']})",
                ])

        explanation = [
            "Критерий Поклингтона: пусть n − 1 = F·R, разложение F известно и F > √n. "
            "Если для каждого простого q | F есть a: a^(n−1) ≡ 1 (mod n) и НОД(a^((n−1)/q) − 1, n) = 1, "
            "то n простое.",
            "Почему: для любого простого делителя r числа n порядок a по модулю r делит n − 1, "
            "но не делит (n − 1)/q, поэтому F | r − 1 и r > F > √n — значит, n не имеет "
            "делителей ≤ √n, т.е. простое.",
            "Генерация: начинаем с маленького простого (пробное деление), затем строим n = R·q + 1, "
            "где q — уже доказанное простое (F = q), R — чётное произведение малых простых и q² > n. "
            "Кандидаты, не прошедшие a^(n−1) ≡ 1, отбрасываются (они составные по Ферма).",
            "Так как R состоит из малых простых, разложение p − 1 = R·q известно полностью — "
            "по нему проверяется, что g — первообразный корень.",
        ]

        return [
            {"type": "steps", "title": "Генерация p: критерий Поклингтона", "items": explanation},
            {
                "type": "table", "title": "Сертификат простоты p (каждый шаг опирается на предыдущий)",
                "columns": ["шаг", "бит", "n", "q = F", "R", "a", "проверка"],
                "rows": rows, "highlight": [len(rows) - 1],
            },
        ]

    def sections(self, encode_result: dict, decode_result: dict) -> list[dict]:
        """Пошаговое описание для визуализации (формат секций учебных разделов)."""
        p, g, x, y = self.p, self.g, self.x, self.y
        factors = factorization_text(self.p_minus_1_factors)
        proof = (
            f"простота доказана по критерию Поклингтона за {len(self.chain)} шаг(ов) "
            "(см. сертификат ниже)"
            if self.chain else "простота проверена пробным делением"
        )

        key_steps = [
            f"Простое p = {p} ({p.bit_length()} бит, {proof}); p − 1 = {factors}.",
            f"g = {g} — первообразный корень: g^((p−1)/q) ≢ 1 (mod p) для каждого простого q | p − 1, "
            "поэтому степени g пробегают все ненулевые вычеты.",
            f"Секретный ключ x = {x}; открытый ключ y = gˣ mod p = {g}^{x} mod {p} = {y}.",
            "Для каждого символа берётся свой случайный сеансовый ключ k (НОД(k, p − 1) = 1): "
            "a = gᵏ mod p, b = yᵏ·M mod p. Поэтому одинаковые символы шифруются по-разному.",
            "Получатель вычисляет s = aˣ = gᵏˣ = yᵏ (mod p) и снимает «маску»: M = b·s⁻¹ mod p. "
            "Без x найти s — задача Диффи–Хеллмана (дискретный логарифм).",
        ]

        encrypt_rows = [
            [index, block["char"], block["m"], block["k"],
             f"{g}^{block['k']} = {block['a']}",
             f"{block['y_k']}·{block['m']} = {block['b']}"]
            for index, block in enumerate(encode_result["blocks"])
        ]
        decrypt_rows = [
            [index, f"({block['a']}, {block['b']})",
             f"{block['a']}^{x} = {block['s']}", block["s_inv"],
             f"{block['b']}·{block['s_inv']} = {block['m']}", block["char"]]
            for index, block in enumerate(decode_result["blocks"])
        ]

        source = "".join(block["char"] for block in encode_result["blocks"])
        ok = decode_result["decoded"] == source

        return [
            {
                "type": "table", "title": "Ключи",
                "columns": ["параметр", "значение", "доступ"],
                "rows": [
                    ["p — простой модуль", p, "открытый"],
                    ["g — первообразный корень", g, "открытый"],
                    ["y = gˣ mod p", y, "открытый"],
                    ["x — секретный ключ", x, "только у получателя"],
                ],
                "highlight": [3],
            },
            {"type": "steps", "title": "Как это работает", "items": key_steps},
            *self.certificate_sections(),
            {
                "type": "table", "title": "Шифрование (mod p): M — код символа, k — случайный сеансовый ключ",
                "columns": ["#", "символ", "M", "k", "a = gᵏ", "b = yᵏ·M"],
                "rows": encrypt_rows, "highlight": [],
            },
            {
                "type": "table", "title": "Расшифрование (mod p): s = aˣ, M = b·s⁻¹",
                "columns": ["#", "(a, b)", "s = aˣ", "s⁻¹", "M = b·s⁻¹", "символ"],
                "rows": decrypt_rows, "highlight": [],
            },
            {
                "type": "result", "kind": "ok" if ok else "fail",
                "title": "Сообщение восстановлено" if ok else "Расшифровка не совпала",
                "text": f"Символов: {len(source)} → пар (a, b): {len(encode_result['blocks'])} → «{decode_result['decoded']}»",
            },
        ]
