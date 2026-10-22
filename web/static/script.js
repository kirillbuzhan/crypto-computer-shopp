const transmitButton = document.getElementById("transmit-button");
const messageInput = document.getElementById("message");

const sourceMessage = document.getElementById("source-message");
const encodedMessage = document.getElementById("encoded-message");
const decodedMessage = document.getElementById("decoded-message");
const receiverMessage = document.getElementById("receiver-message");
const errorMessage = document.getElementById("error-message");

const algorithmOverlay = document.getElementById("algorithm-overlay");
const algorithmOptions = document.querySelectorAll(".algorithm-option");
const changeAlgorithmButton = document.getElementById("change-algorithm-button");
const currentAlgorithmLabel = document.getElementById("current-algorithm-label");

const codeSection = document.getElementById("code-section");
const codeSectionTitle = document.getElementById("code-section-title");
const codeCodesBody = document.getElementById("code-codes-body");
const encodeTrace = document.getElementById("encode-trace");
const encodeBitstring = document.getElementById("encode-bitstring");
const decodeTrace = document.getElementById("decode-trace");
const codeTreeWrap = document.getElementById("code-tree-wrap");
const frequencyNote = document.getElementById("frequency-note");

const frequencySourceRow = document.getElementById("frequency-source-row");
const frequencySourceOptions = document.querySelectorAll(".segmented-option[data-frequency-source]");

const hammingVariantRow = document.getElementById("hamming-variant-row");
const hammingVariantOptions = document.querySelectorAll(".segmented-option[data-hamming-variant]");

const hammingErrorRow = document.getElementById("hamming-error-row");
const simulateErrorCheckbox = document.getElementById("simulate-error-checkbox");

const hammingSection = document.getElementById("hamming-section");
const hammingSectionTitle = document.getElementById("hamming-section-title");
const hammingEncodeTitle = document.getElementById("hamming-encode-title");
const hammingEncodeBlocksWrap = document.getElementById("hamming-encode-blocks");
const hammingTransmissionWrap = document.getElementById("hamming-transmission");
const hammingErrorNote = document.getElementById("hamming-error-note");
const hammingDecodeBlocksWrap = document.getElementById("hamming-decode-blocks");

const hammingDetailOverlay = document.getElementById("hamming-detail-overlay");
const hammingDetailClose = document.getElementById("hamming-detail-close");
const hammingDetailTitle = document.getElementById("hamming-detail-title");
const hammingDetailBody = document.getElementById("hamming-detail-body");

const hadamardVariantRow = document.getElementById("hadamard-variant-row");
const hadamardVariantOptions = document.querySelectorAll(".segmented-option[data-hadamard-variant]");
const hadamardErrorRow = document.getElementById("hadamard-error-row");
const hadamardSimulateErrorCheckbox = document.getElementById("hadamard-simulate-error-checkbox");
const hadamardErrorCountInput = document.getElementById("hadamard-error-count");
const hadamardErrorHint = document.getElementById("hadamard-error-hint");

const hadamardSection = document.getElementById("hadamard-section");
const hadamardSectionTitle = document.getElementById("hadamard-section-title");
const hadamardMatrixTitle = document.getElementById("hadamard-matrix-title");
const hadamardParams = document.getElementById("hadamard-params");
const hadamardMatrixTable = document.getElementById("hadamard-matrix");
const hadamardEncodeTitle = document.getElementById("hadamard-encode-title");
const hadamardEncodeBlocksWrap = document.getElementById("hadamard-encode-blocks");
const hadamardTransmissionWrap = document.getElementById("hadamard-transmission");
const hadamardErrorNote = document.getElementById("hadamard-error-note");
const hadamardDecodeBlocksWrap = document.getElementById("hadamard-decode-blocks");

const elgamalKeyRow = document.getElementById("elgamal-key-row");
const elgamalPInput = document.getElementById("elgamal-p");
const elgamalGInput = document.getElementById("elgamal-g");
const elgamalXInput = document.getElementById("elgamal-x");
const elgamalGenerateButton = document.getElementById("elgamal-generate-button");
const elgamalBitsInput = document.getElementById("elgamal-bits");
const elgamalLargeButton = document.getElementById("elgamal-large-button");
const elgamalKeyHint = document.getElementById("elgamal-key-hint");
const elgamalSection = document.getElementById("elgamal-section");
const elgamalSectionsWrap = document.getElementById("elgamal-sections");

const transmissionView = document.getElementById("transmission-view");

const labRoot = document.getElementById("lab");
const theoryLinksWrap = document.getElementById("theory-links");
// алгоритм → [{slug, title}] — статьи теории, которые стоит прочитать
const THEORY_LINKS = JSON.parse(labRoot.dataset.theory || "{}");

const monoidSection = document.getElementById("monoid-section");
const diophantineSection = document.getElementById("diophantine-section");
const congruenceSection = document.getElementById("congruence-section");
const residueSection = document.getElementById("residue-section");

// Учебные разделы без схемы передачи: вместо источник → приёмник показываем примеры.
const STUDY_SECTIONS = new Set(["monoids", "diophantine", "congruences", "residues"]);
const monoidTabs = document.querySelectorAll("#monoid-tabs .monoid-tab");
const monoidExampleTitle = document.getElementById("monoid-example-title");
const monoidSignature = document.getElementById("monoid-signature");
const monoidExampleDesc = document.getElementById("monoid-example-desc");
const monoidProps = document.getElementById("monoid-props");
const monoidElementsInput = document.getElementById("monoid-elements");
const monoidModulusWrap = document.getElementById("monoid-modulus-wrap");
const monoidModulusInput = document.getElementById("monoid-modulus");
const monoidRunButton = document.getElementById("monoid-run-button");
const monoidInputHint = document.getElementById("monoid-input-hint");
const monoidError = document.getElementById("monoid-error");
const monoidResult = document.getElementById("monoid-result");
const monoidFold = document.getElementById("monoid-fold");
const monoidFoldResult = document.getElementById("monoid-fold-result");
const monoidChecks = document.getElementById("monoid-checks");
const monoidCayleyBlock = document.getElementById("monoid-cayley-block");
const monoidCayleyTitle = document.getElementById("monoid-cayley-title");
const monoidCayleyTable = document.getElementById("monoid-cayley");

const SVG_NS = "http://www.w3.org/2000/svg";

const ALGORITHM_LABELS = {
    reverse: "Переворачивание текста",
    huffman: "Код Хаффмана",
    shannon: "Код Шеннона-Фано",
    hamming: "Код Хэмминга",
    hadamard: "Код Адамара",
    elgamal: "Шифр Эль-Гамаля",
    monoids: "Моноиды",
    diophantine: "Диофантовы уравнения",
    congruences: "Сравнения",
    residues: "Вычеты",
};

// Параметры вариантов Хэмминга, которые нужны фронтенду для подписей
// (сами биты чётности определяются по номеру позиции — степень двойки —
// и не зависят от этой таблицы).
const HAMMING_VARIANT_LABELS = {
    "74": "Хэмминг (7,4)",
    "1511": "Хэмминг (15,11)",
};

// Порядок матрицы n -> число бит данных k и сколько ошибок исправляет блок
// (t = (n/2 - 1) // 2) — для подписей и подсказки у поля "сколько бит испортить".
const HADAMARD_VARIANTS = {
    "8": { label: "Адамар (8,4)", dataBits: 4, correctable: 1 },
    "16": { label: "Адамар (16,5)", dataBits: 5, correctable: 3 },
    "32": { label: "Адамар (32,6)", dataBits: 6, correctable: 7 },
};

// Алгоритмы, у которых есть таблица кодов, дерево и трассировка —
// для них показываем общий блок визуализации.
const CODE_ALGORITHMS = new Set(["huffman", "shannon"]);

let currentAlgorithm = null;
let currentFrequencySource = "message";
let currentHammingVariant = "74";
let currentHadamardVariant = "8";


function selectAlgorithm(algorithm) {
    currentAlgorithm = algorithm;

    currentAlgorithmLabel.textContent = ALGORITHM_LABELS[algorithm] || algorithm;
    changeAlgorithmButton.hidden = false;

    algorithmOverlay.hidden = true;

    frequencySourceRow.hidden = !CODE_ALGORITHMS.has(algorithm);
    hammingVariantRow.hidden = algorithm !== "hamming";
    hammingErrorRow.hidden = algorithm !== "hamming";
    hadamardVariantRow.hidden = algorithm !== "hadamard";
    hadamardErrorRow.hidden = algorithm !== "hadamard";
    elgamalKeyRow.hidden = algorithm !== "elgamal";

    if (!CODE_ALGORITHMS.has(algorithm)) {
        codeSection.hidden = true;
    }

    if (algorithm !== "hamming") {
        hammingSection.hidden = true;
    }

    if (algorithm !== "hadamard") {
        hadamardSection.hidden = true;
    }

    if (algorithm !== "elgamal") {
        elgamalSection.hidden = true;
    }

    // Учебные разделы (моноиды, диофантовы уравнения, сравнения, вычеты) — не алгоритмы передачи: вместо схемы
    // источник → приёмник показываем отдельный раздел с примерами.
    transmissionView.hidden = STUDY_SECTIONS.has(algorithm);
    monoidSection.hidden = algorithm !== "monoids";
    diophantineSection.hidden = algorithm !== "diophantine";
    congruenceSection.hidden = algorithm !== "congruences";
    residueSection.hidden = algorithm !== "residues";
    errorMessage.textContent = "";

    renderTheoryLinks(algorithm);

    // Адрес вида /lab?algorithm=huffman можно сохранить в закладки или дать студентам.
    const url = new URL(window.location.href);
    url.searchParams.set("algorithm", algorithm);
    window.history.replaceState(null, "", url);
}


