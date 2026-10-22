"""Генерация больших простых чисел с доказательством по критерию Поклингтона.

Критерий Поклингтона. Пусть n − 1 = F·R, где разложение F на простые
множители известно и F > √n. Если для каждого простого q | F найдётся
основание a, такое что
    a^(n−1) ≡ 1 (mod n)   и   НОД(a^((n−1)/q) − 1, n) = 1,
то n — простое.

(Любой простой делитель r числа n сравним с 1 по модулю F, т.е. r > F > √n,
а у составного n обязан быть простой делитель не больше √n.)

Построение «снизу вверх»:
    1. маленькое простое q₀ находится пробным делением;
    2. на каждом шаге берётся уже доказанное простое q (F = q) и
       n = R·q + 1, где R — чётное произведение малых простых, а q² > n;
    3. ищется основание a для критерия; если a^(n−1) ≢ 1 — n составное
       (тест Ферма), берём новое R.
Так как R состоит из малых простых, полное разложение n − 1 = R·q известно
на каждом шаге — оно нужно Эль-Гамалю для проверки первообразного корня.
Цепочка шагов — сертификат простоты: её можно перепроверить без доверия
генератору.
"""

import random
from collections import Counter
from math import gcd, isqrt

from algebra.diophantine import is_prime


MIN_BITS = 32
MAX_BITS = 1024
TRIAL_DIVISION_BITS = 24      # до этого размера простоту доказываем пробным делением
SMALL_PRIME_LIMIT = 1 << 16   # «малые» простые для множителя R
MAX_WITNESS = 100             # сколько оснований a перебираем для одного кандидата


def _small_primes(limit: int) -> list[int]:
    sieve = bytearray([1]) * limit
    sieve[0:2] = b"\x00\x00"
    for value in range(2, isqrt(limit - 1) + 1):
        if sieve[value]:
            sieve[value * value::value] = bytearray(len(sieve[value * value::value]))
    return [value for value in range(limit) if sieve[value]]


SMALL_PRIMES = _small_primes(SMALL_PRIME_LIMIT)
SIEVE_PRIMES = SMALL_PRIMES[:300]


def _has_small_divisor(n: int) -> bool:
    return any(n % prime == 0 and n != prime for prime in SIEVE_PRIMES)


def pocklington_witness(n: int, q: int) -> int | None:
    """Основание a для критерия Поклингтона с F = q (q — простое, q | n − 1).

    Возвращает a или None, если n составное (не прошло тест Ферма)
    либо подходящее a не нашлось среди первых MAX_WITNESS оснований.
    """
    r = (n - 1) // q
    for a in range(2, MAX_WITNESS):
        if pow(a, n - 1, n) != 1:
            return None
        if gcd(pow(a, r, n) - 1, n) == 1:
            return a
    return None


def _trial_prime(bits: int, rng: random.Random) -> int:
    while True:
        candidate = rng.randrange(1 << (bits - 1), 1 << bits) | 1
        if is_prime(candidate):
            return candidate


