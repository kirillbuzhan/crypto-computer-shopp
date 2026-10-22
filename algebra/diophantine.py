"""Примеры диофантовых уравнений.

Диофантово уравнение — уравнение с целыми коэффициентами, решения
которого ищутся в целых числах. Пять примеров:

    1. linear      — линейное уравнение ax + by = c (расширенный алгоритм Евклида);
    2. congruence  — линейное сравнение ax ≡ b (mod m), то же уравнение ax − my = b;
    3. rsa         — секретный ключ RSA: e·d − φ(n)·k = 1;
    4. coins       — неотрицательные решения ax + by = c (задача о размене);
    5. pythagorean — нелинейное x² + y² = z² (пифагоровы тройки, формула Евклида).

Каждый решатель возвращает словарь с уравнением и списком «секций» —
шагов решения, таблиц и итоговых выводов, которые фронтенд рисует
одинаково для всех примеров:

    {"type": "steps",  "title": str, "items": [str, ...]}
    {"type": "table",  "title": str, "columns": [...], "rows": [[...]], "highlight": [row_index, ...]}
    {"type": "result", "kind": "ok" | "fail" | "info", "title": str, "text": str}
"""

from math import gcd, isqrt


MAX_ABS_VALUE = 10 ** 12
MAX_LISTED_SOLUTIONS = 50


def num(value: int) -> str:
    """Число с типографским минусом."""
    return str(value).replace("-", "−")


def linear_expr(terms: list[tuple[int, str]]) -> str:
    """Записать сумму вида 56x − 72y без «+ −» и коэффициентов 1."""
    parts = []
    for coef, var in terms:
        if coef == 0:
            continue
        magnitude = abs(coef)
        body = f"{'' if magnitude == 1 and var else magnitude}{var}"
        if not parts:
            parts.append(("−" if coef < 0 else "") + body)
        else:
            parts.append((" − " if coef < 0 else " + ") + body)
    return "".join(parts) or "0"


def param_expr(base: int, step: int, var: str = "t") -> str:
    """Записать base + step·t."""
    if step == 0:
        return num(base)
    sign = "+" if step > 0 else "−"
    return f"{num(base)} {sign} {abs(step)}·{var}"


def get_int(params: dict, name: str, low: int, high: int, label: str | None = None) -> int:
    label = label or name
    raw = params.get(name)
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        raise ValueError(f"Параметр {label} должен быть целым числом") from None
    if not low <= value <= high:
        raise ValueError(f"Параметр {label} должен быть от {num(low)} до {num(high)}")
    return value


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def extended_euclid(a: int, b: int) -> dict:
    """Расширенный алгоритм Евклида для a, b > 0 с таблицей шагов.

    Инвариант каждой строки: rᵢ = sᵢ·a + tᵢ·b, где
    rᵢ = rᵢ₋₂ − qᵢ·rᵢ₋₁, а qᵢ = rᵢ₋₂ div rᵢ₋₁.
    Последний ненулевой остаток — НОД(a, b).
    """
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    rows = [[0, num(r0), "—", num(s0), num(t0)], [1, num(r1), "—", num(s1), num(t1)]]

    index = 1
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
        index += 1
        rows.append([index, num(r1), num(q), num(s1), num(t1)])

    return {"gcd": r0, "s": s0, "t": t0, "rows": rows, "gcd_row": len(rows) - 2}


def euclid_section(a: int, b: int, euclid: dict) -> dict:
    return {
        "type": "table",
        "title": f"Расширенный алгоритм Евклида для a = {a}, b = {b} (rᵢ = sᵢ·a + tᵢ·b)",
        "columns": ["i", "rᵢ", "qᵢ", "sᵢ", "tᵢ"],
        "rows": euclid["rows"],
        "highlight": [euclid["gcd_row"]],
    }


