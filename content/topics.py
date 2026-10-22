"""Каталог разделов сайта: теория, связь с лабораторией, порядок навигации.

Текст каждой статьи лежит в шаблоне web/templates/theory/<slug>.html,
здесь — только метаданные, из которых строятся меню, главная страница,
оглавление теории и переходы «назад / далее».
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    slug: str
    title: str
    summary: str
    group: str
    lab: str | None = None          # ключ алгоритма в лаборатории (?algorithm=...)
    lab_title: str | None = None    # подпись алгоритма в лаборатории, если отличается


GROUPS = [
    ("basics", "Основы теории информации"),
    ("compression", "Эффективное кодирование (сжатие)"),
    ("correction", "Помехоустойчивое кодирование"),
    ("crypto", "Криптография"),
    ("algebra", "Алгебра и теория чисел"),
]

TOPICS = [
    Topic(
        "transmission-model", "Модель системы передачи информации",
        "Схема Шеннона: источник, кодер, канал, декодер, приёмник. Количество информации, энтропия, избыточность.",
        "basics", lab="reverse", lab_title="Переворачивание текста",
    ),
    Topic(
        "huffman", "Код Хаффмана",
        "Оптимальный префиксный код: дерево строится снизу вверх объединением двух самых редких узлов.",
        "compression", lab="huffman",
    ),
    Topic(
        "shannon-fano", "Код Шеннона–Фано",
        "Префиксный код «сверху вниз»: символы делятся на группы с близкими суммарными частотами.",
        "compression", lab="shannon",
    ),
    Topic(
        "hamming", "Код Хэмминга",
        "Линейный код, исправляющий одну ошибку: биты чётности на позициях 2ᵏ и синдром — номер ошибочного бита.",
        "correction", lab="hamming",
    ),
    Topic(
        "hadamard", "Код Адамара",
        "Код из строк матрицы Адамара: расстояние n/2, декодирование по максимуму корреляции.",
        "correction", lab="hadamard",
    ),
    Topic(
        "classical-ciphers", "Классические шифры",
        "Перестановка и замена, шифр Цезаря, частотный анализ. Принцип Керкгоффса.",
        "crypto", lab="reverse", lab_title="Переворачивание текста",
    ),
    Topic(
        "elgamal", "Шифр Эль-Гамаля",
        "Асимметричное шифрование на задаче дискретного логарифма: ключи, сеансовый ключ k, стойкость.",
        "crypto", lab="elgamal",
    ),
    Topic(
        "primality", "Простые числа и тесты простоты",
        "Пробное деление, тест Ферма, Миллер–Рабин и доказательство простоты по критерию Поклингтона.",
        "crypto", lab="elgamal", lab_title="Шифр Эль-Гамаля (генерация p)",
    ),
    Topic(
        "monoids", "Моноиды",
        "Множество с ассоциативной операцией и нейтральным элементом. Полугруппы, группы, примеры.",
        "algebra", lab="monoids",
    ),
    Topic(
        "diophantine", "Диофантовы уравнения",
        "Линейные уравнения в целых числах, расширенный алгоритм Евклида, соотношение Безу.",
        "algebra", lab="diophantine",
    ),
    Topic(
        "congruences", "Сравнения по модулю",
        "Арифметика остатков, быстрое возведение в степень, теоремы Эйлера и Ферма, китайская теорема.",
        "algebra", lab="congruences",
    ),
    Topic(
        "residues", "Вычеты и первообразные корни",
        "Кольцо ℤₘ, функция Эйлера, порядок элемента, первообразные корни, дискретный логарифм.",
        "algebra", lab="residues",
    ),
]

TOPICS_BY_SLUG = {topic.slug: topic for topic in TOPICS}


def grouped_topics() -> list[tuple[str, str, list[Topic]]]:
    return [(key, title, [topic for topic in TOPICS if topic.group == key]) for key, title in GROUPS]


def neighbours(slug: str) -> tuple[Topic | None, Topic | None]:
    index = next(i for i, topic in enumerate(TOPICS) if topic.slug == slug)
    previous = TOPICS[index - 1] if index > 0 else None
    following = TOPICS[index + 1] if index + 1 < len(TOPICS) else None
    return previous, following


# Ключ алгоритма лаборатории → статьи теории (первая — основная).
LAB_THEORY = {
    "reverse": ["classical-ciphers", "transmission-model"],
    "huffman": ["huffman", "transmission-model"],
    "shannon": ["shannon-fano", "huffman"],
    "hamming": ["hamming"],
    "hadamard": ["hadamard", "hamming"],
    "elgamal": ["elgamal", "primality", "residues"],
    "monoids": ["monoids"],
    "diophantine": ["diophantine"],
    "congruences": ["congruences"],
    "residues": ["residues"],
}

LAB_ALGORITHMS = set(LAB_THEORY)


def lab_theory_links() -> dict[str, list[dict]]:
    """Для фронтенда лаборатории: алгоритм → [{slug, title}, ...]."""
    return {
        algorithm: [{"slug": slug, "title": TOPICS_BY_SLUG[slug].title} for slug in slugs]
        for algorithm, slugs in LAB_THEORY.items()
    }
