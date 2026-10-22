from transmission.huffman import HuffmanCoder
from transmission.shannon_fano import ShannonFanoCoder
from transmission.hamming import HammingCoder, DEFAULT_VARIANT as HAMMING_DEFAULT_VARIANT
from transmission.hadamard import HadamardCoder, DEFAULT_VARIANT as HADAMARD_DEFAULT_VARIANT
from transmission.elgamal import ElGamalCoder


class Decoder:
    """Декодер сообщения."""

    def decode(
        self,
        encoded: str,
        algorithm: str = "reverse",
        codes: dict | None = None,
        variant: str | None = None,
        data_bit_length: int | None = None,
        keys: dict | None = None,
    ) -> dict:
        """Декодировать сообщение выбранным алгоритмом.

        variant — вариант кода Хэмминга ("74" или "1511") или Адамара
        ("8", "16", "32"), должен совпадать с тем, что использовался при
        кодировании. data_bit_length — сколько бит исходных данных реально
        значимы (остаток — дополнение нулями до целого числа блоков), тоже
        только для блочных кодов. keys — ключи Эль-Гамаля {"p", "g", "x"}
        (получателю для расшифрования нужен секретный x).

        Возвращает словарь с декодированным текстом. Для Хаффмана и
        Шеннона-Фано — с пошаговой трассировкой по битам. Для Хэмминга —
        со списком блоков, содержащих синдром и результат самоисправления.
        """
        if algorithm == "huffman":
            return HuffmanCoder().decode(encoded, codes or {})

        if algorithm == "shannon":
            return ShannonFanoCoder().decode(encoded, codes or {})

        if algorithm == "hamming":
            return HammingCoder(variant or HAMMING_DEFAULT_VARIANT).decode(encoded, data_bit_length=data_bit_length)

        if algorithm == "hadamard":
            return HadamardCoder(variant or HADAMARD_DEFAULT_VARIANT).decode(encoded, data_bit_length=data_bit_length)

        if algorithm == "elgamal":
            return ElGamalCoder(**(keys or {})).decode(encoded)

        return {
            "decoded": encoded[::-1],
            "steps": [],
        }