def solve_linear_core(a: int, b: int, c: int) -> dict:
    """Общее решение ax + by = c (a, b ≠ 0).

    Евклид считается для |a|, |b|; знаки переносятся на коэффициенты Безу.
    Возвращает частное решение, нормализованное к наименьшему x ≥ 0,
    и шаги общего решения x = x₀ + (b/g)·t, y = y₀ − (a/g)·t.
    """
    euclid = extended_euclid(abs(a), abs(b))
    g = euclid["gcd"]
    s = euclid["s"] * (1 if a > 0 else -1)
    t = euclid["t"] * (1 if b > 0 else -1)

    result = {"euclid": euclid, "gcd": g, "s": s, "t": t, "solvable": c % g == 0}
    if not result["solvable"]:
        return result

    k = c // g
    x_raw, y_raw = s * k, t * k
    dx, dy = b // g, -(a // g)

    # Сдвигаем параметр так, чтобы x₀ стал наименьшим неотрицательным.
    x0 = x_raw % abs(dx)
    shift = (x0 - x_raw) // dx
    y0 = y_raw + dy * shift

    result.update({"k": k, "x_raw": x_raw, "y_raw": y_raw, "x0": x0, "y0": y0, "dx": dx, "dy": dy})
    return result


def bezout_line(a: int, b: int, core: dict) -> str:
    return (
        f"Соотношение Безу: {linear_expr([(a, '')])}·({num(core['s'])}) "
        f"+ {linear_expr([(b, '')])}·({num(core['t'])}) = {core['gcd']}".replace("+ −", "− ")
    )


# --- 1. Линейное уравнение ax + by = c ---

