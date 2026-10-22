"""Примеры сравнений по модулю.

a ≡ b (mod m) ⇔ m | (a − b). Сравнения можно складывать, вычитать,
умножать и возводить в степень — это «арифметика остатков», на которой
построена вся асимметричная криптография. Пять примеров:

    1. power       — быстрое возведение в степень aᵏ mod m (бинарный метод);
    2. euler       — теорема Эйлера / малая теорема Ферма: понижение показателя;
    3. crt         — китайская теорема об остатках для системы из трёх сравнений;
    4. quadratic   — квадратичное сравнение x² ≡ a (mod p): критерий Эйлера и корни;
    5. divisibility — признаки делимости: N mod m через остатки степеней 10.

Формат ответа тот же, что у диофантовых уравнений: уравнение и список
секций (steps / table / result), которые фронтенд рисует одинаково.
"""

from math import gcd

from algebra.diophantine import MAX_ABS_VALUE, extended_euclid, euclid_section, get_int, is_prime, num


def factorize(value: int) -> list[tuple[int, int]]:
    """Разложение на простые множители пробным делением: [(p, степень), ...]."""
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        power = 0
        while value % divisor == 0:
            value //= divisor
            power += 1
        if power:
            factors.append((divisor, power))
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append((value, 1))
    return factors


def factorization_text(factors: list[tuple[int, int]]) -> str:
    sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return " · ".join(f"{p}{str(e).translate(sup) if e > 1 else ''}" for p, e in factors)


def base_text(a: int) -> str:
    """Основание степени: отрицательное — в скобках, чтобы (−3)ᵏ не путать с −3ᵏ."""
    return f"({num(a)})" if a < 0 else num(a)


def euler_phi(factors: list[tuple[int, int]]) -> int:
    phi = 1
    for p, e in factors:
        phi *= p ** (e - 1) * (p - 1)
    return phi


# --- 1. Быстрое возведение в степень ---

MAX_EXPONENT = 10 ** 30


def solve_power(params: dict) -> dict:
    a = get_int(params, "a", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    k = get_int(params, "k", 0, MAX_EXPONENT)
    m = get_int(params, "m", 2, MAX_ABS_VALUE)

    equation = f"{base_text(a)}^{k} mod {m} = ?"
    bits = bin(k)[2:]
    base = a % m

    rows = []
    highlight = []
    accumulator = 1 % m
    square = base
    # Идём по битам k справа налево: на шаге i держим a^(2ⁱ) mod m
    # и домножаем результат, если i-й бит равен 1.
    for index, bit in enumerate(reversed(bits)):
        if bit == "1":
            accumulator = (accumulator * square) % m
            highlight.append(index)
        rows.append([index, bit, f"a^{2 ** index}" if index < 20 else f"a^(2^{index})", square, accumulator if bit == "1" else "—"])
        square = (square * square) % m

    multiplications = (len(bits) - 1) + bits.count("1")
    steps = [
        f"Приводим основание: {num(a)} ≡ {base} (mod {m}).",
        f"Записываем показатель в двоичной системе: {k} = {bits}₂ ({len(bits)} бит).",
        "Последовательно возводим в квадрат: a, a², a⁴, a⁸, … (mod m) — каждый следующий остаток = квадрат предыдущего.",
        "Перемножаем по модулю те степени, которым соответствует бит 1.",
        f"Итого около {multiplications} умножений вместо {k - 1 if k > 1 else 0} при наивном способе.",
    ]

    result = pow(a, k, m)
    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table",
                "title": "Бинарное возведение в степень (биты показателя справа налево; выделены биты 1)",
                "columns": ["i", "бит", "степень", "a^(2ⁱ) mod m", "результат"],
                "rows": rows,
                "highlight": highlight,
            },
            {"type": "result", "kind": "ok", "title": "Ответ", "text": f"{base_text(a)}^{k} ≡ {result} (mod {m})"},
        ],
    }


# --- 2. Теорема Эйлера и малая теорема Ферма ---