function renderTheoryLinks(algorithm) {
    const links = THEORY_LINKS[algorithm] || [];
    theoryLinksWrap.innerHTML = "";
    theoryLinksWrap.hidden = links.length === 0;
    if (!links.length) return;

    const label = document.createElement("span");
    label.className = "theory-links-label";
    label.textContent = "Теория:";
    theoryLinksWrap.appendChild(label);

    links.forEach((link) => {
        const anchor = document.createElement("a");
        anchor.href = `${APP_ROOT}/theory/${link.slug}`;
        anchor.textContent = link.title;
        theoryLinksWrap.appendChild(anchor);
    });
}


algorithmOptions.forEach((button) => {
    button.addEventListener("click", () => {
        selectAlgorithm(button.dataset.algorithm);
    });
});


changeAlgorithmButton.addEventListener("click", () => {
    algorithmOverlay.hidden = false;
});


frequencySourceOptions.forEach((button) => {
    button.addEventListener("click", () => {
        currentFrequencySource = button.dataset.frequencySource;

        frequencySourceOptions.forEach((option) => {
            option.classList.toggle("active", option === button);
        });
    });
});


hammingVariantOptions.forEach((button) => {
    button.addEventListener("click", () => {
        currentHammingVariant = button.dataset.hammingVariant;

        hammingVariantOptions.forEach((option) => {
            option.classList.toggle("active", option === button);
        });
    });
});


function updateHadamardErrorHint() {
    const variant = HADAMARD_VARIANTS[currentHadamardVariant];
    const blockSize = Number(currentHadamardVariant);

    hadamardErrorCountInput.max = blockSize;
    if (Number(hadamardErrorCountInput.value) > blockSize) {
        hadamardErrorCountInput.value = blockSize;
    }

    const count = Number(hadamardErrorCountInput.value) || 1;
    const overLimit = count > variant.correctable;

    hadamardErrorHint.textContent = overLimit
        ? `Код n = ${blockSize} гарантированно исправляет до ${variant.correctable} ошибок в блоке — при ${count} декодирование может ошибиться.`
        : `Код n = ${blockSize} гарантированно исправляет до ${variant.correctable} ошибок в блоке.`;
    hadamardErrorHint.classList.toggle("over-limit", overLimit);
}


hadamardVariantOptions.forEach((button) => {
    button.addEventListener("click", () => {
        currentHadamardVariant = button.dataset.hadamardVariant;

        hadamardVariantOptions.forEach((option) => {
            option.classList.toggle("active", option === button);
        });

        updateHadamardErrorHint();
    });
});

hadamardErrorCountInput.addEventListener("input", updateHadamardErrorHint);

updateHadamardErrorHint();


// Биты чётности в коде Хэмминга всегда стоят на позициях-степенях двойки
// (1, 2, 4, 8, ...) — это работает для любого варианта (7,4)/(15,11) и т.д.,
// без необходимости знать конкретный размер блока.
function isHammingParityPosition(position) {
    return position > 0 && (position & (position - 1)) === 0;
}


function buildSvgEl(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
    return el;
}


// Раскладка дерева: x — по порядку листьев (in-order), y — по глубине.
// Работает для любого бинарного дерева префиксного кода — и Хаффмана,
// и Шеннона-Фано, поскольку обоим достаточно формы {freq, char, left, right}.
function computeTreeLayout(root) {
    const LEAF_GAP = 64;
    const LEVEL_GAP = 76;

    const nodes = [];
    const links = [];
    let leafIndex = 0;

    function assign(node, depth) {
        if (!node) {
            return null;
        }

        const isLeaf = node.left === null && node.right === null;
        const info = { freq: node.freq, char: node.char, depth, x: 0, isLeaf };
        nodes.push(info);

        if (isLeaf) {
            info.x = leafIndex * LEAF_GAP;
            leafIndex += 1;
            return info;
        }

        const leftInfo = assign(node.left, depth + 1);
        const rightInfo = assign(node.right, depth + 1);

        if (leftInfo && rightInfo) {
            info.x = (leftInfo.x + rightInfo.x) / 2;
            links.push({ from: info, to: leftInfo, bit: "0" });
            links.push({ from: info, to: rightInfo, bit: "1" });
        } else if (leftInfo) {
            info.x = leftInfo.x;
            links.push({ from: info, to: leftInfo, bit: "0" });
        } else if (rightInfo) {
            info.x = rightInfo.x;
            links.push({ from: info, to: rightInfo, bit: "1" });
        }

        return info;
    }

    assign(root, 0);

    const maxDepth = nodes.reduce((max, node) => Math.max(max, node.depth), 0);

    return { nodes, links, leafCount: Math.max(leafIndex, 1), maxDepth, LEAF_GAP, LEVEL_GAP };
}


function renderCodeTree(tree) {
    codeTreeWrap.innerHTML = "";

    if (!tree) {
        codeTreeWrap.textContent = "—";
        return;
    }

    const { nodes, links, leafCount, maxDepth, LEAF_GAP, LEVEL_GAP } = computeTreeLayout(tree);

    const PADDING = 30;
    const NODE_RADIUS = 20;
    const width = (leafCount - 1) * LEAF_GAP + PADDING * 2 + NODE_RADIUS * 2;
    const height = maxDepth * LEVEL_GAP + PADDING * 2 + NODE_RADIUS * 2;

    const svg = buildSvgEl("svg", {
        viewBox: `0 0 ${width} ${height}`,
        width: width,
        height: height,
        class: "code-tree-svg",
    });

    const toX = (x) => x + PADDING + NODE_RADIUS;
    const toY = (depth) => depth * LEVEL_GAP + PADDING + NODE_RADIUS;

    // Сначала рёбра, чтобы они были под узлами.
    links.forEach((link) => {
        const x1 = toX(link.from.x);
        const y1 = toY(link.from.depth);
        const x2 = toX(link.to.x);
        const y2 = toY(link.to.depth);

        svg.appendChild(buildSvgEl("line", { x1, y1, x2, y2, class: "tree-edge" }));

        const label = buildSvgEl("text", {
            x: (x1 + x2) / 2 + (link.bit === "0" ? -12 : 12),
            y: (y1 + y2) / 2 - 4,
            "text-anchor": "middle",
            class: "tree-edge-label",
        });
        label.textContent = link.bit;
        svg.appendChild(label);
    });

    nodes.forEach((node) => {
        const cx = toX(node.x);
        const cy = toY(node.depth);

        svg.appendChild(
            buildSvgEl("circle", {
                cx,
                cy,
                r: NODE_RADIUS,
                class: node.isLeaf ? "tree-node-circle tree-leaf-circle" : "tree-node-circle",
            })
        );

        if (node.isLeaf) {
            const charLabel = buildSvgEl("text", {
                x: cx,
                y: cy - 3,
                "text-anchor": "middle",
                class: "tree-char",
            });
            charLabel.textContent = node.char === " " ? "␣" : node.char;
            svg.appendChild(charLabel);
        }

        const freqLabel = buildSvgEl("text", {
            x: cx,
            y: cy + (node.isLeaf ? 12 : 4),
            "text-anchor": "middle",
            class: "tree-freq",
        });
        freqLabel.textContent = node.freq;
        svg.appendChild(freqLabel);
    });

    codeTreeWrap.appendChild(svg);
}


// Одна карточка блока: строка бит (1..7) с подсветкой чётности/испорченного бита.
function buildHammingBlockCard(options) {
    const card = document.createElement("div");
    card.className = "hamming-block-card" + (options.hasError ? " has-error" : "");

    const label = document.createElement("div");
    label.className = "hamming-block-label";
    label.textContent = options.label;
    card.appendChild(label);

    const row = document.createElement("div");
    row.className = "hamming-bit-row";

    for (let i = 0; i < options.bits.length; i += 1) {
        const position = i + 1; // Хэмминг нумерует позиции внутри блока с единицы.

        const bitWrap = document.createElement("div");
        bitWrap.className =
            "hamming-bit" +
            (isHammingParityPosition(position) ? " is-parity" : "") +
            (options.flippedPosition === position ? " is-flipped" : "");

        const valueEl = document.createElement("div");
        valueEl.className = "hamming-bit-value";
        valueEl.textContent = options.bits[i];

        const posEl = document.createElement("div");
        posEl.className = "hamming-bit-position";
        posEl.textContent = position;

        bitWrap.append(valueEl, posEl);
        row.appendChild(bitWrap);
    }

    card.appendChild(row);

    const footer = document.createElement("div");
    footer.className = "hamming-block-footer";
    footer.innerHTML = options.footerHtml;
    card.appendChild(footer);

    return card;
}


