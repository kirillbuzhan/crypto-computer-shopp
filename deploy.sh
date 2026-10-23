#!/usr/bin/env bash
# Развёртывание и обновление сайта одной командой (Linux-сервер).
#
# Первый запуск на чистом сервере:
#   git clone https://github.com/kirillbuzhan/crypto-computer-shopp /opt/crypto-lab
#   cd /opt/crypto-lab && sudo ./deploy.sh
#
# Обновление — та же команда: подтянет код из git, пересоберёт образ и
# перезапустит контейнер. Сайт будет доступен на порту 3250.

set -euo pipefail

PORT=3250
cd "$(dirname "$0")"

log() { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

if [ "$(id -u)" -ne 0 ] && ! docker info >/dev/null 2>&1; then
    echo "Нужны права на Docker: запустите через sudo." >&2
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    log "Docker не найден — устанавливаю"
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Не найден плагин docker compose (нужен Docker Compose v2.24+)." >&2
    exit 1
fi

if [ -d .git ]; then
    log "Обновляю код из git"
    git pull --ff-only
fi

if [ ! -f .env ]; then
    log "Создаю .env из .env.example (настройки можно поправить позже)"
    cp .env.example .env
fi

log "Собираю образ и запускаю контейнер"
docker compose up -d --build --remove-orphans

log "Жду, пока сайт ответит"
for _ in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1:${PORT}/healthz" >/dev/null 2>&1; then
        docker image prune -f >/dev/null
        log "Готово: http://$(hostname -I 2>/dev/null | awk '{print $1}'):${PORT}"
        exit 0
    fi
    sleep 2
done

echo "Сайт не ответил за 60 секунд. Логи:" >&2
docker compose logs --tail=50 web >&2
exit 1