def solve_euler(params: dict) -> dict:
    a = get_int(params, "a", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    k = get_int(params, "k", 0, MAX_EXPONENT)
    m = get_int(params, "m", 2, MAX_ABS_VALUE)

    equation = f"{base_text(a)}^{k} mod {m} = ?"
    factors = factorize(m)
    phi = euler_phi(factors)
    prime = len(factors) == 1 and factors[0][1] == 1

    factor_rows = [[p, e, f"{p}^{e - 1}·({p} − 1)", p ** (e - 1) * (p - 1)] for p, e in factors]
    steps = [
        f"Раскладываем модуль: {m} = {factorization_text(factors)}.",
        f"Функция Эйлера φ(m) = ∏ pᵉ⁻¹(p − 1) = {phi} — столько чисел от 1 до m взаимно просты с m.",
    ]
    if prime:
        steps.append(f"m = {m} — простое, поэтому φ(m) = m − 1 и это частный случай — малая теорема Ферма: a^{m - 1} ≡ 1 (mod {m}).")

    sections = [{"type": "steps", "title": "Ход решения", "items": steps}]
    sections.append({
        "type": "table", "title": "Вычисление φ(m)",
        "columns": ["p", "степень e", "вклад", "значение"],
        "rows": factor_rows, "highlight": [],
    })

    g = gcd(a, m)
    direct = pow(a, k, m)
    if g != 1:
        steps.append(f"НОД({num(a)}, {m}) = {g} ≠ 1 — теорема Эйлера неприменима, считаем напрямую.")
        sections.append({
            "type": "result", "kind": "info", "title": f"Теорема неприменима: НОД = {g}",
            "text": f"{base_text(a)}^{k} ≡ {direct} (mod {m}) (вычислено напрямую)",
        })
        return {"equation": equation, "sections": sections}

    reduced = k % phi
    check = pow(a, phi, m)
    steps += [
        f"НОД({num(a)}, {m}) = 1, значит по теореме Эйлера a^φ(m) ≡ 1: {base_text(a)}^{phi} mod {m} = {check}.",
        f"Поэтому показатель можно взять по модулю φ(m): {k} = {k // phi}·{phi} + {reduced}.",
        f"{base_text(a)}^{k} = ({base_text(a)}^{phi})^{k // phi} · {base_text(a)}^{reduced} ≡ 1^{k // phi} · {base_text(a)}^{reduced} ≡ {pow(a, reduced, m)} (mod {m}).",
    ]
    sections.append({
        "type": "result", "kind": "ok" if pow(a, reduced, m) == direct else "fail",
        "title": f"Показатель понижен: {k} → {reduced}",
        "text": f"{base_text(a)}^{k} ≡ {base_text(a)}^{reduced} ≡ {direct} (mod {m})",
    })
    return {"equation": equation, "sections": sections}


# --- 3. Китайская теорема об остатках ---

MAX_CRT_MODULUS = 10 ** 6


def solve_crt(params: dict) -> dict:
    system = []
    for index in (1, 2, 3):
        r = get_int(params, f"r{index}", -MAX_ABS_VALUE, MAX_ABS_VALUE, f"r{index}")
        m = get_int(params, f"m{index}", 2, MAX_CRT_MODULUS, f"m{index}")
        system.append((r % m, m))

    equation = ",  ".join(f"x ≡ {r} (mod {m})" for r, m in system)
    steps = ["Приводим остатки: " + ";  ".join(f"x ≡ {r} (mod {m})" for r, m in system) + "."]

    for i in range(3):
        for j in range(i + 1, 3):
            g = gcd(system[i][1], system[j][1])
            if g != 1:
                return {
                    "equation": equation,
                    "sections": [
                        {"type": "steps", "title": "Ход решения", "items": steps},
                        {
                            "type": "result", "kind": "fail", "title": "Модули не взаимно просты",
                            "text": f"НОД(m{i + 1}, m{j + 1}) = НОД({system[i][1]}, {system[j][1]}) = {g}. "
                                    "Китайская теорема требует попарно взаимно простых модулей.",
                        },
                    ],
                }

    big_m = 1
    for _, m in system:
        big_m *= m

    steps += [
        f"Модули попарно взаимно просты, значит решение единственно по модулю M = {' · '.join(str(m) for _, m in system)} = {big_m}.",
        "Для каждого i: Mᵢ = M / mᵢ и yᵢ = Mᵢ⁻¹ mod mᵢ (обратный находим расширенным алгоритмом Евклида).",
        "Тогда x = Σ rᵢ·Mᵢ·yᵢ (mod M): i-е слагаемое ≡ rᵢ по модулю mᵢ и ≡ 0 по остальным модулям.",
    ]

    rows = []
    total = 0
    euclid_tables = []
    for index, (r, m) in enumerate(system, start=1):
        m_i = big_m // m
        m_i_mod = m_i % m
        euclid = extended_euclid(m_i_mod, m) if m_i_mod else None
        y_i = euclid["s"] % m if euclid else 0
        term = r * m_i * y_i
        total += term
        rows.append([index, r, m, m_i, m_i_mod, y_i, term])
        if index == 1 and euclid:
            euclid_tables.append(euclid_section(m_i_mod, m, euclid))

    x = total % big_m
    checks = "; ".join(f"{x} mod {m} = {x % m}" for _, m in system)
    steps.append(f"Сумма {total} mod {big_m} = {x}. Проверка: {checks}.")

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table", "title": "Построение решения",
                "columns": ["i", "rᵢ", "mᵢ", "Mᵢ = M/mᵢ", "Mᵢ mod mᵢ", "yᵢ = Mᵢ⁻¹", "rᵢ·Mᵢ·yᵢ"],
                "rows": rows, "highlight": [],
            },
            *[{**table, "title": "Обратный для i = 1: " + table["title"]} for table in euclid_tables],
            {"type": "result", "kind": "ok", "title": "Ответ", "text": f"x ≡ {x} (mod {big_m})"},
        ],
    }


