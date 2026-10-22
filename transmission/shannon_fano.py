from collections import Counter
from typing import Optional

from transmission.prefix_tree import (
    TreeNode,
    build_codes,
    decode_with_codes,
    encode_with_codes,
    serialize_tree,
)


class ShannonFanoCoder:
    """Кодирование и декодирование методом Шеннона-Фано с пошаговой трассировкой.

    В отличие от Хаффмана дерево строится сверху вниз: список символов,
    отсортированный по убыванию частоты, на каждом шаге делится на две
    группы с максимально близкими суммами частот — левая получает "0",
    правая "1", и так рекурсивно.
    """

    def _build_tree(self, symbols: list[tuple[str, int]]) -> Optional[TreeNode]:
        if len(symbols) == 1:
            char, freq = symbols[0]
            return TreeNode(freq=freq, char=char)

        total = sum(freq for _, freq in symbols)

        # Ищем точку разреза, при которой суммы частот двух групп наиболее близки.
        split = 1
        best_diff = None
        running = 0
        for i in range(1, len(symbols)):
            running += symbols[i - 1][1]
            diff = abs(2 * running - total)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                split = i

        left = self._build_tree(symbols[:split])
        right = self._build_tree(symbols[split:])

        return TreeNode(freq=total, left=left, right=right)

    def encode(self, message: str, frequencies: Optional[dict] = None) -> dict:
        """Закодировать сообщение, вернуть биты, таблицу кодов, дерево и трассировку по символам.

        Если frequencies не задан, вес символа — число его вхождений в само
        сообщение. Если задан (например, из frequency.json) — используется
        он, но только для символов, реально встретившихся в сообщении.
        """
        if not message:
            return {"encoded": "", "codes": {}, "frequencies": {}, "steps": [], "tree": None}

        if frequencies is None:
            char_freqs = dict(Counter(message))
        else:
            char_freqs = frequencies

        # Сортировка по убыванию частоты; при равных частотах порядок
        # символов стабилен и совпадает с порядком их первого появления.
        symbols = sorted(char_freqs.items(), key=lambda item: item[1], reverse=True)

        root = self._build_tree(symbols)
        codes = build_codes(root)
        bits, steps = encode_with_codes(message, codes)

        return {
            "encoded": bits,
            "codes": codes,
            "frequencies": dict(char_freqs),
            "steps": steps,
            "tree": serialize_tree(root),
        }

    def decode(self, bits: str, codes: dict) -> dict:
        """Декодировать битовую строку по таблице кодов, вернуть текст и трассировку по битам."""
        return decode_with_codes(bits, codes)