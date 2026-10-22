import heapq
from collections import Counter
from typing import Optional

from transmission.prefix_tree import (
    TreeNode,
    build_codes,
    decode_with_codes,
    encode_with_codes,
    serialize_tree,
)


class HuffmanCoder:
    """Кодирование и декодирование методом Хаффмана с пошаговой трассировкой.

    Строит дерево снизу вверх: два самых редких узла на каждом шаге
    объединяются в новый, пока не останется один — корень.
    """

    def _build_tree(self, char_freqs: dict) -> Optional[TreeNode]:
        # Каждый элемент кучи — (частота, порядковый номер, узел).
        # Порядковый номер даёт устойчивое сравнение при равных частотах
        # и попутно избавляет от необходимости сравнивать сами узлы.
        heap: list[tuple[int, int, TreeNode]] = []
        order = 0
        for char, freq in char_freqs.items():
            heap.append((freq, order, TreeNode(freq=freq, char=char)))
            order += 1
        heapq.heapify(heap)

        if len(heap) == 1:
            # Единственный символ — присваиваем ему код "0", завернув в корень.
            only_freq, _, only_node = heap[0]
            return TreeNode(freq=only_freq, left=only_node)

        while len(heap) > 1:
            freq_a, _, node_a = heapq.heappop(heap)
            freq_b, _, node_b = heapq.heappop(heap)
            merged = TreeNode(freq=freq_a + freq_b, left=node_a, right=node_b)
            heapq.heappush(heap, (freq_a + freq_b, order, merged))
            order += 1

        return heap[0][2] if heap else None

    def encode(self, message: str, frequencies: Optional[dict] = None) -> dict:
        """Закодировать сообщение, вернуть биты, таблицу кодов, дерево и трассировку по символам.

        Если frequencies не задан, вес каждого символа — число его вхождений
        в само сообщение (как раньше). Если задан — используется он: это
        позволяет строить дерево по внешней статистике (например, из
        frequency.json), а не по конкретному переданному тексту. В любом
        случае таблица включает только символы, реально встретившиеся
        в сообщении — иначе не для чего строить коды.
        """
        if not message:
            return {"encoded": "", "codes": {}, "frequencies": {}, "steps": [], "tree": None}

        if frequencies is None:
            char_freqs = dict(Counter(message))
        else:
            char_freqs = frequencies

        root = self._build_tree(char_freqs)
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