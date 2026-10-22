"""Код Хэмминга: m битов чётности + (2^m - 1 - m) битов данных на блок.

Поддерживаются два варианта:
  - (7,4)   — m=3: 4 бита данных + 3 бита чётности, блок 7 бит;
  - (15,11) — m=4: 11 бит данных + 4 бита чётности, блок 15 бит.

Сообщение (UTF-8) превращается в сплошной поток бит, который режется на
блоки по k бит данных (при необходимости последний блок дополняется
нулями до полного k — длина "полезных" бит передаётся декодеру отдельно,
чтобы он знал, где обрезать дополнение). Каждый блок данных превращается
в кодовое слово длиной n = k + m. Декодер по m проверочным битам
вычисляет "синдром" — номер позиции, в которой случилась ошибка (0, если
ошибок нет) — и самостоятельно её исправляет, после чего восстанавливает
исходные k бит данных.

Нумерация битов внутри блока — с единицы (1..n), как принято в
классическом описании кода Хэмминга. Биты чётности стоят на позициях,
являющихся степенями двойки: 1, 2, 4, 8, ... Бит чётности p проверяет
все позиции, чей номер имеет установленный тот же бит в двоичной записи.
"""

import random
from typing import Optional

# m -> (n — длина блока, k — число бит данных, подпись для UI)
VARIANTS = {
    "74": {"m": 3, "block_size": 7, "data_bits": 4, "label": "Хэмминг (7,4)"},
    "1511": {"m": 4, "block_size": 15, "data_bits": 11, "label": "Хэмминг (15,11)"},
}

DEFAULT_VARIANT = "74"


def _is_power_of_two(position: int) -> bool:
    return position > 0 and (position & (position - 1)) == 0


def _parity_positions(block_size: int) -> list[int]:
    return [position for position in range(1, block_size + 1) if _is_power_of_two(position)]


def _data_positions(block_size: int) -> list[int]:
    return [position for position in range(1, block_size + 1) if not _is_power_of_two(position)]


def _covered_positions(parity_position: int, block_size: int) -> list[int]:
    """Все позиции (1..block_size), которые проверяет данный бит чётности (включая себя)."""
    return [position for position in range(1, block_size + 1) if position & parity_position]