def _smooth_cofactor(q: int, bits: int, rng: random.Random) -> Counter:
    """Чётное R из малых простых, такое что R·q + 1 имеет ровно bits бит."""
    low, high = 1 << (bits - 1), (1 << bits) - 1
    factors = Counter({2: 1})
    r = 2
    while r * q < low:
        limit = min(high // (r * q), SMALL_PRIME_LIMIT - 1)
        # бинарным поиском находим, сколько малых простых не превосходят limit
        lo, hi = 0, len(SMALL_PRIMES)
        while lo < hi:
            mid = (lo + hi) // 2
            if SMALL_PRIMES[mid] <= limit:
                lo = mid + 1
            else:
                hi = mid
        prime = SMALL_PRIMES[rng.randrange(lo)]
        factors[prime] += 1
        r *= prime
    return factors


def generate_prime(bits: int, rng: random.Random | None = None) -> dict:
    """Простое p ровно из bits бит с сертификатом Поклингтона.

    Возвращает {"p", "factors": [(q, e), ...] — разложение p − 1,
    "chain": [шаги сертификата от маленького простого к p]}.
    """
    rng = rng or random.SystemRandom()

    if bits <= TRIAL_DIVISION_BITS:
        p = _trial_prime(bits, rng)
        factors = Counter()
        rest = p - 1
        for prime in SMALL_PRIMES:
            while rest % prime == 0:
                factors[prime] += 1
                rest //= prime
        if rest > 1:
            factors[rest] += 1
        step = {"p": p, "bits": p.bit_length(), "method": "trial"}
        return {"p": p, "factors": sorted(factors.items()), "chain": [step]}

    # q > √p гарантирует 2·bit_length(q) − 2 ≥ bits
    base = generate_prime(bits // 2 + 2, rng)
    q = base["p"]

    attempts = 0
    while True:
        attempts += 1
        r_factors = _smooth_cofactor(q, bits, rng)
        r = 1
        for prime, power in r_factors.items():
            r *= prime ** power
        p = r * q + 1
        if p.bit_length() != bits or q * q <= p or _has_small_divisor(p):
            continue
        a = pocklington_witness(p, q)
        if a is None:
            continue

        factors = r_factors.copy()
        factors[q] += 1
        step = {
            "p": p, "bits": bits, "method": "pocklington",
            "q": q, "r": r, "r_factors": sorted(r_factors.items()),
            "a": a, "attempts": attempts,
        }
        return {"p": p, "factors": sorted(factors.items()), "chain": base["chain"] + [step]}


def verify_chain(chain: list[dict]) -> bool:
    """Повторная проверка сертификата: каждый шаг опирается на предыдущий."""
    previous = None
    for step in chain:
        p = step["p"]
        if step["method"] == "trial":
            # пробное деление допустимо только для маленьких чисел — иначе проверка зависнет
            if previous is not None or p.bit_length() > TRIAL_DIVISION_BITS or not is_prime(p):
                return False
        else:
            q, r, a = step["q"], step["r"], step["a"]
            if q != previous or p - 1 != r * q or q * q <= p:
                return False
            if pow(a, p - 1, p) != 1 or gcd(pow(a, r, p) - 1, p) != 1:
                return False
            # R должно состоять из перечисленных малых простых — тогда разложение p − 1 известно
            product = 1
            for prime, power in step["r_factors"]:
                if not 1 < prime < SMALL_PRIME_LIMIT or not 1 <= power <= MAX_BITS or not is_prime(prime):
                    return False
                product *= prime ** power
                if product > r:
                    return False
            if product != r:
                return False
        previous = p
    return previous is not None


def chain_factors(chain: list[dict]) -> list[tuple[int, int]]:
    """Разложение p − 1 для последнего числа проверенного сертификата."""
    last = chain[-1]
    factors = Counter(dict(last["r_factors"]))
    factors[last["q"]] += 1
    return sorted(factors.items())


def parse_chain(raw) -> list[dict]:
    """Сертификат, пришедший от клиента (большие числа — строками), → проверяемый вид.

    Бросает ValueError, если структура не та или числа слишком велики.
    """
    if not isinstance(raw, list) or not 1 <= len(raw) <= 16:
        raise ValueError("Сертификат простоты повреждён")

    def number(value) -> int:
        result = int(str(value))
        if not 0 < result < 1 << (MAX_BITS + 1):
            raise ValueError
        return result

    chain = []
    try:
        for step in raw:
            if step.get("method") == "trial":
                chain.append({"p": number(step["p"]), "bits": int(step["bits"]), "method": "trial"})
                continue
            if step.get("method") != "pocklington" or len(step["r_factors"]) > 200:
                raise ValueError
            chain.append({
                "p": number(step["p"]), "bits": int(step["bits"]), "method": "pocklington",
                "q": number(step["q"]), "r": number(step["r"]), "a": number(step["a"]),
                "r_factors": [(number(prime), int(power)) for prime, power in step["r_factors"]],
                "attempts": int(step.get("attempts", 0)),
            })
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValueError("Сертификат простоты повреждён") from None
    return chain