def solve_linear(params: dict) -> dict:
    a = get_int(params, "a", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    b = get_int(params, "b", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    c = get_int(params, "c", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    if a == 0 or b == 0:
        raise ValueError("Коэффициенты a и b должны быть ненулевыми")

    equation = f"{linear_expr([(a, 'x'), (b, 'y')])} = {num(c)}"
    core = solve_linear_core(a, b, c)
    g = core["gcd"]

    steps = [
        f"Находим d = НОД(|a|, |b|) = НОД({abs(a)}, {abs(b)}) расширенным алгоритмом Евклида: d = {g}.",
        bezout_line(a, b, core) + ".",
        f"Решение существует тогда и только тогда, когда d | c: {num(c)} mod {g} = {c % g}.",
    ]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}, euclid_section(abs(a), abs(b), core["euclid"])]

    if not core["solvable"]:
        sections.append({
            "type": "result", "kind": "fail", "title": "Решений нет",
            "text": f"Левая часть при любых целых x, y делится на {g}, а правая часть {num(c)} — нет.",
        })
        return {"equation": equation, "sections": sections}

    steps += [
        f"Умножаем соотношение Безу на c / d = {num(core['k'])}: частное решение x = {num(core['x_raw'])}, y = {num(core['y_raw'])}.",
        f"Однородное уравнение {linear_expr([(a // g, 'x'), (b // g, 'y')])} = 0 даёт сдвиги x → x + {num(core['dx'])}·t, y → y {'−' if core['dy'] < 0 else '+'} {abs(core['dy'])}·t.",
        f"Сдвигаем t так, чтобы x был наименьшим неотрицательным: x₀ = {num(core['x0'])}, y₀ = {num(core['y0'])}.",
    ]

    rows = []
    for param in range(-2, 3):
        x = core["x0"] + core["dx"] * param
        y = core["y0"] + core["dy"] * param
        rows.append([num(param), num(x), num(y), f"{num(a * x + b * y)} ✓"])

    sections += [
        {"type": "table", "title": "Несколько решений", "columns": ["t", "x", "y", "ax + by"], "rows": rows, "highlight": [2]},
        {
            "type": "result", "kind": "ok", "title": "Общее решение (t ∈ ℤ)",
            "text": f"x = {param_expr(core['x0'], core['dx'])},  y = {param_expr(core['y0'], core['dy'])}",
        },
    ]
    return {"equation": equation, "sections": sections}


# --- 2. Линейное сравнение ax ≡ b (mod m) ---

def solve_congruence(params: dict) -> dict:
    a = get_int(params, "a", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    b = get_int(params, "b", -MAX_ABS_VALUE, MAX_ABS_VALUE)
    m = get_int(params, "m", 2, MAX_ABS_VALUE)

    equation = f"{linear_expr([(a, 'x')])} ≡ {num(b)} (mod {m})"
    a_r, b_r = a % m, b % m
    if a_r == 0:
        raise ValueError(f"a ≡ 0 (mod {m}) — сравнение вырождается в 0 ≡ {b_r}, выберите другое a")

    euclid = extended_euclid(a_r, m)
    g = euclid["gcd"]
    steps = [
        f"Приводим коэффициенты по модулю: {a_r}x ≡ {b_r} (mod {m}).",
        f"Сравнение равносильно диофантову уравнению {a_r}x − {m}y = {b_r}.",
        f"d = НОД({a_r}, {m}) = {g}; решение есть тогда и только тогда, когда d | {b_r}.",
    ]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}, euclid_section(a_r, m, euclid)]

    if b_r % g != 0:
        sections.append({
            "type": "result", "kind": "fail", "title": "Решений нет",
            "text": f"{b_r} не делится на НОД({a_r}, {m}) = {g}.",
        })
        return {"equation": equation, "sections": sections}

    m_g = m // g
    x0 = (euclid["s"] * (b_r // g)) % m_g
    steps += [
        f"Из Евклида: {a_r}·({num(euclid['s'])}) + {m}·({num(euclid['t'])}) = {g}, значит {a_r}·({num(euclid['s'])}) ≡ {g} (mod {m}).",
        f"Умножаем на {b_r} / {g} = {b_r // g}: x ≡ {num(euclid['s'])}·{b_r // g} ≡ {x0} (mod {m_g}).",
        f"По модулю {m} это даёт ровно d = {g} различн{'ое решение' if g == 1 else 'ых решения' if g < 5 else 'ых решений'}: x = {x0} + {m_g}·k, k = 0…{g - 1}.",
    ]

    shown = min(g, MAX_LISTED_SOLUTIONS)
    rows = []
    for index in range(shown):
        x = x0 + m_g * index
        rows.append([index, x, f"{a_r}·{x} = {a_r * x}", f"{(a_r * x) % m} ✓"])

    title = "Решения по модулю m" + (f" (первые {shown} из {g})" if shown < g else "")
    sections += [
        {"type": "table", "title": title, "columns": ["k", "x", "a·x", f"a·x mod {m}"], "rows": rows, "highlight": []},
        {"type": "result", "kind": "ok", "title": "Ответ", "text": f"x ≡ {x0} (mod {m_g})"},
    ]
    return {"equation": equation, "sections": sections}


# --- 3. Секретный ключ RSA: e·d ≡ 1 (mod φ(n)) ---

MAX_RSA_PRIME = 10 ** 6


def solve_rsa(params: dict) -> dict:
    p = get_int(params, "p", 2, MAX_RSA_PRIME)
    q = get_int(params, "q", 2, MAX_RSA_PRIME)
    e = get_int(params, "e", 2, MAX_ABS_VALUE)
    message = get_int(params, "msg", 0, MAX_ABS_VALUE, "M")

    for name, value in (("p", p), ("q", q)):
        if not is_prime(value):
            raise ValueError(f"{name} = {value} — не простое число")
    if p == q:
        raise ValueError("p и q должны быть различными")

    n = p * q
    phi = (p - 1) * (q - 1)
    if e >= phi:
        raise ValueError(f"Нужно 1 < e < φ(n) = {phi}")
    if message >= n:
        raise ValueError(f"Сообщение M должно быть меньше n = {n}")

    equation = f"{e}·d − {phi}·k = 1"
    euclid = extended_euclid(e, phi)
    g = euclid["gcd"]

    steps = [
        f"n = p·q = {p}·{q} = {n},  φ(n) = (p − 1)(q − 1) = {p - 1}·{q - 1} = {phi}.",
        f"Ключ d — обратный к e по модулю φ(n): e·d ≡ 1 (mod {phi}), т.е. диофантово уравнение {e}·d − {phi}·k = 1.",
        f"Решение есть только при НОД(e, φ(n)) = 1. Считаем: НОД({e}, {phi}) = {g}.",
    ]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}, euclid_section(e, phi, euclid)]

    if g != 1:
        sections.append({
            "type": "result", "kind": "fail", "title": "Ключ d не существует",
            "text": f"e = {e} и φ(n) = {phi} не взаимно просты (НОД = {g}) — выберите другое e.",
        })
        return {"equation": equation, "sections": sections}

    d = euclid["s"] % phi
    k = (e * d - 1) // phi
    cipher = pow(message, e, n)
    decrypted = pow(cipher, d, n)

    steps += [
        f"Из Евклида: {e}·({num(euclid['s'])}) + {phi}·({num(euclid['t'])}) = 1, значит d ≡ {num(euclid['s'])} ≡ {d} (mod {phi}).",
        f"Проверка: e·d = {e}·{d} = {e * d} = {k}·{phi} + 1.",
        f"Шифрование M = {message}: C = Mᵉ mod n = {message}^{e} mod {n} = {cipher}.",
        f"Расшифрование: Cᵈ mod n = {cipher}^{d} mod {n} = {decrypted}.",
    ]

    sections += [
        {
            "type": "table", "title": "Ключи RSA",
            "columns": ["", "значение"],
            "rows": [["открытый ключ (e, n)", f"({e}, {n})"], ["секретный ключ (d, n)", f"({d}, {n})"], ["C = Mᵉ mod n", cipher], ["Cᵈ mod n", decrypted]],
            "highlight": [1],
        },
        {
            "type": "result", "kind": "ok" if decrypted == message else "fail",
            "title": f"d = {d}",
            "text": f"Сообщение {message} → шифр {cipher} → расшифровано {decrypted}" + (" ✓" if decrypted == message else " ✗"),
        },
    ]
    return {"equation": equation, "sections": sections}


