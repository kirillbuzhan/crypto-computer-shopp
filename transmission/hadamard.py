"""Код Адамара (расширенный код Адамара, он же код Рида-Маллера 1-го порядка).

Строится по матрице Адамара H порядка n = 2^r (конструкция Сильвестра):
    H_1 = [1],   H_2n = [[H_n,  H_n],
                         [H_n, -H_n]].
Строки H попарно ортогональны: любые две различаются ровно в n/2 позициях.

Кодовые слова — все строки H и их инверсии (строки -H), итого 2n слов
длины n. Значит, одно слово несёт k = r + 1 бит данных:
  - старший бит данных — "бит знака": брать строку как есть или инвертировать;
  - остальные r бит — номер строки i в матрице.
Переводя +1 → "0", -1 → "1", бит j кодового слова равен
    знак XOR <i, j>   (скалярное произведение двоичных записей i и j по модулю 2).

Минимальное расстояние кода d = n/2, поэтому он исправляет до
t = (n/2 - 1) // 2 ошибок в блоке — гораздо больше, чем Хэмминг, ценой
большой избыточности.

Декодирование — по максимуму корреляции: принятый блок переводится
в ±1 и скалярно умножается на каждую строку H. Строка с наибольшим по
модулю значением и есть переданная, знак корреляции даёт бит знака,
а число ошибок в блоке = (n - |корреляция|) / 2.

Поддерживаемые варианты:
  - n=8  — 4 бита данных → 8 бит, исправляет 1 ошибку;
  - n=16 — 5 бит данных → 16 бит, исправляет 3 ошибки;
  - n=32 — 6 бит данных → 32 бита, исправляет 7 ошибок.

Как и в коде Хэмминга, сообщение (UTF-8) превращается в поток бит,
который режется на блоки по k бит (последний дополняется нулями,
длина полезных данных передаётся декодеру отдельно).
"""

import random
from typing import Optional

VARIANTS = {
    "8": {"order": 8, "data_bits": 4, "label": "Адамар (8,4)"},
    "16": {"order": 16, "data_bits": 5, "label": "Адамар (16,5)"},
    "32": {"order": 32, "data_bits": 6, "label": "Адамар (32,6)"},
}

DEFAULT_VARIANT = "8"


def build_hadamard_matrix(order: int) -> list[list[int]]:
    """Матрица Адамара порядка order (степень двойки) по конструкции Сильвестра."""
    matrix = [[1]]
    while len(matrix) < order:
        matrix = [row + row for row in matrix] + [row + [-value for value in row] for row in matrix]
    return matrix


def _row_to_bits(row: list[int]) -> str:
    return "".join("0" if value == 1 else "1" for value in row)


