"""Алгоритмы: примеры из статей теории должны совпадать с тем, что считает лаборатория."""

import copy
import random

import pytest

from algebra.pocklington import generate_prime, parse_chain, verify_chain
from transmission.elgamal import ElGamalCoder, generate_large_keys
from transmission.hamming import HammingCoder
from transmission.huffman import HuffmanCoder
from transmission.shannon_fano import ShannonFanoCoder


def is_probable_prime(n: int) -> bool:
    """Независимая проверка Миллером–Рабином (для сверки с Поклингтоном)."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


@pytest.mark.parametrize("bits", [32, 33, 64, 127, 256, 512])
def test_generated_primes_are_prime_and_certified(bits):
    rng = random.Random(bits)
    for _ in range(5):
        result = generate_prime(bits, rng)
        p = result["p"]
        assert p.bit_length() == bits
        assert is_probable_prime(p)
        assert verify_chain(result["chain"])
        product = 1
        for prime, power in result["factors"]:
            product *= prime ** power
        assert product == p - 1


def test_certificate_survives_json_roundtrip():
    chain = generate_prime(128, random.Random(1))["chain"]
    as_strings = [{key: (str(value) if isinstance(value, int) else value) for key, value in step.items()} for step in chain]
    assert verify_chain(parse_chain(as_strings))


def test_tampered_certificates_are_rejected():
    chain = generate_prime(128, random.Random(2))["chain"]

    broken_link = copy.deepcopy(chain)
    broken_link[-1]["q"] += 2
    assert not verify_chain(broken_link)

    big_trial = copy.deepcopy(chain)
    big_trial[0] = {"p": 2 ** 61 - 1, "bits": 61, "method": "trial"}
    assert not verify_chain(big_trial)

    wrong_factors = copy.deepcopy(chain)
    wrong_factors[-1]["r_factors"] = [(2, 10 ** 6)]
    assert not verify_chain(wrong_factors)

    with pytest.raises(ValueError):
        parse_chain("not a chain")


def test_elgamal_article_example():
    coder = ElGamalCoder(23, 5, 6)
    assert coder.y == 8
    a, b = pow(5, 3, 23), pow(8, 3, 23) * 10 % 23
    assert (a, b) == (10, 14)
    assert coder.decode("(10,14)")["blocks"][0]["m"] == 10


def test_elgamal_large_keys_roundtrip():
    keys = generate_large_keys(128, random.Random(3))
    coder = ElGamalCoder(keys["p"], keys["g"], keys["x"], certificate=keys["certificate"])
    message = "Привет, мир!"
    assert coder.decode(coder.encode(message)["encoded"])["decoded"] == message


def test_elgamal_large_p_requires_certificate():
    keys = generate_large_keys(64, random.Random(4))
    with pytest.raises(ValueError):
        ElGamalCoder(keys["p"], keys["g"], keys["x"])


def test_hamming_article_example():
    coder = HammingCoder("74")
    assert coder._encode_chunk("1011")["codeword"] == "0110011"
    decoded = coder._decode_block("0110001")
    assert decoded["data_bits"] == "1011"


@pytest.mark.parametrize("coder", [HuffmanCoder, ShannonFanoCoder])
def test_prefix_codes_article_example(coder):
    result = coder().encode("абракадабра")
    assert len(result["encoded"]) == 23
    assert coder().decode(result["encoded"], result["codes"])["decoded"] == "абракадабра"
