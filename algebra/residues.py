"""Примеры на вычеты по модулю.

Вычет по модулю m — класс [r]ₘ = {r + km : k ∈ ℤ} чисел с одинаковым
остатком от деления на m. Множество классов образует кольцо ℤₘ.
Пять примеров:

    1. classes   — классы вычетов, наименьший неотрицательный и абсолютно наименьший вычеты;
    2. reduced   — приведённая система вычетов, φ(m) и её перестановка умножением на a;
    3. units     — обратимые элементы и делители нуля кольца ℤₘ;
    4. order     — порядок элемента и первообразные корни;
    5. dlog      — дискретный логарифм gˣ ≡ b (mod m) методом «шаг младенца — шаг великана».

Формат ответа — как у диофантовых уравнений и сравнений: уравнение
и список секций (steps / table / result).
"""

from math import gcd, isqrt

from algebra.diophantine import extended_euclid, get_int, num
from algebra.congruences import euler_phi, factorization_text, factorize


def symmetric(value: int, m: int) -> int:
    """Абсолютно наименьший вычет: представитель из (−m/2, m/2]."""
    value %= m
    return value - m if value > m // 2 else value


def inverse(a: int, m: int) -> int | None:
    euclid = extended_euclid(a % m, m) if a % m else None
    if not euclid or euclid["gcd"] != 1:
        return None
    return euclid["s"] % m


def element_order(a: int, m: int) -> int:
    """Наименьшее k ≥ 1 с aᵏ ≡ 1 (mod m) (a — обратимый элемент)."""
    k, value = 1, a % m
    while value != 1 % m:
        value = value * a % m
        k += 1
    return k


# --- 1. Классы вычетов ---

MAX_CLASSES_MODULUS = 30


def solve_classes(params: dict) -> dict:
    m = get_int(params, "m", 2, MAX_CLASSES_MODULUS)
    x = get_int(params, "x", -10 ** 12, 10 ** 12)

    q, r = divmod(x, m)
    sym = symmetric(x, m)
    equation = f"{num(x)} ∈ [?]_{m}"

    steps = [
        f"Делим с остатком (остаток 0 ≤ r < m): {num(x)} = {num(q)}·{m} + {r}.",
        f"Значит {num(x)} ≡ {r} (mod {m}) и лежит в классе [{r}]_{m} = {{…, {num(r - m)}, {r}, {r + m}, {r + 2 * m}, …}}.",
        f"Наименьший неотрицательный вычет — {r}; абсолютно наименьший (|r| ≤ m/2) — {num(sym)}.",
        f"Всего классов ровно {m}: [0], [1], …, [{m - 1}] — они образуют полную систему вычетов и разбивают ℤ без пересечений.",
    ]

    rows = []
    for residue in range(m):
        members = [residue + k * m for k in range(-2, 3)]
        rows.append([
            f"[{residue}]",
            ", ".join(num(member) for member in members) + ", …",
            residue,
            num(symmetric(residue, m)),
        ])

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table",
                "title": f"Полная система вычетов по модулю {m} (выделен класс числа {num(x)})",
                "columns": ["класс", "представители r + km (k = −2…2)", "наим. неотрицательный", "абсолютно наименьший"],
                "rows": rows,
                "highlight": [r],
            },
            {"type": "result", "kind": "ok", "title": "Ответ", "text": f"{num(x)} ∈ [{r}]_{m},  {num(x)} ≡ {r} ≡ {num(sym)} (mod {m})"},
        ],
    }


# --- 2. Приведённая система вычетов ---

MAX_REDUCED_MODULUS = 200