class HadamardCoder:
    """Кодирование и декодирование кодом Адамара с исправлением нескольких ошибок."""

    def __init__(self, variant: str = DEFAULT_VARIANT):
        self.variant = variant if variant in VARIANTS else DEFAULT_VARIANT
        config = VARIANTS[self.variant]
        self.block_size = config["order"]
        self.data_bits_count = config["data_bits"]
        self.min_distance = self.block_size // 2
        self.correctable_errors = (self.min_distance - 1) // 2
        self.matrix = build_hadamard_matrix(self.block_size)

    def _encode_chunk(self, data_bits: str) -> dict:
        """Закодировать k бит данных: бит знака + номер строки матрицы."""
        sign_bit = data_bits[0]
        row_index = int(data_bits[1:], 2)

        row_bits = _row_to_bits(self.matrix[row_index])
        if sign_bit == "1":
            codeword = "".join("1" if bit == "0" else "0" for bit in row_bits)
        else:
            codeword = row_bits

        return {
            "data_bits": data_bits,
            "sign_bit": sign_bit,
            "row_index": row_index,
            "codeword": codeword,
        }

    def _decode_block(self, received: str) -> dict:
        """Найти ближайшее кодовое слово по максимуму модуля корреляции."""
        signal = [1 if bit == "0" else -1 for bit in received]

        correlations = [
            sum(s * h for s, h in zip(signal, row))
            for row in self.matrix
        ]

        best_abs = max(abs(value) for value in correlations)
        candidates = [index for index, value in enumerate(correlations) if abs(value) == best_abs]
        # При равенстве нескольких кандидатов (слишком много ошибок) берём первую
        # строку и честно помечаем результат как неоднозначный.
        row_index = candidates[0]
        correlation = correlations[row_index]
        sign_bit = "0" if correlation > 0 else "1"

        row_width = self.data_bits_count - 1
        data_bits = sign_bit + format(row_index, f"0{row_width}b")
        corrected = self._encode_chunk(data_bits)["codeword"]

        error_positions = [
            position + 1
            for position, (got, fixed) in enumerate(zip(received, corrected))
            if got != fixed
        ]

        return {
            "received": received,
            "correlations": correlations,
            "row_index": row_index,
            "correlation": correlation,
            "sign_bit": sign_bit,
            "ambiguous": len(candidates) > 1,
            "error_positions": error_positions,
            "corrected": corrected,
            "data_bits": data_bits,
        }

    def encode(self, message: str) -> dict:
        """Закодировать сообщение: UTF-8 → поток бит → блоки по k бит → слова длины n."""
        if not message:
            return {"encoded": "", "blocks": [], "data_bit_length": 0, "variant": self.variant}

        bit_stream = "".join(format(byte, "08b") for byte in message.encode("utf-8"))
        data_bit_length = len(bit_stream)

        k = self.data_bits_count
        padded_stream = bit_stream + "0" * ((-data_bit_length) % k)

        blocks = []
        bits = ""

        for chunk_index, i in enumerate(range(0, len(padded_stream), k)):
            block = self._encode_chunk(padded_stream[i:i + k])
            block["chunk_index"] = chunk_index
            block["position_start"] = len(bits)
            bits += block["codeword"]
            block["position_end"] = len(bits)
            blocks.append(block)

        return {
            "encoded": bits,
            "blocks": blocks,
            "data_bit_length": data_bit_length,
            "variant": self.variant,
        }

    def decode(self, bits: str, data_bit_length: Optional[int] = None) -> dict:
        """Декодировать битовую строку блоками по n бит, исправляя до t ошибок в каждом."""
        if not bits:
            return {"decoded": "", "blocks": []}

        blocks = []
        data_chunks = []

        for i in range(0, len(bits), self.block_size):
            chunk = bits[i:i + self.block_size]
            if len(chunk) < self.block_size:
                break

            result = self._decode_block(chunk)
            result["position_start"] = i
            result["position_end"] = i + self.block_size
            blocks.append(result)
            data_chunks.append(result["data_bits"])

        data_stream = "".join(data_chunks)
        if data_bit_length is not None:
            data_stream = data_stream[:data_bit_length]

        usable_length = len(data_stream) - (len(data_stream) % 8)
        byte_values = bytes(int(data_stream[i:i + 8], 2) for i in range(0, usable_length, 8))

        return {
            "decoded": byte_values.decode("utf-8", errors="replace"),
            "blocks": blocks,
        }

    def inject_errors(self, bits: str, block_index: int, offsets: list[int]) -> str:
        """Инвертировать указанные биты (смещения 0..n-1) в одном блоке."""
        chars = list(bits)
        for offset in offsets:
            position = block_index * self.block_size + offset
            if 0 <= position < len(chars):
                chars[position] = "1" if chars[position] == "0" else "0"
        return "".join(chars)

    def random_error_positions(self, block_count: int, error_count: int) -> Optional[tuple[int, list[int]]]:
        """Выбрать случайный блок и error_count различных позиций в нём."""
        if block_count <= 0 or error_count <= 0:
            return None
        error_count = min(error_count, self.block_size)
        offsets = sorted(random.sample(range(self.block_size), error_count))
        return random.randrange(block_count), offsets
