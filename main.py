"""Веб-приложение: страницы сайта (главная, лаборатория, теория, справочник)
и JSON API, которое вызывает лаборатория.

Запуск локально:   python launcher.py   (или uvicorn main:app --reload)
Развёртывание:     см. README.md (Docker, nginx, ROOT_PATH).
"""

import json

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import config
from content.reference import FORMULAS, GLOSSARY, LITERATURE, NOTATION
from content.topics import LAB_ALGORITHMS, TOPICS, TOPICS_BY_SLUG, grouped_topics, lab_theory_links, neighbours

from transmission.source import Source
from transmission.encoder import Encoder
from transmission.decoder import Decoder
from transmission.receiver import Receiver
from transmission.hamming import HammingCoder, VARIANTS as HAMMING_VARIANTS, DEFAULT_VARIANT as HAMMING_DEFAULT_VARIANT
from transmission.hadamard import HadamardCoder, VARIANTS as HADAMARD_VARIANTS, DEFAULT_VARIANT as HADAMARD_DEFAULT_VARIANT
from transmission.elgamal import ElGamalCoder, generate_keys as generate_elgamal_keys, generate_large_keys
from algebra.monoids import MonoidDemo, create_monoid
from algebra.diophantine import solve_diophantine
from algebra.congruences import solve_congruence_example
from algebra.residues import solve_residue_example


app = FastAPI(
    title=config.SITE_TITLE,
    root_path=config.ROOT_PATH,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount(
    "/static",
    StaticFiles(directory=config.STATIC_DIR),
    name="static",
)

templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# Таблица упорядочена по символам: при равных частотах дерево строится
# одинаково на любом сервере, независимо от порядка ключей в файле.
with config.FREQUENCY_FILE.open("r", encoding="utf-8") as frequency_file:
    FREQUENCY_TABLE: dict = dict(sorted(json.load(frequency_file).items()))


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "SAMEORIGIN",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'; "
        "frame-ancestors 'self'"
    ),
}


class EnsureRootPathPrefix:
    """Сайт за прокси с префиксом (ROOT_PATH): одни прокси передают путь целиком
    (/crypto-lab/theory), другие отрезают префикс (/theory). По спецификации ASGI
    путь должен включать root_path — дописываем префикс, если его отрезали,
    иначе маршруты ещё найдутся, а статические файлы — уже нет."""

    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        root = scope.get("root_path", "")
        path = scope.get("path", "")
        if scope["type"] in ("http", "websocket") and root and path != root and not path.startswith(root + "/"):
            scope = dict(scope, path=root + path, raw_path=root.encode() + (scope.get("raw_path") or path.encode()))
        await self.app(scope, receive, send)


app.add_middleware(EnsureRootPathPrefix)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


def render(request: Request, name: str, status_code: int = 200, **context) -> HTMLResponse:
    """Шаблон страницы с общими данными сайта (меню, префикс адресов, подвал)."""
    root = request.scope.get("root_path", "").rstrip("/")
    context.update(
        root=root,
        site={
            "title": config.SITE_TITLE,
            "subtitle": config.SITE_SUBTITLE,
            "organization": config.ORGANIZATION,
            "authors": config.AUTHORS,
            "email": config.CONTACT_EMAIL,
        },
        static_version=config.STATIC_VERSION,
        groups=grouped_topics(),
        current_path=request.url.path,
    )
    return templates.TemplateResponse(request=request, name=name, context=context, status_code=status_code)


class InputError(ValueError):
    """Ошибка ввода пользователя — отдаётся фронтенду с кодом 400."""


def _message_from(data: dict, limit: int) -> str:
    message = data.get("message")
    if not isinstance(message, str):
        raise InputError("Сообщение должно быть строкой")
    if not message:
        raise InputError("Введите сообщение")
    if len(message) > limit:
        raise InputError(f"Сообщение слишком длинное: не больше {limit} символов")
    return message


def resolve_frequencies(message: str, frequency_source: str) -> dict | None:
    """Определить таблицу частот для кодирования по выбранному источнику.

    "message" — вес символа = число его вхождений в само сообщение
    (по умолчанию); функция возвращает None, чтобы кодер сам посчитал
    частоты по тексту.

    "file" — вся таблица frequency.json: код строится по полному алфавиту
    файла, поэтому одинаковый текст кодируется одинаково у всех. Символы,
    которых в файле нет, закодировать нельзя — это ошибка ввода.
    """
    if frequency_source != "file":
        return None

    invalid_chars = sorted(set(message) - FREQUENCY_TABLE.keys())
    if invalid_chars:
        shown = ", ".join("␣" if char == " " else repr(char) for char in invalid_chars)
        raise InputError(
            f"Недопустимые символы для частот из frequency.json: {shown}. "
            "Разрешены русские буквы, цифры, пробел и знаки . , ; : ! ? - ( ) \" '"
        )

    return FREQUENCY_TABLE