def solve_reduced(params: dict) -> dict:
    m = get_int(params, "m", 2, MAX_REDUCED_MODULUS)
    a = get_int(params, "a", -10 ** 12, 10 ** 12)

    reduced = [r for r in range(1, m) if gcd(r, m) == 1] if m > 1 else []
    factors = factorize(m)
    phi = euler_phi(factors)
    a_r = a % m
    equation = f"{{{a_r}·r mod {m} : r ∈ R}}"

    steps = [
        f"Приведённая система вычетов R — вычеты полной системы 0…{m - 1}, взаимно простые с m = {m} = {factorization_text(factors)}.",
        f"R = {{{', '.join(map(str, reduced))}}}, её размер φ({m}) = {phi}.",
    ]

    images = [a_r * r % m for r in reduced]
    rows = [[r, f"{a_r}·{r} = {a_r * r}", image, "✓" if gcd(image, m) == 1 else "✗"] for r, image in zip(reduced, images)]
    sections = [{"type": "steps", "title": "Ход решения", "items": steps}]
    table = {
        "type": "table",
        "title": f"Умножение приведённой системы на a = {a_r}",
        "columns": ["r", "a·r", "a·r mod m", "∈ R"],
        "rows": rows,
        "highlight": [],
    }

    if gcd(a_r, m) != 1:
        steps.append(f"НОД({a_r}, {m}) = {gcd(a_r, m)} ≠ 1, поэтому a·r теряет взаимную простоту с m — получается не приведённая система.")
        sections += [table, {
            "type": "result", "kind": "fail", "title": "Перестановки нет",
            "text": f"Образы {{{', '.join(map(str, sorted(set(images))))}}} ≠ R: умножать можно только на a, взаимно простое с m.",
        }]
        return {"equation": equation, "sections": sections}

    product = 1
    for r in reduced:
        product = product * r % m
    steps += [
        f"НОД({a_r}, {m}) = 1, поэтому a·r снова взаимно просто с m и различны для разных r: {{a·r}} — та же система R, только переставленная.",
        f"Перемножим все элементы: ∏(a·r) ≡ ∏r ⇒ a^φ(m)·∏r ≡ ∏r. Так как ∏r ≡ {product} обратимо, a^φ(m) ≡ 1 — это доказательство теоремы Эйлера.",
        f"Проверка: {a_r}^{phi} mod {m} = {pow(a_r, phi, m)}.",
    ]
    table["highlight"] = [index for index, r in enumerate(reduced) if images[index] == r]
    sections += [table, {
        "type": "result", "kind": "ok", "title": f"φ({m}) = {phi}, a·R = R",
        "text": f"{{{', '.join(map(str, images))}}} — перестановка R;  {a_r}^{phi} ≡ 1 (mod {m})",
    }]
    return {"equation": equation, "sections": sections}


# --- 3. Обратимые элементы и делители нуля ---

MAX_UNITS_MODULUS = 60


def solve_units(params: dict) -> dict:
    m = get_int(params, "m", 2, MAX_UNITS_MODULUS)
    equation = f"ℤ_{m} = {{0, 1, …, {m - 1}}}"

    rows = []
    units = []
    zero_divisors = []
    for a in range(m):
        g = gcd(a, m)
        if a == 0:
            rows.append([0, m, "ноль", "—", "—"])
        elif g == 1:
            inv = inverse(a, m)
            units.append(a)
            rows.append([a, 1, "обратимый", f"{a}⁻¹ = {inv}", f"{a}·{inv} = {a * inv} ≡ 1"])
        else:
            partner = m // g
            zero_divisors.append(a)
            rows.append([a, g, "делитель нуля", "нет", f"{a}·{partner} = {a * partner} ≡ 0"])

    is_field = not zero_divisors
    factors = factorize(m)
    steps = [
        "Элемент a ∈ ℤₘ обратим ⇔ НОД(a, m) = 1; обратный находится расширенным алгоритмом Евклида из a·s + m·t = 1.",
        "Если d = НОД(a, m) > 1, то a·(m/d) ≡ 0, хотя оба множителя ненулевые, — a делитель нуля и необратим.",
        f"m = {m} = {factorization_text(factors)}: обратимых элементов φ({m}) = {len(units)}, делителей нуля — {len(zero_divisors)}.",
        f"ℤₘ — поле ⇔ m простое: здесь {'m простое, все ненулевые элементы обратимы.' if is_field else 'm составное, есть делители нуля.'}",
    ]

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table",
                "title": "Элементы кольца ℤₘ (выделены обратимые)",
                "columns": ["a", "НОД(a, m)", "тип", "обратный", "проверка"],
                "rows": rows,
                "highlight": units,
            },
            {
                "type": "result", "kind": "ok" if is_field else "info",
                "title": f"ℤ_{m} — {'поле' if is_field else 'кольцо, но не поле'}",
                "text": f"Группа обратимых ℤ_{m}* = {{{', '.join(map(str, units))}}}"
                        + (f";  делители нуля: {{{', '.join(map(str, zero_divisors))}}}" if zero_divisors else ""),
            },
        ],
    }