function renderHammingEncodeBlocks(blocks) {
    hammingEncodeBlocksWrap.innerHTML = "";

    blocks.forEach((block, index) => {
        const card = buildHammingBlockCard({
            label: `#${index}`,
            bits: block.codeword,
            flippedPosition: null,
            footerHtml: `данные: <b>${block.data_bits}</b>`,
        });
        card.style.animationDelay = `${index * 25}ms`;

        hammingEncodeBlocksWrap.appendChild(card);
    });
}


function renderHammingDecodeBlocks(blocks) {
    hammingDecodeBlocksWrap.innerHTML = "";

    blocks.forEach((block, index) => {
        const hasError = block.error_position !== 0;

        const footerHtml = hasError
            ? `синдром: <b>${block.syndrome}</b> → <span class="error-text">ошибка в позиции ${block.error_position}, исправлено</span>` +
              `<span class="detail-hint">нажмите для подробностей</span>`
            : `синдром: <b>0</b> → <span class="ok-text">ошибок нет</span>`;

        const card = buildHammingBlockCard({
            label: `#${index}`,
            bits: block.corrected,
            flippedPosition: hasError ? block.error_position : null,
            footerHtml,
            hasError,
        });
        card.style.animationDelay = `${index * 25}ms`;

        if (hasError) {
            card.classList.add("clickable");
            card.setAttribute("role", "button");
            card.setAttribute("tabindex", "0");

            const open = () => openHammingDetail(block, index);
            card.addEventListener("click", open);
            card.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    open();
                }
            });
        }

        hammingDecodeBlocksWrap.appendChild(card);
    });
}


// Строка из 7 клеток-бит для модалки с подробностями: может подсвечивать
// позицию ошибки и/или позиции, охваченные конкретной проверкой чётности.
function buildHammingBitStrip(bits7, options = {}) {
    const row = document.createElement("div");
    row.className = "hamming-bit-row hamming-detail-bit-row";

    const covered = new Set(options.coveredPositions || []);

    for (let i = 0; i < bits7.length; i += 1) {
        const position = i + 1;

        const bitWrap = document.createElement("div");
        bitWrap.className =
            "hamming-bit" +
            (isHammingParityPosition(position) ? " is-parity" : "") +
            (covered.has(position) ? " is-covered" : "") +
            (options.highlightPosition === position ? " is-flipped" : "");

        const valueEl = document.createElement("div");
        valueEl.className = "hamming-bit-value";
        valueEl.textContent = bits7[i];

        const posEl = document.createElement("div");
        posEl.className = "hamming-bit-position";
        posEl.textContent = position;

        bitWrap.append(valueEl, posEl);
        row.appendChild(bitWrap);
    }

    return row;
}


// Открыть модалку с разбором: где была ошибка и как декодер её нашёл и исправил.
function openHammingDetail(block, index) {
    hammingDetailTitle.textContent = `Блок #${index} — найдена и исправлена ошибка`;

    hammingDetailBody.innerHTML = "";

    // 1. Что пришло (с подсветкой испорченного бита).
    const receivedSection = document.createElement("div");
    receivedSection.className = "hamming-detail-section";

    const receivedTitle = document.createElement("h4");
    receivedTitle.textContent = "Получено (с ошибкой)";
    receivedSection.appendChild(receivedTitle);
    receivedSection.appendChild(
        buildHammingBitStrip(block.received, { highlightPosition: block.error_position })
    );

    hammingDetailBody.appendChild(receivedSection);

    // 2. Три проверки чётности — какие позиции охватывает каждая и сошлась ли она.
    const checksSection = document.createElement("div");
    checksSection.className = "hamming-detail-section";

    const checksTitle = document.createElement("h4");
    checksTitle.textContent = "Проверки чётности";
    checksSection.appendChild(checksTitle);

    block.checks.forEach((check) => {
        const failed = check.result !== 0;

        const checkRow = document.createElement("div");
        checkRow.className = "hamming-check-row" + (failed ? " check-failed" : "");

        const label = document.createElement("div");
        label.className = "hamming-check-label";
        label.innerHTML =
            `p<sub>${check.parity_position}</sub> проверяет позиции ${check.covered_positions.join(", ")} → ` +
            `XOR = <b>${check.result}</b> ` +
            (failed ? "— <b>не сошлось</b>" : "— сошлось");
        checkRow.appendChild(label);
        checkRow.appendChild(
            buildHammingBitStrip(block.received, { coveredPositions: check.covered_positions })
        );

        checksSection.appendChild(checkRow);
    });

    hammingDetailBody.appendChild(checksSection);

    // 3. Как из непройденных проверок складывается синдром = позиция ошибки.
    const syndromeSection = document.createElement("div");
    syndromeSection.className = "hamming-detail-section";

    const syndromeTitle = document.createElement("h4");
    syndromeTitle.textContent = "Синдром";
    syndromeSection.appendChild(syndromeTitle);

    const failedPositions = block.checks.filter((c) => c.result !== 0).map((c) => c.parity_position);

    const syndromeText = document.createElement("p");
    syndromeText.innerHTML =
        `Не сошлись проверки p<sub>${failedPositions.join("</sub>, p<sub>")}</sub>. ` +
        `Их номера складываются в синдром: ${failedPositions.join(" + ")} = <b>${block.syndrome}</b>. ` +
        `Значит, ошибка — ровно в позиции ${block.syndrome} (это и есть принцип Хэмминга: ` +
        `номер позиции однозначно восстанавливается из того, какие проверки не сошлись).`;
    syndromeSection.appendChild(syndromeText);

    hammingDetailBody.appendChild(syndromeSection);

    // 4. Исправленный результат.
    const fixedSection = document.createElement("div");
    fixedSection.className = "hamming-detail-section";

    const fixedTitle = document.createElement("h4");
    fixedTitle.textContent = "После исправления";
    fixedSection.appendChild(fixedTitle);
    fixedSection.appendChild(
        buildHammingBitStrip(block.corrected, { highlightPosition: block.error_position })
    );

    const fixedText = document.createElement("p");
    fixedText.innerHTML =
        `Бит в позиции ${block.error_position} инвертирован обратно. ` +
        `Восстановленные данные этого блока: <b>${block.data_bits}</b>.`;
    fixedSection.appendChild(fixedText);

    hammingDetailBody.appendChild(fixedSection);

    hammingDetailOverlay.hidden = false;
}


function closeHammingDetail() {
    hammingDetailOverlay.hidden = true;
}


hammingDetailClose.addEventListener("click", closeHammingDetail);

hammingDetailOverlay.addEventListener("click", (event) => {
    if (event.target === hammingDetailOverlay) {
        closeHammingDetail();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !hammingDetailOverlay.hidden) {
        closeHammingDetail();
    }
});


// Сравнение "отправлено" / "получено" с подсветкой испорченного при передаче бита.
function renderHammingTransmission(data) {
    hammingTransmissionWrap.innerHTML = "";

    const sentRow = document.createElement("div");
    sentRow.className = "hamming-transmission-row";

    const sentLabel = document.createElement("span");
    sentLabel.className = "transmission-label";
    sentLabel.textContent = "Отправлено:";

    const sentBits = document.createElement("span");
    sentBits.textContent = data.encoded || "—";

    sentRow.append(sentLabel, sentBits);

    const receivedRow = document.createElement("div");
    receivedRow.className = "hamming-transmission-row";

    const receivedLabel = document.createElement("span");
    receivedLabel.className = "transmission-label";
    receivedLabel.textContent = "Получено:";

    const receivedBits = document.createElement("span");

    if (data.error && data.error.injected && data.error.global_position !== null) {
        const position = data.error.global_position;
        const before = data.transmitted.slice(0, position);
        const flipped = data.transmitted[position];
        const after = data.transmitted.slice(position + 1);

        receivedBits.append(document.createTextNode(before));

        const flippedSpan = document.createElement("span");
        flippedSpan.className = "flipped-bit";
        flippedSpan.textContent = flipped;
        receivedBits.appendChild(flippedSpan);

        receivedBits.append(document.createTextNode(after));
    } else {
        receivedBits.textContent = data.transmitted || "—";
    }

    receivedRow.append(receivedLabel, receivedBits);

    hammingTransmissionWrap.append(sentRow, receivedRow);

    if (data.error && data.error.injected) {
        hammingErrorNote.textContent =
            `Канал испортил бит №${data.error.global_position} ` +
            `(блок ${data.error.block_index}, позиция ${data.error.bit_offset + 1} внутри блока).`;
        hammingErrorNote.hidden = false;
    } else {
        hammingErrorNote.hidden = true;
    }
}


