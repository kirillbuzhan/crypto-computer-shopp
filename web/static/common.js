// Общие функции всех страниц сайта: адреса API с учётом префикса,
// экранирование HTML и оформление формул.

// Сайт может быть опубликован не с корня домена (ROOT_PATH, например
// "/crypto-lab"): префикс приходит в атрибуте data-root у <body>.
const APP_ROOT = (document.body.dataset.root || "").replace(/\/$/, "");

function apiUrl(path) {
    return `${APP_ROOT}/${path.replace(/^\//, "")}`;
}


function escapeHtml(text) {
    return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}


// --- Красивые формулы ---

// Сервер пишет формулы простым текстом: a^(n−1), g^k, s⁻¹, γ_3, (mod p).
// formatMath превращает их в HTML: степени — верхние индексы, индексы — нижние,
// однобуквенные латинские переменные — курсив. Текст предварительно экранируется.
const SUPERSCRIPT_CHARS = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁻": "−", "ˣ": "x", "ᵏ": "k", "ᵉ": "e", "ᵈ": "d", "ⁱ": "i", "ⁿ": "n", "ᵐ": "m", "ᵗ": "t",
};
const SUPERSCRIPT_RUN = new RegExp(`[${Object.keys(SUPERSCRIPT_CHARS).join("")}]+`, "g");
const EXPONENT_TOKEN = /^[0-9A-Za-zА-Яа-яα-ωΑ-Ωₐ-ₜ₀-₉]+/;

function matchingParen(text, start) {
    let depth = 0;
    for (let index = start; index < text.length; index++) {
        if (text[index] === "(") depth++;
        if (text[index] === ")" && --depth === 0) return index;
    }
    return -1;
}

// a^(…) и a^token → a<sup>…</sup>; внешние скобки показателя убираются,
// функция в показателе (a^φ(m)) захватывается вместе с аргументом.
function formatExponents(text) {
    let html = "";
    let index = 0;
    while (index < text.length) {
        const char = text[index];
        if (char !== "^") {
            html += char;
            index++;
            continue;
        }

        let exponent = null;
        let next = index + 1;
        if (text[next] === "(") {
            const close = matchingParen(text, next);
            if (close !== -1) {
                exponent = text.slice(next + 1, close);
                next = close + 1;
            }
        } else {
            const token = text.slice(next).match(EXPONENT_TOKEN);
            if (token) {
                exponent = token[0];
                next += exponent.length;
                if (text[next] === "(" && /[^0-9]$/.test(exponent)) {
                    const close = matchingParen(text, next);
                    if (close !== -1) {
                        exponent += text.slice(next, close + 1);
                        next = close + 1;
                    }
                }
            }
        }

        if (exponent === null) {
            html += char;
            index++;
            continue;
        }
        html += `<sup class="math-sup">${formatExponents(exponent)}</sup>`;
        index = next;
    }
    return html;
}

function formatMath(text) {
    let html = formatExponents(escapeHtml(text));

    html = html.replace(SUPERSCRIPT_RUN, (run) =>
        `<sup class="math-sup">${[...run].map((char) => SUPERSCRIPT_CHARS[char]).join("")}</sup>`);

    html = html.replace(/([A-Za-zα-ωΑ-Ω])_(?:\(([^()]*)\)|(\w+))/g,
        (match, base, group, word) => `${base}<sub class="math-sub">${group ?? word}</sub>`);

    // Курсив — только в тексте, не внутри тегов и HTML-сущностей.
    return html.split(/(<[^>]+>|&\w+;)/).map((part, index) => index % 2
        ? part
        : part.replace(/(?<![A-Za-zА-Яа-яЁё])([A-Za-z])(?![0-9A-Za-zА-Яа-яЁё])/g,
            '<i class="math-var">$1</i>')
    ).join("");
}


// Формулы в статьях пишутся простым текстом внутри <span class="f"> (строчная),
// <div class="f-block"> (выключная) или .f-text (обычный текст с формулами) —
// так страница читается и без JavaScript, а со скриптом выглядит как в учебнике.
function renderFormulas(root = document) {
    root.querySelectorAll(".f, .f-block, .f-text").forEach((element) => {
        if (element.dataset.rendered) return;
        element.innerHTML = formatMath(element.textContent);
        element.dataset.rendered = "1";
    });
}


function setupNavigation() {
    const toggle = document.getElementById("nav-toggle");
    const menu = document.getElementById("site-nav");
    if (!toggle || !menu) return;

    toggle.addEventListener("click", () => {
        const open = menu.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
    });
}


// Содержание статьи собирается из её заголовков h2.
function buildArticleContents() {
    const nav = document.getElementById("article-contents");
    if (!nav) return;

    const headings = nav.closest(".article").querySelectorAll("h2");
    if (headings.length < 3) return;

    const list = nav.querySelector("ol");
    headings.forEach((heading, index) => {
        if (!heading.id) heading.id = `section-${index + 1}`;
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent;
        item.appendChild(link);
        list.appendChild(item);
    });
    nav.hidden = false;
}


// Поиск по глоссарию справочника.
function setupGlossaryFilter() {
    const input = document.getElementById("glossary-filter");
    if (!input) return;

    const entries = [...document.querySelectorAll(".glossary-entry")];
    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        entries.forEach((entry) => {
            entry.hidden = query !== "" && !entry.textContent.toLowerCase().includes(query);
        });
    });
}


renderFormulas();
setupNavigation();
buildArticleContents();
setupGlossaryFilter();