class HammingCoder:
    """Кодирование и декодирование кодом Хэмминга с исправлением одиночной ошибки."""

    def __init__(self, variant: str = DEFAULT_VARIANT):
        config = VARIANTS.get(variant, VARIANTS[DEFAULT_VARIANT])
        self.variant = variant if variant in VARIANTS else DEFAULT_VARIANT
        self.block_size = config["block_size"]
        self.data_bits_count = config["data_bits"]
        self.parity_positions = _parity_positions(self.block_size)
        self.data_positions = _data_positions(self.block_size)

    def _encode_chunk(self, data_bits: str) -> dict:
        """Закодировать k бит данных в n-битное кодовое слово."""
        codeword = [None] * (self.block_size + 1)  # индекс 0 не используется

        for position, bit in zip(self.data_positions, data_bits):
            codeword[position] = bit

        parity_bits = {}
        for p in self.parity_positions:
            # При вычислении бита чётности его собственная позиция исключается —
            # мы как раз решаем, каким её сделать.
            value = 0
            for pos in _covered_positions(p, self.block_size):
                if pos != p:
                    value ^= int(codeword[pos])
            codeword[p] = str(value)
            parity_bits[str(p)] = str(value)

        codeword_bits = "".join(codeword[1:])

        return {
            "data_bits": data_bits,
            "parity_bits": parity_bits,
            "codeword": codeword_bits,
        }

    def _decode_block(self, received: str) -> dict:
        """Проверить и при необходимости исправить одно n-битное кодовое слово."""
        codeword = [None] + list(received)  # 1-индексация

        # Детали каждой проверки чётности — нужны не только чтобы посчитать
        # синдром, но и чтобы потом наглядно объяснить, как он получился
        # (какие проверки "не сошлись" и почему).
        checks = []
        syndrome = 0
        for p in self.parity_positions:
            covered = _covered_positions(p, self.block_size)
            # На приёме проверяем ВСЕ позиции, включая саму позицию бита чётности:
            # если ошибок не было, суммарный XOR по этому набору должен быть равен 0.
            value = 0
            for pos in covered:
                value ^= int(codeword[pos])
            checks.append({"parity_position": p, "covered_positions": covered, "result": value})
            if value != 0:
                syndrome += p

        corrected = list(received)
        error_position = syndrome  # 0 — ошибок не найдено, иначе номер позиции 1..n

        if error_position != 0 and error_position <= self.block_size:
            idx = error_position - 1
            corrected[idx] = "1" if corrected[idx] == "0" else "0"

        corrected_bits = "".join(corrected)
        corrected_indexed = [None] + list(corrected_bits)
        data_bits = "".join(corrected_indexed[pos] for pos in self.data_positions)

        return {
            "received": received,
            "checks": checks,
            "syndrome": syndrome,
            "error_position": error_position,
            "corrected": corrected_bits,
            "data_bits": data_bits,
        }

    def encode(self, message: str) -> dict:
        """Закодировать сообщение: UTF-8 → поток бит → блоки по k бит данных → код Хэмминга."""
        if not message:
            return {"encoded": "", "blocks": [], "data_bit_length": 0, "variant": self.variant}

        message_bytes = message.encode("utf-8")
        bit_stream = "".join(format(byte, "08b") for byte in message_bytes)
        data_bit_length = len(bit_stream)

        k = self.data_bits_count
        padding = (-data_bit_length) % k
        padded_stream = bit_stream + "0" * padding

        blocks = []
        bits = ""

        for chunk_index, i in enumerate(range(0, len(padded_stream), k)):
            chunk = padded_stream[i:i + k]
            block = self._encode_chunk(chunk)
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
        """Декодировать битовую строку блоками по n бит, исправляя одиночные ошибки.

        data_bit_length — сколько первых бит восстановленного потока данных
        реально относятся к сообщению (остальное — дополнение нулями до
        целого числа блоков на кодере). Если не передано, дополнение не
        отбрасывается.
        """
        if not bits:
            return {"decoded": "", "blocks": []}

        blocks = []
        data_chunks = []

        for i in range(0, len(bits), self.block_size):
            chunk = bits[i:i + self.block_size]
            if len(chunk) < self.block_size:
                break  # неполный блок — оборванные данные, дальше декодировать нечего

            result = self._decode_block(chunk)
            result["position_start"] = i
            result["position_end"] = i + self.block_size
            blocks.append(result)
            data_chunks.append(result["data_bits"])

        data_stream = "".join(data_chunks)
        if data_bit_length is not None:
            data_stream = data_stream[:data_bit_length]

        usable_length = len(data_stream) - (len(data_stream) % 8)
        byte_values = [
            int(data_stream[i:i + 8], 2)
            for i in range(0, usable_length, 8)
        ]

        try:
            decoded = bytes(byte_values).decode("utf-8")
        except UnicodeDecodeError:
            decoded = bytes(byte_values).decode("utf-8", errors="replace")

        return {
            "decoded": decoded,
            "blocks": blocks,
        }

    def inject_error(self, bits: str, block_index: int, bit_offset: int) -> str:
        """Испортить один бит в указанном блоке — симуляция ошибки при передаче.

        block_index — номер блока (с нуля), bit_offset — позиция внутри
        блока (0..block_size-1, соответствует позициям Хэмминга 1..n).
        """
        position = block_index * self.block_size + bit_offset
        if position < 0 or position >= len(bits):
            return bits

        chars = list(bits)
        chars[position] = "1" if chars[position] == "0" else "0"
        return "".join(chars)

    def random_error_position(self, block_count: int) -> Optional[tuple[int, int]]:
        """Выбрать случайные (номер блока, смещение бита) для демонстрации ошибки."""
        if block_count <= 0:
            return None
        return random.randrange(block_count), random.randrange(self.block_size)
    