function renderHammingVisualization(data) {
    const variantLabel = HAMMING_VARIANT_LABELS[data.variant] || "Хэмминг";
    const blockSize = data.block_size || (data.encode_blocks[0] ? data.encode_blocks[0].codeword.length : 0);
    const dataBitsCount = data.encode_blocks[0] ? data.encode_blocks[0].data_bits.length : 0;

    hammingSectionTitle.textContent = `Визуализация: ${variantLabel}`;
    hammingEncodeTitle.textContent =
        `Кодирование (${dataBitsCount} бит данных → ${blockSize}-битное слово)`;

    renderHammingEncodeBlocks(data.encode_blocks);
    renderHammingTransmission(data);
    renderHammingDecodeBlocks(data.decode_blocks);

    hammingSection.hidden = false;
}


function renderCodeVisualization(data) {
    codeSectionTitle.textContent = `Визуализация: ${ALGORITHM_LABELS[data.algorithm] || data.algorithm}`;

    if (data.frequency_missing_chars && data.frequency_missing_chars.length > 0) {
        const chars = data.frequency_missing_chars
            .map((char) => (char === " " ? "␣" : char))
            .join(", ");
        frequencyNote.textContent =
            `В frequency.json нет данных для символов: ${chars} — им присвоен вес 1.`;
        frequencyNote.hidden = false;
    } else {
        frequencyNote.hidden = true;
    }

    // Таблица кодов: символ, частота, код.
    codeCodesBody.innerHTML = "";

    Object.entries(data.codes).forEach(([char, code]) => {
        const row = document.createElement("tr");

        const charCell = document.createElement("td");
        charCell.className = "char-cell";
        charCell.textContent = char === " " ? "␣" : char;

        const freqCell = document.createElement("td");
        freqCell.textContent = data.frequencies[char];

        const codeCell = document.createElement("td");
        codeCell.className = "code-cell";
        codeCell.textContent = code;

        row.append(charCell, freqCell, codeCell);
        codeCodesBody.appendChild(row);
    });

    // Трассировка кодирования: каждый символ исходного сообщения -> его код.
    encodeTrace.innerHTML = "";

    data.encode_steps.forEach((step, index) => {
        const chip = document.createElement("div");
        chip.className = "trace-chip";
        chip.style.animationDelay = `${index * 40}ms`;

        const top = document.createElement("span");
        top.className = "chip-top";
        top.textContent = step.char === " " ? "␣" : step.char;

        const bottom = document.createElement("span");
        bottom.className = "chip-bottom";
        bottom.textContent = step.code;

        chip.title = `Позиция битов: ${step.position_start}–${step.position_end}`;

        chip.append(top, bottom);
        encodeTrace.appendChild(chip);
    });

    encodeBitstring.textContent = data.encoded || "—";

    // Трассировка декодирования: последовательность битов -> символ.
    decodeTrace.innerHTML = "";

    data.decode_steps.forEach((step, index) => {
        const chip = document.createElement("div");
        chip.className = "trace-chip decode-chip";
        chip.style.animationDelay = `${index * 40}ms`;

        const top = document.createElement("span");
        top.className = "chip-top";
        top.textContent = step.bits;

        const bottom = document.createElement("span");
        bottom.className = "chip-bottom";
        bottom.textContent = step.char === " " ? "␣" : step.char;

        chip.title = `Позиция битов: ${step.position_start}–${step.position_end}`;

        chip.append(top, bottom);
        decodeTrace.appendChild(chip);
    });

    renderCodeTree(data.tree);

    codeSection.hidden = false;
}


// --- Код Адамара ---

// Ряд бит блока Адамара (позиции 1..n) с подсветкой испорченных/исправленных бит.
function buildHadamardBitStrip(bits, highlightPositions = []) {
    const row = document.createElement("div");
    row.className = "hamming-bit-row hadamard-bits";

    const highlighted = new Set(highlightPositions);

    for (let i = 0; i < bits.length; i += 1) {
        const position = i + 1;

        const bitWrap = document.createElement("div");
        bitWrap.className = "hamming-bit" + (highlighted.has(position) ? " is-flipped" : "");

        const valueEl = document.createElement("div");
        valueEl.className = "hamming-bit-value";
        valueEl.textContent = bits[i];

        const posEl = document.createElement("div");
        posEl.className = "hamming-bit-position";
        posEl.textContent = position;

        bitWrap.append(valueEl, posEl);
        row.appendChild(bitWrap);
    }

    return row;
}


function buildHadamardCard(label, bits, highlightPositions, footerHtml) {
    const card = document.createElement("div");
    card.className = "hamming-block-card";

    const labelEl = document.createElement("div");
    labelEl.className = "hamming-block-label";
    labelEl.textContent = label;

    const footer = document.createElement("div");
    footer.className = "hamming-block-footer";
    footer.innerHTML = footerHtml;

    card.append(labelEl, buildHadamardBitStrip(bits, highlightPositions), footer);
    return card;
}


function makeCardClickable(card, onOpen) {
    card.classList.add("clickable");
    card.setAttribute("role", "button");
    card.setAttribute("tabindex", "0");

    card.addEventListener("click", onOpen);
    card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onOpen();
        }
    });
}


// Матрица Адамара: +1 / −1, строки, реально использованные при кодировании, выделены.
function renderHadamardMatrix(matrix, usedRows) {
    hadamardMatrixTable.innerHTML = "";

    const head = document.createElement("tr");
    head.appendChild(document.createElement("th"));
    matrix.forEach((_, column) => {
        const th = document.createElement("th");
        th.textContent = column + 1;
        head.appendChild(th);
    });
    hadamardMatrixTable.appendChild(head);

    matrix.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");
        if (usedRows.has(rowIndex)) {
            tr.className = "used";
        }

        const th = document.createElement("th");
        th.textContent = rowIndex;
        th.title = `Строка ${rowIndex} — номер ${rowIndex.toString(2)}₂`;
        tr.appendChild(th);

        row.forEach((value) => {
            const td = document.createElement("td");
            td.className = value === 1 ? "plus" : "minus";
            td.textContent = value === 1 ? "+" : "−";
            tr.appendChild(td);
        });

        hadamardMatrixTable.appendChild(tr);
    });
}


function renderHadamardEncodeBlocks(blocks) {
    hadamardEncodeBlocksWrap.innerHTML = "";

    blocks.forEach((block, index) => {
        const footerHtml =
            `данные: <b>${block.data_bits}</b><br>` +
            `знак <b>${block.sign_bit}</b> · строка <b>${block.row_index}</b>` +
            (block.sign_bit === "1" ? " (инвертирована)" : "");

        const card = buildHadamardCard(`#${index}`, block.codeword, [], footerHtml);
        card.style.animationDelay = `${index * 25}ms`;
        hadamardEncodeBlocksWrap.appendChild(card);
    });
}


function renderHadamardTransmission(data) {
    hadamardTransmissionWrap.innerHTML = "";

    const makeRow = (labelText, content) => {
        const row = document.createElement("div");
        row.className = "hamming-transmission-row";

        const label = document.createElement("span");
        label.className = "transmission-label";
        label.textContent = labelText;

        row.append(label, content);
        return row;
    };

    const sentBits = document.createElement("span");
    sentBits.textContent = data.encoded || "—";

    const receivedBits = document.createElement("span");
    const flipped = new Set(data.error.injected ? data.error.global_positions : []);

    if (flipped.size > 0) {
        for (let i = 0; i < data.transmitted.length; i += 1) {
            if (flipped.has(i)) {
                const span = document.createElement("span");
                span.className = "flipped-bit";
                span.textContent = data.transmitted[i];
                receivedBits.appendChild(span);
            } else {
                receivedBits.append(document.createTextNode(data.transmitted[i]));
            }
        }
    } else {
        receivedBits.textContent = data.transmitted || "—";
    }

    hadamardTransmissionWrap.append(makeRow("Отправлено:", sentBits), makeRow("Получено:", receivedBits));

    if (data.error.injected) {
        const positions = data.error.bit_offsets.map((offset) => offset + 1).join(", ");
        hadamardErrorNote.textContent =
            `Канал испортил ${data.error.bit_offsets.length} бит(а) в блоке ${data.error.block_index} ` +
            `(позиции ${positions} внутри блока).`;
        hadamardErrorNote.hidden = false;
    } else {
        hadamardErrorNote.hidden = true;
    }
}


function renderHadamardDecodeBlocks(data) {
    hadamardDecodeBlocksWrap.innerHTML = "";

    data.decode_blocks.forEach((block, index) => {
        const errorCount = block.error_positions.length;
        let statusHtml;

        if (!block.decoded_correctly) {
            statusHtml = `<span class="error-text">ошибок больше ${data.correctable_errors} — декодировано неверно</span>`;
        } else if (errorCount > 0) {
            statusHtml = `<span class="error-text">исправлено ошибок: ${errorCount}</span>`;
        } else {
            statusHtml = `<span class="ok-text">ошибок нет</span>`;
        }

        const footerHtml =
            `корреляция: <b>${block.correlation}</b> → строка ${block.row_index}<br>` + statusHtml;

        // Показываем пришедший блок: подсвечены биты, которые декодер счёл ошибочными.
        const card = buildHadamardCard(`#${index}`, block.received, block.error_positions, footerHtml);
        card.style.animationDelay = `${index * 25}ms`;

        if (!block.decoded_correctly) {
            card.classList.add("decode-failed");
        } else if (errorCount > 0) {
            card.classList.add("has-error");
        }

        makeCardClickable(card, () => openHadamardDetail(block, index, data));
        hadamardDecodeBlocksWrap.appendChild(card);
    });
}


