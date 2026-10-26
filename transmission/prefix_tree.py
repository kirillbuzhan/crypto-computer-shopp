from dataclasses import dataclass
from typing import Optional


@dataclass
class TreeNode:
    """Узел бинарного дерева префиксного кода.

    Используется и Хаффманом, и Шенноном-Фано — оба строят бинарное
    дерево, где путь до листа (0 — влево, 1 — вправо) и есть код символа.
    """

    freq: int
    char: Optional[str] = None
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def build_codes(root: Optional[TreeNode]) -> dict:
    """Обойти дерево и построить таблицу кодов символ -> биты."""
    codes: dict[str, str] = {}

    def walk(node: Optional[TreeNode], path: str) -> None:
        if node is None:
            return
        if node.is_leaf():
            codes[node.char] = path or "0"
            return
        walk(node.left, path + "0")
        walk(node.right, path + "1")

    walk(root, "")
    return codes


def prune_tree(node: Optional[TreeNode], keep: set) -> Optional[TreeNode]:
    """Оставить в дереве только пути к листьям с символами из keep.

    Нужен, когда код построен по большому алфавиту (frequency.json), а
    показать надо лишь ветви символов сообщения. Коды оставшихся листьев
    не меняются: у внутреннего узла может остаться один потомок, но
    его ребро сохраняет свой бит (0 — влево, 1 — вправо).
    """
    if node is None:
        return None
    if node.is_leaf():
        return node if node.char in keep else None

    left = prune_tree(node.left, keep)
    right = prune_tree(node.right, keep)
    if left is None and right is None:
        return None
    return TreeNode(freq=node.freq, left=left, right=right)


def serialize_tree(node: Optional[TreeNode]) -> Optional[dict]:
    """Превратить дерево в JSON-совместимую структуру для визуализации."""
    if node is None:
        return None

    return {
        "freq": node.freq,
        "char": node.char,
        "left": serialize_tree(node.left),
        "right": serialize_tree(node.right),
    }


def encode_with_codes(message: str, codes: dict) -> tuple[str, list]:
    """Закодировать сообщение по готовой таблице кодов.

    Возвращает битовую строку и пошаговую трассировку (какой символ
    превратился в какие биты и на какой позиции).
    """
    steps = []
    bits = ""

    for char in message:
        code = codes[char]
        steps.append(
            {
                "char": char,
                "code": code,
                "position_start": len(bits),
                "position_end": len(bits) + len(code),
            }
        )
        bits += code

    return bits, steps


def decode_with_codes(bits: str, codes: dict) -> dict:
    """Декодировать битовую строку по таблице кодов.

    Возвращает текст и пошаговую трассировку (какая последовательность
    битов превратилась в какой символ и на какой позиции).
    """
    if not bits or not codes:
        return {"decoded": "", "steps": []}

    reverse_codes = {code: char for char, code in codes.items()}

    decoded_chars = []
    steps = []
    buffer = ""
    segment_start = 0

    for index, bit in enumerate(bits):
        buffer += bit
        if buffer in reverse_codes:
            char = reverse_codes[buffer]
            decoded_chars.append(char)
            steps.append(
                {
                    "bits": buffer,
                    "char": char,
                    "position_start": segment_start,
                    "position_end": index + 1,
                }
            )
            buffer = ""
            segment_start = index + 1

    return {
        "decoded": "".join(decoded_chars),
        "steps": steps,
    }