# --- 4. Порядок элемента и первообразные корни ---

MAX_ORDER_MODULUS = 1000
MAX_ORDER_ROWS = 60
MAX_SHOWN_POWERS = 12


def has_primitive_root(m: int, factors: list[tuple[int, int]]) -> bool:
    """Первообразные корни есть только при m = 2, 4, pᵏ, 2pᵏ (p — нечётное простое)."""
    if m in (2, 4):
        return True
    odd = [(p, e) for p, e in factors if p != 2]
    two_power = next((e for p, e in factors if p == 2), 0)
    return len(odd) == 1 and two_power <= 1


def solve_order(params: dict) -> dict:
    m = get_int(params, "m", 3, MAX_ORDER_MODULUS)
    factors = factorize(m)
    phi = euler_phi(factors)
    equation = f"ord_{m}(a) = min{{k ≥ 1 : aᵏ ≡ 1 (mod {m})}}"

    units = [a for a in range(1, m) if gcd(a, m) == 1]
    orders = {a: element_order(a, m) for a in units}
    roots = [a for a in units if orders[a] == phi]
    divisors = [d for d in range(1, phi + 1) if phi % d == 0]

    rows = []
    for a in units[:MAX_ORDER_ROWS]:
        k = orders[a]
        powers = [pow(a, i, m) for i in range(1, min(k, MAX_SHOWN_POWERS) + 1)]
        shown = ", ".join(map(str, powers)) + (", …" if k > MAX_SHOWN_POWERS else "")
        rows.append([a, k, shown, "да" if k == phi else ""])

    exists = has_primitive_root(m, factors)
    steps = [
        f"Порядок a — длина цикла степеней a, a², a³, … по модулю m; он определён для обратимых a.",
        f"φ({m}) = {phi}. По теореме Лагранжа порядок любого элемента делит φ(m): возможные порядки — {', '.join(map(str, divisors))}.",
        f"Первообразный корень g — элемент максимального порядка φ(m): его степени пробегают всю группу ℤₘ*.",
        f"Первообразные корни существуют только при m = 2, 4, pᵏ, 2pᵏ; m = {factorization_text(factors)} — "
        + ("подходит." if exists else "не подходит, поэтому корней нет."),
    ]
    if roots:
        steps.append(f"Число первообразных корней равно φ(φ(m)) = φ({phi}) = {len(roots)}. Они — основа протокола Диффи–Хеллмана и схемы Эль-Гамаля.")

    title = "Порядки обратимых элементов (выделены первообразные корни)"
    if len(units) > MAX_ORDER_ROWS:
        title += f" — первые {MAX_ORDER_ROWS} из {len(units)}"

    return {
        "equation": equation,
        "sections": [
            {"type": "steps", "title": "Ход решения", "items": steps},
            {
                "type": "table", "title": title,
                "columns": ["a", "ord(a)", "a¹, a², … mod m", "первообразный"],
                "rows": rows,
                "highlight": [index for index, row in enumerate(rows) if row[1] == phi],
            },
            {
                "type": "result", "kind": "ok" if roots else "info",
                "title": f"Первообразных корней: {len(roots)}",
                "text": ("g ∈ {" + ", ".join(map(str, roots[:30])) + (", …" if len(roots) > 30 else "") + "}")
                        if roots else f"Группа ℤ_{m}* не циклическая: максимальный порядок {max(orders.values())} < φ(m) = {phi}.",
            },
        ],
    }


# --- 5. Дискретный логарифм: шаг младенца — шаг великана ---

MAX_DLOG_MODULUS = 10 ** 10
MAX_SHOWN_STEPS = 40
MAX_ORDER_BRUTE_FORCE = 10 ** 6