// Модалка с разбором декодирования блока: корреляции со всеми строками матрицы.
function openHadamardDetail(block, index, data) {
    const n = data.block_size;
    const errorCount = block.error_positions.length;

    hammingDetailTitle.textContent = `Блок #${index} — декодирование кодом Адамара`;
    hammingDetailBody.innerHTML = "";

    const addSection = (title, ...children) => {
        const section = document.createElement("div");
        section.className = "hamming-detail-section";

        const heading = document.createElement("h4");
        heading.textContent = title;
        section.append(heading, ...children);

        hammingDetailBody.appendChild(section);
    };

    const paragraph = (html) => {
        const p = document.createElement("p");
        p.innerHTML = html;
        return p;
    };

    // 1. Что пришло.
    addSection(
        "Получено",
        buildHadamardBitStrip(block.received),
        paragraph("Каждый бит переводится в ±1: 0 → +1, 1 → −1.")
    );

    // 2. Корреляции со всеми строками.
    const bestAbs = Math.abs(block.correlation);
    const list = document.createElement("div");
    list.className = "correlation-list";

    block.correlations.forEach((value, rowIndex) => {
        const chip = document.createElement("div");
        chip.className = "correlation-chip";
        if (rowIndex === block.row_index) {
            chip.classList.add("best");
        } else if (Math.abs(value) === bestAbs) {
            chip.classList.add("tie");
        }

        const rowEl = document.createElement("span");
        rowEl.className = "corr-row";
        rowEl.textContent = `H${rowIndex}`;

        const valueEl = document.createElement("span");
        valueEl.className = "corr-value";
        valueEl.textContent = value > 0 ? `+${value}` : value;

        chip.append(rowEl, valueEl);
        list.appendChild(chip);
    });

    addSection(
        "Корреляция с каждой строкой матрицы",
        list,
        paragraph(
            `Скалярное произведение принятого блока на строку H<sub>i</sub>. Без ошибок оно равно ` +
            `±${n} для переданной строки и 0 для остальных (строки ортогональны). ` +
            `Каждая ошибка уменьшает модуль «правильной» корреляции на 2.`
        )
    );

    // 3. Решение.
    const signText = block.correlation > 0
        ? "положительна → бит знака 0 (строка как есть)"
        : "отрицательна → бит знака 1 (строка инвертирована)";

    let decisionHtml =
        `Максимум модуля — у строки <b>${block.row_index}</b> (|${block.correlation}| = ${bestAbs}). ` +
        `Корреляция ${signText}. ` +
        `Число ошибок = (n − |корреляция|) / 2 = (${n} − ${bestAbs}) / 2 = <b>${errorCount}</b>.`;

    if (block.ambiguous) {
        decisionHtml +=
            ` <span class="error-text">Несколько строк дали одинаковый максимум — ` +
            `ошибок слишком много, выбор неоднозначен.</span>`;
    }

    addSection("Решение", paragraph(decisionHtml));

    // 4. Результат.
    const resultChildren = [
        buildHadamardBitStrip(block.corrected, block.error_positions),
        paragraph(
            `Восстановленные данные: знак <b>${block.sign_bit}</b> + номер строки ` +
            `<b>${block.data_bits.slice(1)}</b>₂ = <b>${block.data_bits}</b>.`
        ),
    ];

    if (!block.decoded_correctly) {
        resultChildren.push(
            paragraph(
                `<b>Это неверный результат:</b> в блоке было больше ${data.correctable_errors} ошибок ` +
                `(минимальное расстояние кода d = ${data.min_distance}), поэтому принятое слово ` +
                `оказалось ближе к другому кодовому слову.`
            )
        );
    }

    addSection("После исправления", ...resultChildren);

    hammingDetailOverlay.hidden = false;
}


function renderHadamardVisualization(data) {
    const variant = HADAMARD_VARIANTS[data.variant];
    const usedRows = new Set(data.encode_blocks.map((block) => block.row_index));

    hadamardSectionTitle.textContent = `Визуализация: ${variant ? variant.label : "Адамар"}`;
    hadamardMatrixTitle.textContent = `Матрица Адамара H${data.block_size} (конструкция Сильвестра)`;
    hadamardParams.textContent =
        `n = ${data.block_size}, k = ${data.data_bits} бит данных, ` +
        `минимальное расстояние d = ${data.min_distance}, исправляет до t = ${data.correctable_errors} ошибок в блоке. ` +
        `Жирным выделены номера строк, использованных в сообщении.`;
    hadamardEncodeTitle.textContent =
        `Кодирование (${data.data_bits} бит данных → ${data.block_size}-битное слово)`;

    renderHadamardMatrix(data.matrix, usedRows);
    renderHadamardEncodeBlocks(data.encode_blocks);
    renderHadamardTransmission(data);
    renderHadamardDecodeBlocks(data);

    hadamardSection.hidden = false;
}


async function transmitMessage() {
    const message = messageInput.value.trim();

    errorMessage.textContent = "";

    if (!currentAlgorithm) {
        errorMessage.textContent = "Выберите тип шифрования.";
        algorithmOverlay.hidden = false;
        return;
    }

    if (STUDY_SECTIONS.has(currentAlgorithm)) {
        return;
    }

    if (!message) {
        errorMessage.textContent = "Введите сообщение.";
        return;
    }

    try {
        const requestBody = {
            message: message,
            algorithm: currentAlgorithm,
        };

        if (CODE_ALGORITHMS.has(currentAlgorithm)) {
            requestBody.frequency_source = currentFrequencySource;
        }

        if (currentAlgorithm === "hamming") {
            requestBody.variant = currentHammingVariant;
            requestBody.simulate_error = simulateErrorCheckbox.checked;
        }

        if (currentAlgorithm === "hadamard") {
            requestBody.variant = currentHadamardVariant;
            requestBody.simulate_error = hadamardSimulateErrorCheckbox.checked;
            requestBody.error_count = Number(hadamardErrorCountInput.value) || 1;
        }

        if (currentAlgorithm === "elgamal") {
            requestBody.keys = {
                p: elgamalPInput.value,
                g: elgamalGInput.value,
                x: elgamalXInput.value,
            };
            if (elgamalCertificate && elgamalCertificate.p === elgamalPInput.value.trim()) {
                requestBody.keys.certificate = elgamalCertificate.chain;
            }
        }

        const response = await fetch(apiUrl("transmit"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            // Сервер может вернуть понятное описание ошибки (например, неверные ключи Эль-Гамаля).
            let detail = null;
            try {
                detail = (await response.json()).error;
            } catch (parseError) {
                detail = null;
            }
            throw new Error(detail || "Ошибка передачи сообщения.");
        }

        const data = await response.json();

        sourceMessage.textContent = data.source;
        encodedMessage.textContent = data.encoded;
        decodedMessage.textContent = data.decoded;
        receiverMessage.textContent = data.receiver;

        codeSection.hidden = true;
        hammingSection.hidden = true;
        hadamardSection.hidden = true;
        elgamalSection.hidden = true;

        if (CODE_ALGORITHMS.has(data.algorithm)) {
            renderCodeVisualization(data);
        } else if (data.algorithm === "hamming") {
            renderHammingVisualization(data);
        } else if (data.algorithm === "hadamard") {
            renderHadamardVisualization(data);
        } else if (data.algorithm === "elgamal") {
            renderElGamalVisualization(data);
        }

    } catch (error) {
        errorMessage.textContent = error.message;
    }
}


transmitButton.addEventListener("click", transmitMessage);


messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        transmitMessage();
    }
});


// --- Моноиды ---