# --- 4. Неотрицательные решения ax + by = c (размен суммы) ---

MAX_COIN = 10 ** 6
MAX_SUM = 10 ** 9


def solve_coins(params: dict) -> dict:
    a = get_int(params, "a", 1, MAX_COIN)
    b = get_int(params, "b", 1, MAX_COIN)
    c = get_int(params, "c", 0, MAX_SUM)

    equation = f"{linear_expr([(a, 'x'), (b, 'y')])} = {c},  x, y ≥ 0"
    core = solve_linear_core(a, b, c)
    g = core["gcd"]

    steps = [
        f"Сколько монет по {a} (x штук) и по {b} (y штук) дают ровно {c}? Нужны целые x, y ≥ 0.",
        f"НОД({a}, {b}) = {g}; {c} mod {g} = {c % g}.",
    ]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}, euclid_section(a, b, core["euclid"])]

    frobenius_note = None
    if g == 1:
        frobenius = a * b - a - b
        frobenius_note = {
            "type": "result", "kind": "info", "title": "Число Фробениуса",
            "text": (
                f"Так как НОД = 1, любую сумму больше ab − a − b = {frobenius} можно набрать монетами {a} и {b}."
                if frobenius >= 0 else f"Монетой {min(a, b)} можно набрать любую сумму."
            ),
        }

    if not core["solvable"]:
        sections.append({
            "type": "result", "kind": "fail", "title": "Набрать нельзя",
            "text": f"Любая сумма монет {a} и {b} делится на {g}, а {c} — нет.",
        })
        return {"equation": equation, "sections": sections}

    x0, y0, dx, dy = core["x0"], core["y0"], core["dx"], core["dy"]
    # x = x0 + dx·t ≥ 0 и y = y0 + dy·t ≥ 0, где dx > 0, dy < 0; x0 — наименьший ≥ 0, поэтому t ≥ 0.
    t_max = y0 // -dy if y0 >= 0 else -1
    count = t_max + 1 if t_max >= 0 else 0

    steps += [
        f"Общее решение: x = {param_expr(x0, dx)}, y = {param_expr(y0, dy)}.",
        f"x ≥ 0 ⇔ t ≥ 0;  y ≥ 0 ⇔ t ≤ {num(y0)} / {-dy}"
        + (f" ⇒ t = 0…{t_max}." if count else " — таких t нет."),
    ]

    if count == 0:
        sections.append({
            "type": "result", "kind": "fail", "title": "Неотрицательных решений нет",
            "text": f"Целые решения есть (например, x = {num(x0)}, y = {num(y0)}), но y < 0 — сумму {c} так не набрать.",
        })
    else:
        shown = min(count, MAX_LISTED_SOLUTIONS)
        rows = []
        for param in range(shown):
            x = x0 + dx * param
            y = y0 + dy * param
            rows.append([param, x, y, x + y, f"{a}·{x} + {b}·{y} = {a * x + b * y}"])
        min_coins = min(range(shown), key=lambda index: rows[index][3])

        sections += [
            {
                "type": "table",
                "title": "Все способы" + (f" (первые {shown} из {count})" if shown < count else "") + " — выделен способ с наименьшим числом монет",
                "columns": ["t", f"x (по {a})", f"y (по {b})", "монет", "проверка"],
                "rows": rows,
                "highlight": [min_coins],
            },
            {"type": "result", "kind": "ok", "title": f"Способов: {count}", "text": f"Сумму {c} можно набрать {count} способ{'ом' if count % 10 == 1 and count % 100 != 11 else 'ами'}."},
        ]

    if frobenius_note:
        sections.append(frobenius_note)
    return {"equation": equation, "sections": sections}


