from typing import Optional

from transmission.huffman import HuffmanCoder
from transmission.shannon_fano import ShannonFanoCoder
from transmission.hamming import HammingCoder, DEFAULT_VARIANT as HAMMING_DEFAULT_VARIANT
from transmission.hadamard import HadamardCoder, DEFAULT_VARIANT as HADAMARD_DEFAULT_VARIANT
from transmission.elgamal import ElGamalCoder


class Encoder:
    """Кодер сообщения."""

    def encode(
        self,
        message: str,
        algorithm: str = "reverse",
        frequencies: Optional[dict] = None,
        variant: Optional[str] = None,
        keys: Optional[dict] = None,
    ) -> dict:
        """Закодировать сообщение выбранным алгоритмом.

        frequencies — необязательная внешняя таблица частот символов
        (например, из frequency.json). Используется только алгоритмами
        на основе префиксных кодов (Хаффман, Шеннон-Фано); если не
        задана, частоты считаются по самому сообщению.

        variant — вариант кода Хэмминга ("74" или "1511") или Адамара
        ("8", "16", "32"); игнорируется остальными алгоритмами.

        keys — ключи Эль-Гамаля {"p", "g", "x"}; только для "elgamal".

        Возвращает словарь с закодированными данными. Для Хаффмана и
        Шеннона-Фано — таблица кодов, дерево и трассировка. Для Хэмминга —
        список блоков и длину полезных данных (для обрезки дополнения
        при декодировании) вместо кодов/дерева.
        """
        if algorithm == "huffman":
            return HuffmanCoder().encode(message, frequencies=frequencies)

        if algorithm == "shannon":
            return ShannonFanoCoder().encode(message, frequencies=frequencies)

        if algorithm == "hamming":
            return HammingCoder(variant or HAMMING_DEFAULT_VARIANT).encode(message)

        if algorithm == "hadamard":
            return HadamardCoder(variant or HADAMARD_DEFAULT_VARIANT).encode(message)

        if algorithm == "elgamal":
            return ElGamalCoder(**(keys or {})).encode(message)

        return {
            "encoded": message[::-1],
            "codes": {},
            "frequencies": {},
            "steps": [],
            "tree": None,
        }