// Описание пяти примеров: подписи, свойства и значения по умолчанию.
// Сами вычисления (свёртка, проверка аксиом) выполняет сервер — /monoid.
const MONOID_EXAMPLES = {
    strings: {
        title: "Строки и конкатенация",
        signature: "(Σ*, ·, ε)",
        op: "·",
        description:
            "Носитель — все конечные слова над алфавитом Σ, операция — приписывание одного слова к другому, " +
            "нейтральный элемент — пустое слово ε. Это свободный моноид: именно в нём живут сообщения и их коды. " +
            "Кодирование префиксным кодом (Хаффман, Шеннон-Фано) — гомоморфизм моноидов: код(uv) = код(u) · код(v).",
        props: [["ассоциативен", true], ["нейтральный: ε", true], ["коммутативен", false], ["группа", false]],
        defaultElements: "ab, ra, ca, ε, dabra",
        hint: "Пустое слово можно ввести как ε. Запятая служит разделителем элементов.",
    },
    addition: {
        title: "Натуральные числа и сложение",
        signature: "(ℕ₀, +, 0)",
        op: "+",
        description:
            "Неотрицательные целые числа со сложением, нейтральный элемент — 0. Коммутативный моноид, но не группа: " +
            "у положительных чисел нет противоположных в ℕ₀ (для группы нужно расширить до ℤ). " +
            "Длина слова — гомоморфизм (Σ*, ·, ε) → (ℕ₀, +, 0): |uv| = |u| + |v|.",
        props: [["ассоциативен", true], ["нейтральный: 0", true], ["коммутативен", true], ["группа", false]],
        defaultElements: "3, 5, 0, 12",
        hint: "Целые неотрицательные числа.",
    },
    modular: {
        title: "Умножение по модулю n",
        signature: "(ℤₙ, · mod n, 1)",
        op: "·",
        description:
            "Остатки от деления на n с умножением по модулю, нейтральный элемент — 1. Коммутативный моноид, " +
            "но не группа: 0 необратим, а при составном n есть делители нуля (например, 2 · 5 ≡ 0 mod 10). " +
            "Обратимые элементы (НОД(a, n) = 1) образуют группу ℤₙ* — на ней основан RSA.",
        props: [["ассоциативен", true], ["нейтральный: 1", true], ["коммутативен", true], ["группа", false]],
        defaultElements: "3, 7, 9, 4",
        hint: "Числа приводятся по модулю n (2 ≤ n ≤ 100). Таблица Кэли строится при n ≤ 12.",
        hasModulus: true,
    },
    xor: {
        title: "Битовые векторы и XOR",
        signature: "({0,1}ᵏ, ⊕, 0…0)",
        op: "⊕",
        description:
            "Битовые векторы длины k с побитовым исключающим ИЛИ, нейтральный элемент — нулевой вектор. " +
            "Коммутативный моноид и даже группа: каждый вектор обратен сам себе (a ⊕ a = 0…0). " +
            "На этом основаны линейные коды Хэмминга и Адамара: принятое слово = отправленное ⊕ вектор ошибки.",
        props: [["ассоциативен", true], ["нейтральный: 0…0", true], ["коммутативен", true], ["группа", true]],
        defaultElements: "1011, 0110, 1100, 0011",
        hint: "Все векторы одной длины k; нейтральный элемент — k нулей.",
    },
    matrices: {
        title: "Матрицы 2×2 и умножение",
        signature: "(M₂(ℤ), ·, E)",
        op: "·",
        description:
            "Целочисленные матрицы 2×2 с матричным умножением, нейтральный элемент — единичная матрица E. " +
            "Некоммутативный моноид: в общем случае AB ≠ BA. Не группа: вырожденные матрицы (det = 0) необратимы.",
        props: [["ассоциативен", true], ["нейтральный: E", true], ["коммутативен", false], ["группа", false]],
        defaultElements: "1 1 / 0 1, 2 0 / 0 1, 1 0 / 1 1",
        hint: "Матрица записывается как «a b / c d» (строки разделяются «/»).",
    },
};

let currentMonoid = "strings";


function showMonoidExample(key) {
    const example = MONOID_EXAMPLES[key];
    currentMonoid = key;

    monoidTabs.forEach((tab) => {
        tab.classList.toggle("active", tab.dataset.monoid === key);
    });

    monoidExampleTitle.textContent = example.title;
    monoidSignature.textContent = example.signature;
    monoidExampleDesc.textContent = example.description;
    monoidInputHint.textContent = example.hint;
    monoidElementsInput.value = example.defaultElements;
    monoidModulusWrap.hidden = !example.hasModulus;

    monoidProps.innerHTML = "";
    example.props.forEach(([label, yes]) => {
        const prop = document.createElement("span");
        prop.className = `monoid-prop ${yes ? "yes" : "no"}`;
        prop.textContent = `${yes ? "✓" : "✗"} ${label}`;
        monoidProps.appendChild(prop);
    });

    monoidError.textContent = "";
    monoidResult.hidden = true;
}


function buildMonoidCheck(kind, title, bodyHtml) {
    const check = document.createElement("div");
    check.className = `monoid-check ${kind}`;
    check.innerHTML = `<div class="monoid-check-title">${title}</div>${bodyHtml}`;
    return check;
}


function renderMonoidFold(data, op) {
    monoidFold.innerHTML = "";

    data.fold_steps.forEach((step, index) => {
        if (index > 0) {
            const arrow = document.createElement("span");
            arrow.className = "trace-arrow";
            arrow.textContent = "→";
            monoidFold.appendChild(arrow);
        }

        const chip = document.createElement("div");
        chip.className = "trace-chip";
        chip.style.animationDelay = `${index * 0.06}s`;
        chip.innerHTML =
            `<span class="chip-top">${escapeHtml(step.left)} ${op} ${escapeHtml(step.right)}</span>` +
            `<span class="chip-bottom">= ${escapeHtml(step.result)}</span>`;
        monoidFold.appendChild(chip);
    });

    const product = data.elements.map(escapeHtml).join(` ${op} `);
    monoidFoldResult.innerHTML = `${escapeHtml(data.identity)} ${op} ${product} = <b>${escapeHtml(data.fold_result)}</b>`;
}


function renderMonoidChecks(data, op) {
    monoidChecks.innerHTML = "";
    const mark = (holds) => (holds ? "✓" : "✗");

    const assoc = data.associativity;
    if (assoc) {
        const a = escapeHtml(assoc.a);
        const b = escapeHtml(assoc.b);
        const c = escapeHtml(assoc.c);
        monoidChecks.appendChild(buildMonoidCheck(
            assoc.holds ? "ok" : "fail",
            `${mark(assoc.holds)} Ассоциативность (на первых трёх элементах)`,
            `<div><code>(a ${op} b) ${op} c = (${a} ${op} ${b}) ${op} ${c} = ${escapeHtml(assoc.ab)} ${op} ${c} = <b>${escapeHtml(assoc.ab_c)}</b></code></div>` +
            `<div><code>a ${op} (b ${op} c) = ${a} ${op} (${b} ${op} ${c}) = ${a} ${op} ${escapeHtml(assoc.bc)} = <b>${escapeHtml(assoc.a_bc)}</b></code></div>`
        ));
    } else {
        monoidChecks.appendChild(buildMonoidCheck(
            "info",
            "Ассоциативность",
            "Для наглядной проверки введите хотя бы три элемента."
        ));
    }

    const identityHolds = data.identity_checks.every((check) => check.holds);
    const identityRows = data.identity_checks.map((check) => {
        const x = escapeHtml(check.element);
        const e = escapeHtml(data.identity);
        return `<div><code>${e} ${op} ${x} = ${escapeHtml(check.left)}, ${x} ${op} ${e} = ${escapeHtml(check.right)}</code> ${mark(check.holds)}</div>`;
    }).join("");
    monoidChecks.appendChild(buildMonoidCheck(
        identityHolds ? "ok" : "fail",
        `${mark(identityHolds)} Нейтральный элемент e = ${escapeHtml(data.identity)}`,
        identityRows
    ));

    const comm = data.commutativity;
    if (comm) {
        const a = escapeHtml(comm.a);
        const b = escapeHtml(comm.b);
        const verdict = comm.holds
            ? "На этой паре порядок не важен."
            : "Порядок важен — моноид некоммутативен, и это допустимо: коммутативность не входит в аксиомы.";
        monoidChecks.appendChild(buildMonoidCheck(
            comm.holds ? "ok" : "info",
            `${comm.holds ? "=" : "≠"} Коммутативность (не обязательна)`,
            `<div><code>a ${op} b = ${a} ${op} ${b} = <b>${escapeHtml(comm.ab)}</b></code></div>` +
            `<div><code>b ${op} a = ${b} ${op} ${a} = <b>${escapeHtml(comm.ba)}</b></code></div>` +
            `<div>${verdict}</div>`
        ));
    }
}