# --- Страницы ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return render(request, "home.html", topics=TOPICS)


@app.get("/lab", response_class=HTMLResponse)
async def lab(request: Request, algorithm: str | None = None):
    return render(
        request, "lab.html",
        initial_algorithm=algorithm if algorithm in LAB_ALGORITHMS else "",
        theory_links=lab_theory_links(),
        max_message_length=config.MAX_MESSAGE_LENGTH,
    )


@app.get("/theory", response_class=HTMLResponse)
async def theory_index(request: Request):
    return render(request, "theory_index.html")


@app.get("/theory/{slug}", response_class=HTMLResponse)
async def theory_page(request: Request, slug: str):
    topic = TOPICS_BY_SLUG.get(slug)
    if topic is None:
        raise HTTPException(status_code=404)
    previous, following = neighbours(slug)
    return render(request, f"theory/{slug}.html", topic=topic, previous=previous, following=following)


@app.get("/reference", response_class=HTMLResponse)
async def reference(request: Request):
    return render(
        request, "reference.html",
        glossary=sorted(GLOSSARY, key=lambda item: item[0].lower()),
        formulas=FORMULAS, notation=NOTATION, literature=LITERATURE,
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return render(request, "about.html")


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return PlainTextResponse("ok")


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, error: StarletteHTTPException):
    wants_html = request.method == "GET" and "text/html" in request.headers.get("accept", "")
    if wants_html and error.status_code == 404:
        return render(request, "404.html", status_code=404)
    return JSONResponse({"error": error.detail}, status_code=error.status_code)


@app.exception_handler(InputError)
async def input_error(request: Request, error: InputError):
    return JSONResponse({"error": str(error)}, status_code=400)


# --- API лаборатории ---

@app.post("/transmit")
async def transmit(data: dict):
    algorithm = data.get("algorithm", "reverse")
    if algorithm not in LAB_ALGORITHMS:
        raise InputError("Неизвестный алгоритм")

    limit = config.MAX_ELGAMAL_MESSAGE_LENGTH if algorithm == "elgamal" else config.MAX_MESSAGE_LENGTH
    source = Source(_message_from(data, limit))
    encoder = Encoder()
    decoder = Decoder()
    receiver = Receiver()

    message = source.generate()

    if algorithm == "hamming":
        return _transmit_hamming(message, data, encoder, decoder, receiver)

    if algorithm == "hadamard":
        return _transmit_hadamard(message, data, encoder, decoder, receiver)

    if algorithm == "elgamal":
        return _transmit_elgamal(message, data, encoder, decoder, receiver)

    # Частоты из файла имеют смысл только для префиксных кодов.
    frequency_source = data.get("frequency_source", "message") if algorithm in ("huffman", "shannon") else "message"
    frequencies = resolve_frequencies(message, frequency_source)

    encode_result = encoder.encode(message, algorithm=algorithm, frequencies=frequencies)
    decode_result = decoder.decode(
        encode_result["encoded"],
        algorithm=algorithm,
        codes=encode_result["codes"],
    )

    receiver.receive(decode_result["decoded"])

    return JSONResponse(
        {
            "algorithm": algorithm,
            "frequency_source": frequency_source,
            "alphabet_size": encode_result.get("alphabet_size", 0),
            "source": message,
            "encoded": encode_result["encoded"],
            "decoded": decode_result["decoded"],
            "receiver": receiver.message,
            "codes": encode_result["codes"],
            "frequencies": encode_result["frequencies"],
            "encode_steps": encode_result["steps"],
            "decode_steps": decode_result["steps"],
            "tree": encode_result["tree"],
        }
    )


@app.post("/monoid")
async def monoid(data: dict):
    """Свёртка введённых элементов в выбранном моноиде и проверка его аксиом.

    Элементы приходят одной строкой через запятую; ошибки разбора
    (не число, разная длина векторов и т.п.) возвращаются с кодом 400.
    """
    raw = str(data.get("elements", ""))
    raw_elements = [item.strip() for item in raw.split(",")] if raw.strip() else []

    try:
        modulus = None
        if data.get("modulus") not in (None, ""):
            try:
                modulus = int(data["modulus"])
            except (TypeError, ValueError):
                raise ValueError("Модуль n должен быть целым числом") from None

        monoid_example = create_monoid(str(data.get("example", "")), modulus)
        result = MonoidDemo(monoid_example).run(raw_elements)
    except (TypeError, ValueError) as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(result)


