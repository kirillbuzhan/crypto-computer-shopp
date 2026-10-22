from pathlib import Path
import subprocess
import sys
import time
import webbrowser


PROJECT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
HOST = "127.0.0.1"
PORT = 8000


def install_dependencies() -> None:
    """Install project dependencies from requirements.txt."""
    if not REQUIREMENTS_FILE.exists():
        raise FileNotFoundError(f"Не найден файл: {REQUIREMENTS_FILE}")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        cwd=PROJECT_DIR,
        check=True,
    )


def start_server() -> subprocess.Popen:
    """Start the FastAPI application with Uvicorn."""
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=PROJECT_DIR,
    )


def main() -> None:
    """Install dependencies, start the server and open the web interface."""
    print("=== Система передачи информации ===")
    print("Проверка зависимостей...")

    try:
        install_dependencies()
    except subprocess.CalledProcessError:
        print("Не удалось установить зависимости.")
        input("Нажмите Enter для выхода...")
        return
    except FileNotFoundError as error:
        print(error)
        input("Нажмите Enter для выхода...")
        return

    print("Запуск FastAPI...")
    server = start_server()
    url = f"http://{HOST}:{PORT}"

    try:
        # Даём Uvicorn немного времени запуститься.
        time.sleep(1)

        if server.poll() is not None:
            print("Не удалось запустить сервер.")
            input("Нажмите Enter для выхода...")
            return

        print(f"Сервер запущен: {url}")
        print("Открываю браузер...")
        webbrowser.open(url)
        print("Для остановки сервера нажмите Ctrl+C.")

        server.wait()

    except KeyboardInterrupt:
        print("Остановка сервера...")
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

        print("Сервер остановлен.")


if __name__ == "__main__":
    main()