function renderMonoidCayley(data) {
    monoidCayleyTable.innerHTML = "";

    if (!data.cayley) {
        monoidCayleyBlock.hidden = true;
        return;
    }

    monoidCayleyTitle.textContent = `Таблица Кэли для ℤ${data.modulus} (строка · столбец mod ${data.modulus})`;

    const headerRow = document.createElement("tr");
    headerRow.innerHTML = "<th>·</th>" + data.cayley.map((_, index) => `<th>${index}</th>`).join("");
    monoidCayleyTable.appendChild(headerRow);

    data.cayley.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<th>${rowIndex}</th>` + row.map((value) => {
            const cls = value === 1 ? "identity-cell" : value === 0 ? "zero-cell" : "";
            return `<td class="${cls}">${value}</td>`;
        }).join("");
        monoidCayleyTable.appendChild(tr);
    });

    monoidCayleyBlock.hidden = false;
}


async function runMonoid() {
    const example = MONOID_EXAMPLES[currentMonoid];
    monoidError.textContent = "";

    const requestBody = {
        example: currentMonoid,
        elements: monoidElementsInput.value,
    };

    if (example.hasModulus) {
        requestBody.modulus = monoidModulusInput.value;
    }

    try {
        const response = await fetch(apiUrl("monoid"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Ошибка вычисления.");
        }

        renderMonoidFold(data, example.op);
        renderMonoidChecks(data, example.op);
        renderMonoidCayley(data);
        monoidResult.hidden = false;

    } catch (error) {
        monoidResult.hidden = true;
        monoidError.textContent = error.message;
    }
}


monoidTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        showMonoidExample(tab.dataset.monoid);
        runMonoid();
    });
});

monoidRunButton.addEventListener("click", runMonoid);

[monoidElementsInput, monoidModulusInput].forEach((input) => {
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            runMonoid();
        }
    });
});

// При первом открытии раздела сразу показываем результат для примера по умолчанию.
algorithmOptions.forEach((button) => {
    if (button.dataset.algorithm === "monoids") {
        button.addEventListener("click", () => {
            if (monoidResult.hidden && !monoidError.textContent) {
                runMonoid();
            }
        });
    }
});

showMonoidExample(currentMonoid);



// --- Диофантовы уравнения ---

// Описание пяти примеров: поля ввода и значения по умолчанию.
// Решение по шагам строит сервер (/diophantine) в виде списка секций —
// шаги, таблицы и вывод — и они рисуются одинаково для всех примеров.
const DIOPHANTINE_EXAMPLES = {
    linear: {
        title: "Линейное уравнение с двумя неизвестными",
        description:
            "Классическое уравнение ax + by = c. Расширенный алгоритм Евклида даёт НОД и коэффициенты Безу, " +
            "по ним строится частное решение, а сдвиг на решения однородного уравнения даёт все остальные. " +
            "Попробуйте a = 1914, b = 899, c = 31 — решений не будет.",
        fields: [["a", "a", 56], ["b", "b", 72], ["c", "c", 40]],
        hint: "a, b — ненулевые целые; знаки допускаются.",
    },
    congruence: {
        title: "Линейное сравнение по модулю",
        description:
            "Сравнение ax ≡ b (mod m) — это то же диофантово уравнение ax − my = b. " +
            "Если d = НОД(a, m) делит b, то по модулю m существует ровно d решений; иначе решений нет. " +
            "При d = 1 решение единственно и выражается через обратный элемент a⁻¹ mod m.",
        fields: [["a", "a", 6], ["b", "b", 4], ["m", "m", 10]],
        hint: "m ≥ 2; a не должно делиться на m.",
    },
    rsa: {
        title: "Секретный ключ RSA",
        description:
            "В RSA секретная экспонента d — решение сравнения e·d ≡ 1 (mod φ(n)), т.е. диофантова уравнения " +
            "e·d − φ(n)·k = 1. Ключ существует только при НОД(e, φ(n)) = 1. " +
            "Найденный ключ сразу проверяется шифрованием и расшифрованием числа M.",
        fields: [["p", "p (простое)", 61], ["q", "q (простое)", 53], ["e", "e", 17], ["msg", "M (сообщение)", 65]],
        hint: "p, q — различные простые до 10⁶; 1 < e < φ(n); 0 ≤ M < n.",
    },
    coins: {
        title: "Размен суммы монетами",
        description:
            "Прикладная задача: сколькими способами можно набрать сумму c монетами номиналом a и b? " +
            "Нужны только неотрицательные решения ax + by = c — из общего решения выбираются допустимые t. " +
            "При НОД(a, b) = 1 любая сумма больше ab − a − b (число Фробениуса) набирается обязательно.",
        fields: [["a", "номинал a", 3], ["b", "номинал b", 5], ["c", "сумма c", 47]],
        hint: "a, b ≥ 1; c ≥ 0. Попробуйте a = 5, b = 7, c = 23 (число Фробениуса).",
    },
    pythagorean: {
        title: "Пифагоровы тройки",
        description:
            "Нелинейное диофантово уравнение x² + y² = z². Все его решения в натуральных числах описываются " +
            "формулой Евклида через параметры m > n > 0: примитивные тройки и кратные им.",
        fields: [["n", "N (макс. z)", 50]],
        hint: "5 ≤ N ≤ 300.",
    },
};


// --- Сравнения ---

const CONGRUENCE_EXAMPLES = {
    power: {
        title: "Быстрое возведение в степень по модулю",
        description:
            "Сравнения можно перемножать, поэтому aᵏ mod m считается без гигантских промежуточных чисел: " +
            "показатель раскладывается по битам, а остатки a, a², a⁴, a⁸, … получаются возведением в квадрат. " +
            "Так работают шифрование и подпись RSA, протокол Диффи–Хеллмана.",
        fields: [["a", "основание a", 5], ["k", "показатель k", 117], ["m", "модуль m", 19]],
        hint: "k до 10³⁰, m от 2 до 10¹².",
        inputType: "text",
    },
    euler: {
        title: "Теорема Эйлера и малая теорема Ферма",
        description:
            "Если НОД(a, m) = 1, то a^φ(m) ≡ 1 (mod m) — теорема Эйлера; при простом m = p это малая теорема Ферма " +
            "a^(p−1) ≡ 1. Поэтому показатель можно приводить по модулю φ(m). Пример по умолчанию — " +
            "последняя цифра числа 7²²².",
        fields: [["a", "основание a", 7], ["k", "показатель k", 222], ["m", "модуль m", 10]],
        hint: "Попробуйте a = 3, k = 1000000, m = 13 (простой модуль) или a = 4, m = 10 (НОД ≠ 1).",
        inputType: "text",
    },
    crt: {
        title: "Китайская теорема об остатках",
        description:
            "Система x ≡ rᵢ (mod mᵢ) с попарно взаимно простыми модулями имеет единственное решение по модулю " +
            "M = m₁·m₂·m₃. По умолчанию — задача Сунь-цзы (III век): число при делении на 3 даёт остаток 2, " +
            "на 5 — остаток 3, на 7 — остаток 2. Используется для ускорения расшифрования RSA.",
        fields: [["r1", "r₁", 2], ["m1", "m₁", 3], ["r2", "r₂", 3], ["m2", "m₂", 5], ["r3", "r₃", 2], ["m3", "m₃", 7]],
        hint: "Модули от 2 до 10⁶, попарно взаимно простые.",
    },
    quadratic: {
        title: "Квадратичное сравнение",
        description:
            "x² ≡ a (mod p) по простому модулю имеет 0, 1 или 2 решения. Разрешимость проверяет критерий Эйлера " +
            "a^((p−1)/2) ≡ ±1, а корень находится формулой a^((p+1)/4) при p ≡ 3 (mod 4) или алгоритмом " +
            "Тонелли–Шенкса. На трудности извлечения корней по составному модулю основана криптосистема Рабина.",
        fields: [["a", "a", 10], ["p", "p (простое)", 13]],
        hint: "p — нечётное простое до 10⁹; при p ≤ 31 показывается таблица квадратов. Попробуйте a = 5, p = 13.",
    },
    divisibility: {
        title: "Признаки делимости",
        description:
            "Признаки делимости — следствие сравнений: N = Σ dᵢ·10ⁱ ≡ Σ dᵢ·(10ⁱ mod m). " +
            "Так как 10 ≡ 1 (mod 9), число сравнимо с суммой цифр; так как 10 ≡ −1 (mod 11) — " +
            "со знакочередующейся суммой. Метод работает для любого делителя m.",
        fields: [["n", "число N", "8172635408"], ["m", "делитель m", 11]],
        hint: "N — до 60 цифр, m от 2 до 1000. Попробуйте m = 9, 7 или 13.",
        inputType: "text",
    },
};


// Общий раздел «примеры с пошаговым решением»: вкладки, поля параметров,
// запрос к серверу и отрисовка секций (шаги / таблицы / вывод).
// Используется диофантовыми уравнениями, сравнениями и вычетами.
function setupSolverSection({ prefix, algorithm, endpoint, examples }) {
    const tabs = document.querySelectorAll(`#${prefix}-tabs .monoid-tab`);
    const exampleTitle = document.getElementById(`${prefix}-example-title`);
    const equation = document.getElementById(`${prefix}-equation`);
    const exampleDesc = document.getElementById(`${prefix}-example-desc`);
    const fields = document.getElementById(`${prefix}-fields`);
    const runButton = document.getElementById(`${prefix}-run-button`);
    const hint = document.getElementById(`${prefix}-hint`);
    const errorText = document.getElementById(`${prefix}-error`);
    const result = document.getElementById(`${prefix}-result`);

    let current = Object.keys(examples)[0];

    function showExample(key) {
        const example = examples[key];
        current = key;

        tabs.forEach((tab) => {
            tab.classList.toggle("active", tab.dataset.example === key);
        });

        exampleTitle.textContent = example.title;
        equation.textContent = "—";
        exampleDesc.textContent = example.description;
        hint.textContent = example.hint;

        fields.innerHTML = "";
        example.fields.forEach(([name, label, value]) => {
            const field = document.createElement("label");
            field.className = "param-field";

            const caption = document.createElement("span");
            caption.textContent = label;

            // Большие числа (показатели до 10³⁰, N до 60 цифр) — в текстовом
            // поле: type="number" теряет точность и показывает экспоненту.
            const input = document.createElement("input");
            input.type = example.inputType || "number";
            input.name = name;
            input.value = value;
            input.addEventListener("keydown", (event) => {
                if (event.key === "Enter") {
                    run();
                }
            });

            field.append(caption, input);
            fields.appendChild(field);
        });

        errorText.textContent = "";
        result.innerHTML = "";
    }

    async function run() {
        errorText.textContent = "";

        const params = {};
        fields.querySelectorAll("input").forEach((input) => {
            params[input.name] = input.value;
        });

        try {
            const response = await fetch(apiUrl(endpoint), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ example: current, params }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Ошибка решения.");
            }

            equation.innerHTML = formatMath(data.equation);
            result.innerHTML = "";
            data.sections.forEach((section) => {
                result.appendChild(buildSolverSection(section));
            });

        } catch (error) {
            result.innerHTML = "";
            errorText.textContent = error.message;
        }
    }

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            showExample(tab.dataset.example);
            run();
        });
    });

    runButton.addEventListener("click", run);

    // При первом открытии раздела сразу решаем пример по умолчанию.
    algorithmOptions.forEach((button) => {
        if (button.dataset.algorithm === algorithm) {
            button.addEventListener("click", () => {
                if (!result.children.length && !errorText.textContent) {
                    run();
                }
            });
        }
    });

    showExample(current);
}