# --- 4. Квадратичное сравнение x² ≡ a (mod p) ---

MAX_QUADRATIC_PRIME = 10 ** 9
MAX_RESIDUE_TABLE = 31


def tonelli_shanks(a: int, p: int) -> int:
    """Квадратный корень из квадратичного вычета a по нечётному простому модулю p."""
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def solve_quadratic(params: dict) -> dict:
    a = get_int(params, "a", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    p = get_int(params, "p", 3, MAX_QUADRATIC_PRIME)
    if not is_prime(p):
        raise ValueError(f"p = {p} — не простое число (нужно нечётное простое)")

    a_r = a % p
    equation = f"x² ≡ {num(a)} (mod {p})"
    steps = [f"Приводим: x² ≡ {a_r} (mod {p})."]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}]

    if p <= MAX_RESIDUE_TABLE:
        squares = [(x, x * x % p) for x in range(1, p)]
        residues = sorted({value for _, value in squares})
        sections.append({
            "type": "table",
            "title": f"Квадраты по модулю {p} (выделены x с x² ≡ {a_r}); вычеты: {', '.join(map(str, residues))}",
            "columns": ["x", "x²", f"x² mod {p}"],
            "rows": [[x, x * x, value] for x, value in squares],
            "highlight": [index for index, (_, value) in enumerate(squares) if value == a_r],
        })

    if a_r == 0:
        steps.append(f"{num(a)} ≡ 0 (mod {p}), значит x² делится на простое p, и x ≡ 0.")
        sections.append({"type": "result", "kind": "ok", "title": "Один корень", "text": f"x ≡ 0 (mod {p})"})
        return {"equation": equation, "sections": sections}

    power = (p - 1) // 2
    legendre = pow(a_r, power, p)
    steps += [
        f"Критерий Эйлера: a — квадратичный вычет ⇔ a^((p−1)/2) ≡ 1 (mod p).",
        f"Считаем {a_r}^{power} mod {p} = " + ("1 — вычет, корни есть." if legendre == 1 else f"{legendre} ≡ −1 — невычет, корней нет."),
    ]

    if legendre != 1:
        sections.append({
            "type": "result", "kind": "fail", "title": "Решений нет",
            "text": f"{a_r} — квадратичный невычет по модулю {p}: символ Лежандра ({a_r}/{p}) = −1.",
        })
        return {"equation": equation, "sections": sections}

    if p % 4 == 3:
        root = pow(a_r, (p + 1) // 4, p)
        steps.append(f"p ≡ 3 (mod 4), поэтому корень даёт формула x = a^((p+1)/4) = {a_r}^{(p + 1) // 4} mod {p} = {root}.")
    else:
        root = tonelli_shanks(a_r, p)
        steps.append(f"p ≡ 1 (mod 4) — корень находим алгоритмом Тонелли–Шенкса: x = {root}.")

    other = p - root
    roots = sorted((root, other))
    steps.append(f"Второй корень — противоположный: −{root} ≡ {other}. Проверка: {roots[0]}² mod {p} = {roots[0] ** 2 % p}, {roots[1]}² mod {p} = {roots[1] ** 2 % p}.")
    sections.append({
        "type": "result", "kind": "ok", "title": "Два корня",
        "text": f"x ≡ {roots[0]} или x ≡ {roots[1]} (mod {p})",
    })
    return {"equation": equation, "sections": sections}


# --- 5. Признаки делимости ---

MAX_DIGITS = 60
MAX_DIVISOR = 1000


def solve_divisibility(params: dict) -> dict:
    digits = str(params.get("n", "")).strip().lstrip("+")
    if not digits.isdigit() or not digits.isascii():
        raise ValueError("N должно быть натуральным числом (только цифры)")
    if len(digits) > MAX_DIGITS:
        raise ValueError(f"N — не больше {MAX_DIGITS} цифр")
    digits = digits.lstrip("0") or "0"
    m = get_int(params, "m", 2, MAX_DIVISOR)

    equation = f"{digits} mod {m} = ?"

    # Остаток 10ⁱ берём в «симметричной» форме (от −m/2 до m/2):
    # так сразу видно 10 ≡ 1 (mod 9) и 10 ≡ −1 (mod 11).
    def symmetric(value: int) -> int:
        return value - m if value > m // 2 else value

    rows = []
    total = 0
    power = 1 % m
    for index, digit in enumerate(reversed(digits)):
        weight = symmetric(power)
        contribution = int(digit) * weight
        total += contribution
        rows.append([index, digit, num(weight), num(contribution)])
        power = power * 10 % m

    remainder = total % m
    steps = [
        f"N = Σ dᵢ·10ⁱ, поэтому N ≡ Σ dᵢ·(10ⁱ mod {m}) (mod {m}) — достаточно знать остатки степеней десяти.",
        f"10 ≡ {num(symmetric(10 % m))} (mod {m}).",
    ]
    if m in (3, 9):
        steps.append(f"10 ≡ 1 (mod {m}) ⇒ 10ⁱ ≡ 1: N сравнимо с суммой своих цифр — классический признак делимости на {m}.")
    elif m == 11:
        steps.append("10 ≡ −1 (mod 11) ⇒ 10ⁱ ≡ (−1)ⁱ: N сравнимо со знакочередующейся суммой цифр справа налево.")
    elif m in (2, 5, 10):
        steps.append(f"10 ≡ 0 (mod {m}) ⇒ важна только последняя цифра.")
    elif m in (4, 25, 20, 50, 100):
        steps.append(f"100 ≡ 0 (mod {m}) ⇒ важны только две последние цифры.")
    elif m in (7, 13, 77, 91, 143, 1001):
        steps.append(f"1000 ≡ −1 (mod {m}), так как 1001 = 7·11·13 ⇒ знакочередующаяся сумма трёхзначных групп.")
    steps.append(f"Сумма взвешенных цифр: {num(total)} ≡ {remainder} (mod {m}). Проверка прямым делением: {digits} mod {m} = {int(digits) % m}.")

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table", "title": "Вклад каждой цифры (i — позиция справа)",
                "columns": ["i", "цифра dᵢ", f"10ⁱ mod {m}", "dᵢ·(10ⁱ mod m)"],
                "rows": rows, "highlight": [],
            },
            {
                "type": "result", "kind": "ok" if remainder == 0 else "info",
                "title": f"Делится на {m}" if remainder == 0 else f"Не делится на {m}",
                "text": f"{digits} ≡ {remainder} (mod {m})",
            },
        ],
    }


SOLVERS = {
    "power": solve_power,
    "euler": solve_euler,
    "crt": solve_crt,
    "quadratic": solve_quadratic,
    "divisibility": solve_divisibility,
}


def solve_congruence_example(example: str, params: dict) -> dict:
    if example not in SOLVERS:
        raise ValueError(f"Неизвестный пример: {example}")
    result = SOLVERS[example](params)
    result["example"] = example
    return result