def solve_dlog(params: dict) -> dict:
    g = get_int(params, "g", 2, MAX_DLOG_MODULUS)
    b = get_int(params, "b", -MAX_DLOG_MODULUS, MAX_DLOG_MODULUS)
    m = get_int(params, "m", 3, MAX_DLOG_MODULUS)

    g, b = g % m, b % m
    if gcd(g, m) != 1 or gcd(b, m) != 1:
        raise ValueError("g и b должны быть взаимно просты с m")

    equation = f"{g}ˣ ≡ {b} (mod {m})"
    n = isqrt(m - 1) + 1  # n² ≥ m − 1 ≥ любого порядка g

    baby = {}
    value = 1
    baby_rows = []
    for j in range(n):
        baby.setdefault(value, j)
        if j < MAX_SHOWN_STEPS:
            baby_rows.append([j, value])
        value = value * g % m

    factor = pow(inverse(g, m), n, m)
    steps = [
        "Задача: найти x по g, b и m. Перебор x = 0, 1, 2, … требует до m шагов — на сложности этой задачи держатся Диффи–Хеллман и Эль-Гамаль.",
        f"Метод Шенкса: пишем x = i·n + j, где n = ⌈√m⌉ = {n}, 0 ≤ j < n. Тогда gʲ ≡ b·(g⁻ⁿ)ⁱ.",
        f"Шаги младенца: таблица gʲ mod m для j = 0…{n - 1}.",
        f"Шаги великана: g⁻ⁿ mod m = {factor}; считаем γᵢ = b·(g⁻ⁿ)ⁱ и ищем γᵢ в таблице. Итого ~2√m = {2 * n} операций вместо {m}.",
    ]

    giant_rows = []
    answer = None
    gamma = b
    for i in range(n + 1):
        found = gamma in baby
        if found and i > MAX_SHOWN_STEPS:
            giant_rows.append(["…", "…", "…"])
        if i < MAX_SHOWN_STEPS or found:
            giant_rows.append([i, gamma, f"j = {baby[gamma]}" if found else "—"])
        if found:
            answer = (i, baby[gamma])
            break
        gamma = gamma * factor % m

    sections = [{"type": "steps", "title": "Ход решения", "items": steps}]
    match_value = gamma if answer else None
    sections.append({
        "type": "table",
        "title": "Шаги младенца: gʲ mod m" + (f" (первые {MAX_SHOWN_STEPS} из {n})" if n > MAX_SHOWN_STEPS else ""),
        "columns": ["j", "gʲ mod m"],
        "rows": baby_rows,
        "highlight": [answer[1]] if answer and answer[1] < MAX_SHOWN_STEPS else [],
    })
    sections.append({
        "type": "table",
        "title": "Шаги великана: γᵢ = b·(g⁻ⁿ)ⁱ mod m",
        "columns": ["i", "γᵢ", "есть в таблице?"],
        "rows": giant_rows,
        "highlight": [len(giant_rows) - 1] if answer else [],
    })

    # Порядок g считаем перебором, поэтому только для умеренных m.
    order = element_order(g, m) if m <= MAX_ORDER_BRUTE_FORCE else None

    if not answer:
        sections.append({
            "type": "result", "kind": "fail", "title": "Решений нет",
            "text": f"{b} не является степенью {g} по модулю {m}: b не лежит в подгруппе, порождённой g"
                    + (f" (ord(g) = {order})." if order else "."),
        })
        return {"equation": equation, "sections": sections}

    i, j = answer
    x = i * n + j
    steps.append(f"Совпадение: γ_{i} = {match_value} = g^{j}. Значит x = i·n + j = {i}·{n} + {j} = {x}.")
    sections.append({
        "type": "result", "kind": "ok", "title": f"x = {x}",
        "text": f"Проверка: {g}^{x} mod {m} = {pow(g, x, m)}"
                + (f";  все решения: x ≡ {x} (mod ord(g) = {order})" if order else ""),
    })
    return {"equation": equation, "sections": sections}


SOLVERS = {
    "classes": solve_classes,
    "reduced": solve_reduced,
    "units": solve_units,
    "order": solve_order,
    "dlog": solve_dlog,
}


def solve_residue_example(example: str, params: dict) -> dict:
    if example not in SOLVERS:
        raise ValueError(f"Неизвестный пример: {example}")
    result = SOLVERS[example](params)
    result["example"] = example
    return result