function buildSolverSection(section) {
    if (section.type === "result") {
        const check = document.createElement("div");
        check.className = `monoid-check ${section.kind}`;
        check.innerHTML =
            `<div class="monoid-check-title">${formatMath(section.title)}</div>` +
            `<div class="dioph-result-text">${formatMath(section.text)}</div>`;
        return check;
    }

    const block = document.createElement("div");
    block.className = "code-block";

    const title = document.createElement("h3");
    title.innerHTML = formatMath(section.title);
    block.appendChild(title);

    if (section.type === "steps") {
        const list = document.createElement("ol");
        list.className = "dioph-steps";
        section.items.forEach((item) => {
            const li = document.createElement("li");
            li.innerHTML = formatMath(item);
            list.appendChild(li);
        });
        block.appendChild(list);
        return block;
    }

    const highlight = new Set(section.highlight || []);
    const header = section.columns.map((column) => `<th>${formatMath(column)}</th>`).join("");
    const body = section.rows.map((row, index) => {
        // Переносим только очень длинные числа (большие ключи), остальное не рвём.
        const cells = row.map((cell) => {
            const longNumber = /\d{18}/.test(String(cell));
            return `<td${longNumber ? ' class="long-number"' : ""}>${formatMath(cell)}</td>`;
        }).join("");
        return `<tr class="${highlight.has(index) ? "highlight" : ""}">${cells}</tr>`;
    }).join("");

    const wrap = document.createElement("div");
    wrap.className = "table-wrap dioph-table-wrap";
    wrap.innerHTML = `<table class="code-table dioph-table"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
    block.appendChild(wrap);
    return block;
}


setupSolverSection({
    prefix: "diophantine",
    algorithm: "diophantine",
    endpoint: "/diophantine",
    examples: DIOPHANTINE_EXAMPLES,
});

setupSolverSection({
    prefix: "congruence",
    algorithm: "congruences",
    endpoint: "/congruences",
    examples: CONGRUENCE_EXAMPLES,
});


// --- Вычеты ---

const RESIDUE_EXAMPLES = {
    classes: {
        title: "Классы вычетов",
        description:
            "Числа с одинаковым остатком от деления на m образуют класс вычетов [r]ₘ = {r + km}. " +
            "Классов ровно m, они не пересекаются и покрывают все целые числа — это полная система вычетов. " +
            "У каждого класса есть наименьший неотрицательный (0…m−1) и абсолютно наименьший (|r| ≤ m/2) представитель.",
        fields: [["m", "модуль m", 5], ["x", "число x", -17]],
        hint: "2 ≤ m ≤ 30; x — любое целое (в том числе отрицательное).",
    },
    reduced: {
        title: "Приведённая система вычетов",
        description:
            "Из полной системы вычетов оставляем только взаимно простые с m — получается приведённая система R " +
            "из φ(m) элементов. Умножение на a с НОД(a, m) = 1 лишь переставляет её элементы — " +
            "отсюда в одну строку следует теорема Эйлера a^φ(m) ≡ 1.",
        fields: [["m", "модуль m", 9], ["a", "множитель a", 2]],
        hint: "2 ≤ m ≤ 200. Попробуйте a = 3 при m = 9 — перестановка разрушится.",
    },
    units: {
        title: "Обратимые элементы и делители нуля",
        description:
            "Классы вычетов можно складывать и умножать — получается кольцо ℤₘ. Элемент a обратим, " +
            "если НОД(a, m) = 1, иначе он делитель нуля: a·b ≡ 0 при ненулевых a и b. " +
            "Деление по модулю (а значит, и шифры вроде аффинного) возможно только на обратимые элементы.",
        fields: [["m", "модуль m", 12]],
        hint: "2 ≤ m ≤ 60. Сравните составное m = 12 и простое m = 13.",
    },
    order: {
        title: "Порядок элемента и первообразные корни",
        description:
            "Степени обратимого a по модулю m повторяются по циклу; длина цикла — порядок ord(a), он делит φ(m). " +
            "Элемент порядка φ(m) называется первообразным корнем: его степени дают все обратимые вычеты.",
        fields: [["m", "модуль m", 11]],
        hint: "3 ≤ m ≤ 1000. Попробуйте m = 8 или m = 15 — первообразных корней нет.",
    },
    dlog: {
        title: "Дискретный логарифм",
        description:
            "Обратная к возведению в степень задача: по g, b, m найти x с gˣ ≡ b (mod m). Считать gˣ легко, " +
            "а находить x — трудно; на этом построены Диффи–Хеллман и Эль-Гамаль. Метод Шенкса " +
            "«шаг младенца — шаг великана» решает её за ~2√m операций вместо m.",
        fields: [["g", "основание g", 5], ["b", "значение b", 8], ["m", "модуль m", 23]],
        hint: "m до 10¹⁰; g и b взаимно просты с m. Попробуйте g = 3, b = 7, m = 1000000007.",
        inputType: "text",
    },
};

setupSolverSection({
    prefix: "residue",
    algorithm: "residues",
    endpoint: "/residues",
    examples: RESIDUE_EXAMPLES,
});


// --- Шифр Эль-Гамаля ---

// Сервер описывает шифрование в том же формате секций (таблицы / шаги / вывод),
// что и учебные разделы, поэтому используем общий buildSolverSection.
function renderElGamalVisualization(data) {
    elgamalSectionsWrap.innerHTML = "";
    data.sections.forEach((section) => {
        elgamalSectionsWrap.appendChild(buildSolverSection(section));
    });
    elgamalSection.hidden = false;
}


// Сертификат Поклингтона для сгенерированного p: сервер ничего не хранит,
// поэтому сертификат отправляется обратно вместе с ключами и перепроверяется.
let elgamalCertificate = null;

// Большие числа сервер присылает строками, чтобы JavaScript не потерял цифры.
async function requestElGamalKeys(body, button) {
    errorMessage.textContent = "";
    button.disabled = true;

    try {
        const response = await fetch(apiUrl("elgamal/keys"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            let detail = null;
            try {
                detail = (await response.json()).error;
            } catch (parseError) {
                detail = null;
            }
            throw new Error(detail || "Не удалось сгенерировать ключи.");
        }

        const keys = await response.json();
        elgamalPInput.value = keys.p;
        elgamalGInput.value = keys.g;
        elgamalXInput.value = keys.x;
        elgamalCertificate = keys.certificate ? { p: String(keys.p), chain: keys.certificate } : null;
        return keys;

    } catch (error) {
        errorMessage.textContent = error.message;
        return null;
    } finally {
        button.disabled = false;
    }
}


elgamalGenerateButton.addEventListener("click", () => {
    requestElGamalKeys({ message: messageInput.value }, elgamalGenerateButton);
});


elgamalLargeButton.addEventListener("click", async () => {
    const keys = await requestElGamalKeys({ bits: elgamalBitsInput.value }, elgamalLargeButton);
    if (keys) {
        elgamalKeyHint.textContent =
            `Сгенерировано ${keys.bits}-битное простое p; простота доказана по критерию Поклингтона ` +
            `цепочкой из ${keys.steps} шагов — сертификат появится в разборе после передачи.`;
    }
});


// /lab?algorithm=... открывает сразу нужный алгоритм, без окна выбора —
// так же, как если бы пользователь нажал на него (с автозапуском примера).
if (labRoot.dataset.initialAlgorithm) {
    algorithmOptions.forEach((button) => {
        if (button.dataset.algorithm === labRoot.dataset.initialAlgorithm) {
            button.click();
        }
    });
}