# --- 5. Пифагоровы тройки x² + y² = z² ---

MAX_HYPOTENUSE = 300


def solve_pythagorean(params: dict) -> dict:
    limit = get_int(params, "n", 5, MAX_HYPOTENUSE, "N")
    equation = f"x² + y² = z²,  0 < x < y,  z ≤ {limit}"

    triples = []
    m = 2
    while m * m + 1 <= limit:
        for n in range(1, m):
            if (m - n) % 2 == 1 and gcd(m, n) == 1:
                x, y, z = m * m - n * n, 2 * m * n, m * m + n * n
                for k in range(1, limit // z + 1):
                    a, b = sorted((k * x, k * y))
                    triples.append((k * z, a, b, m, n, k))
        m += 1
    triples.sort()

    steps = [
        "Уравнение нелинейное, но все решения в натуральных числах описываются формулой Евклида.",
        "Примитивная тройка (НОД(x, y, z) = 1): x = m² − n², y = 2mn, z = m² + n², где m > n > 0, НОД(m, n) = 1, m − n нечётно.",
        "Остальные тройки — кратные примитивным: (kx, ky, kz).",
        "Почему так: z² − x² = y² ⇒ (z − x)(z + x) = y², а для взаимно простых множителей каждый должен быть полным квадратом (с точностью до множителя 2).",
    ]

    primitive_count = sum(1 for triple in triples if triple[5] == 1)
    rows = [
        [f"({a}, {b}, {z})", m, n, k, "да" if k == 1 else "нет", f"{a * a} + {b * b} = {z * z} ✓"]
        for z, a, b, m, n, k in triples
    ]

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table",
                "title": "Тройки с z ≤ N — примитивные выделены",
                "columns": ["(x, y, z)", "m", "n", "k", "примитивная", "x² + y² = z²"],
                "rows": rows,
                "highlight": [index for index, triple in enumerate(triples) if triple[5] == 1],
            },
            {
                "type": "result", "kind": "ok", "title": f"Найдено троек: {len(triples)}",
                "text": f"Из них примитивных: {primitive_count}.",
            },
        ],
    }


SOLVERS = {
    "linear": solve_linear,
    "congruence": solve_congruence,
    "rsa": solve_rsa,
    "coins": solve_coins,
    "pythagorean": solve_pythagorean,
}


def solve_diophantine(example: str, params: dict) -> dict:
    if example not in SOLVERS:
        raise ValueError(f"Неизвестный пример: {example}")
    result = SOLVERS[example](params)
    result["example"] = example
    return result
