from collections import Counter
from typing import Optional

from transmission.prefix_tree import (
    TreeNode,
    build_codes,
    decode_with_codes,
    encode_with_codes,
    prune_tree,
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
        сообщение. Если задан (например, из frequency.json) — дерево
        строится по всему алфавиту таблицы, а в ответ попадают только
        символы сообщения: их коды, частоты и ветви дерева. Все символы
        сообщения должны быть в таблице.
        """
        if not message:
            return {"encoded": "", "codes": {}, "frequencies": {}, "steps": [], "tree": None}

        if frequencies is None:
            char_freqs = dict(Counter(message))
        else:
            char_freqs = frequencies

        # Сортировка по убыванию частоты; при равных частотах порядок
        # символов стабилен: порядок первого появления в сообщении
        # или порядок в переданной таблице частот.
        symbols = sorted(char_freqs.items(), key=lambda item: item[1], reverse=True)

        root = self._build_tree(symbols)
        codes = build_codes(root)
        bits, steps = encode_with_codes(message, codes)

        # Код построен по всему алфавиту таблицы, а показываем только
        # символы сообщения: их коды, частоты и ветви дерева.
        used = set(message)
        if frequencies is not None:
            root = prune_tree(root, used)

        return {
            "encoded": bits,
            "codes": {char: code for char, code in codes.items() if char in used},
            "frequencies": {char: freq for char, freq in char_freqs.items() if char in used},
            "alphabet_size": len(char_freqs),
            "steps": steps,
            "tree": serialize_tree(root),
        }

    def decode(self, bits: str, codes: dict) -> dict:
        """Декодировать битовую строку по таблице кодов, вернуть текст и трассировку по битам."""
        return decode_with_codes(bits, codes)