@app.post("/diophantine")
async def diophantine(data: dict):
    """Решение выбранного диофантова уравнения с пошаговым разбором.

    Параметры (коэффициенты, модуль, p/q/e и т.д.) приходят словарём
    "params"; ошибки ввода возвращаются с кодом 400.
    """
    params = data.get("params")
    if not isinstance(params, dict):
        params = {}

    try:
        result = solve_diophantine(str(data.get("example", "")), params)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(result)


@app.post("/congruences")
async def congruences(data: dict):
    """Пошаговое решение выбранного примера на сравнения по модулю.

    Формат запроса и ответа — как у /diophantine.
    """
    params = data.get("params")
    if not isinstance(params, dict):
        params = {}

    try:
        result = solve_congruence_example(str(data.get("example", "")), params)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(result)


@app.post("/residues")
async def residues(data: dict):
    """Пошаговый разбор выбранного примера на вычеты.

    Формат запроса и ответа — как у /diophantine и /congruences.
    """
    params = data.get("params")
    if not isinstance(params, dict):
        params = {}

    try:
        result = solve_residue_example(str(data.get("example", "")), params)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    return JSONResponse(result)


JS_SAFE_INTEGER = 2 ** 53 - 1


def _json_safe(value):
    """Большие целые → строки: JavaScript хранит числа как double и потерял бы цифры."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return str(value) if abs(value) > JS_SAFE_INTEGER else value
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


@app.post("/elgamal/keys")
async def elgamal_keys(data: dict):
    """Ключи Эль-Гамаля: учебные (маленькое p под сообщение) или с большим
    простым p заданной битности, доказанным по критерию Поклингтона."""
    if data.get("bits") in (None, ""):
        return JSONResponse(generate_elgamal_keys(str(data.get("message", ""))))

    try:
        bits = int(str(data["bits"]).strip())
    except ValueError:
        return JSONResponse({"error": "Размер p должен быть целым числом бит"}, status_code=400)

    try:
        keys = generate_large_keys(bits)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    return JSONResponse(_json_safe(keys))


def _parse_elgamal_keys(data: dict) -> dict:
    keys = data.get("keys") if isinstance(data.get("keys"), dict) else {}
    parsed = {}
    for name, label in (("p", "p"), ("g", "g"), ("x", "секретный ключ x")):
        text = str(keys.get(name, "")).strip()
        if len(text) > 400:
            raise ValueError(f"Параметр {label} слишком длинный")
        try:
            parsed[name] = int(text)
        except ValueError:
            raise ValueError(f"Параметр {label} должен быть целым числом") from None
    if keys.get("certificate"):
        parsed["certificate"] = keys["certificate"]
    return parsed


def _transmit_elgamal(message: str, data: dict, encoder: Encoder, decoder: Decoder, receiver: Receiver) -> JSONResponse:
    """Ветка для шифра Эль-Гамаля: ключи (p, g, x) приходят с фронтенда,
    кодер шифрует символы парами (a, b), декодер расшифровывает секретным x.
    Ошибки ключей (p не простое, g не первообразный корень, p ≤ кода символа)
    возвращаются с кодом 400 и понятным текстом.
    """
    try:
        keys = _parse_elgamal_keys(data)
        encode_result = encoder.encode(message, algorithm="elgamal", keys=keys)
    except ValueError as error:
        return JSONResponse({"error": str(error)}, status_code=400)

    decode_result = decoder.decode(encode_result["encoded"], algorithm="elgamal", keys=keys)
    receiver.receive(decode_result["decoded"])

    coder = ElGamalCoder(**keys)
    return JSONResponse(_json_safe(
        {
            "algorithm": "elgamal",
            "source": message,
            "encoded": encode_result["encoded"],
            "decoded": decode_result["decoded"],
            "receiver": receiver.message,
            "keys": coder.keys,
            "sections": coder.sections(encode_result, decode_result),
        }
    ))


def _transmit_hamming(message: str, data: dict, encoder: Encoder, decoder: Decoder, receiver: Receiver) -> JSONResponse:
    """Отдельная ветка для кода Хэмминга: другая форма ответа (блоки, а не коды/дерево)
    плюс выбор варианта (7,4)/(15,11) и необязательная симуляция ошибки при
    передаче для демонстрации самоисправления.
    """
    variant = data.get("variant", HAMMING_DEFAULT_VARIANT)
    if variant not in HAMMING_VARIANTS:
        variant = HAMMING_DEFAULT_VARIANT

    simulate_error = bool(data.get("simulate_error", False))
    coder = HammingCoder(variant)

    encode_result = encoder.encode(message, algorithm="hamming", variant=variant)
    clean_bits = encode_result["encoded"]
    block_size = coder.block_size

    transmitted_bits = clean_bits
    error_info = {
        "injected": False,
        "block_index": None,
        "bit_offset": None,
        "global_position": None,
    }

    if simulate_error:
        choice = coder.random_error_position(len(encode_result["blocks"]))
        if choice is not None:
            block_index, bit_offset = choice
            transmitted_bits = coder.inject_error(clean_bits, block_index, bit_offset)
            error_info = {
                "injected": True,
                "block_index": block_index,
                "bit_offset": bit_offset,
                "global_position": block_index * block_size + bit_offset,
            }

    decode_result = decoder.decode(
        transmitted_bits,
        algorithm="hamming",
        variant=variant,
        data_bit_length=encode_result["data_bit_length"],
    )
    receiver.receive(decode_result["decoded"])

    return JSONResponse(
        {
            "algorithm": "hamming",
            "variant": variant,
            "block_size": block_size,
            "source": message,
            "encoded": clean_bits,
            "transmitted": transmitted_bits,
            "decoded": decode_result["decoded"],
            "receiver": receiver.message,
            "encode_blocks": encode_result["blocks"],
            "decode_blocks": decode_result["blocks"],
            "error": error_info,
        }
    )

def _transmit_hadamard(message: str, data: dict, encoder: Encoder, decoder: Decoder, receiver: Receiver) -> JSONResponse:
    """Ветка для кода Адамара: выбор порядка матрицы (8/16/32) и симуляция
    нескольких ошибок в одном блоке — чтобы показать, что код исправляет
    до t ошибок, а при большем их числе может ошибиться.
    """
    variant = data.get("variant", HADAMARD_DEFAULT_VARIANT)
    if variant not in HADAMARD_VARIANTS:
        variant = HADAMARD_DEFAULT_VARIANT

    coder = HadamardCoder(variant)
    block_size = coder.block_size

    simulate_error = bool(data.get("simulate_error", False))
    try:
        error_count = int(data.get("error_count", 1))
    except (TypeError, ValueError):
        error_count = 1
    error_count = max(1, min(error_count, block_size))

    encode_result = encoder.encode(message, algorithm="hadamard", variant=variant)
    clean_bits = encode_result["encoded"]

    transmitted_bits = clean_bits
    error_info = {
        "injected": False,
        "block_index": None,
        "bit_offsets": [],
        "global_positions": [],
    }

    if simulate_error:
        choice = coder.random_error_positions(len(encode_result["blocks"]), error_count)
        if choice is not None:
            block_index, offsets = choice
            transmitted_bits = coder.inject_errors(clean_bits, block_index, offsets)
            error_info = {
                "injected": True,
                "block_index": block_index,
                "bit_offsets": offsets,
                "global_positions": [block_index * block_size + offset for offset in offsets],
            }

    decode_result = decoder.decode(
        transmitted_bits,
        algorithm="hadamard",
        variant=variant,
        data_bit_length=encode_result["data_bit_length"],
    )
    receiver.receive(decode_result["decoded"])

    # Сервер знает исходные блоки, поэтому может честно отметить, где
    # декодер "исправил" ошибки неправильно (ошибок было больше t).
    for sent, got in zip(encode_result["blocks"], decode_result["blocks"]):
        got["decoded_correctly"] = sent["data_bits"] == got["data_bits"]

    return JSONResponse(
        {
            "algorithm": "hadamard",
            "variant": variant,
            "block_size": block_size,
            "data_bits": coder.data_bits_count,
            "min_distance": coder.min_distance,
            "correctable_errors": coder.correctable_errors,
            "matrix": coder.matrix,
            "source": message,
            "encoded": clean_bits,
            "transmitted": transmitted_bits,
            "decoded": decode_result["decoded"],
            "receiver": receiver.message,
            "encode_blocks": encode_result["blocks"],
            "decode_blocks": decode_result["blocks"],
            "error": error_info,
        }
    )
