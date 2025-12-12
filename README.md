# Установка и запуск проекта

## Быстрый старт

### Windows:
```cmd
setup.bat
run.bat
```

## Ручная установка

1. Клонировать репозиторий
2. Создать виртуальное окружение:
    ```commandline
    bash
    python -m venv .venv
    ```

3. Активировать окружение:

Windows: `.venv\Scripts\activate`

Linux/Mac: `source .venv/bin/activate`

4. Установить зависимости:
    ```commandline
    bash
    pip install -r requirements.txt
    ```

5. Запустить проект:
    ```commandline
    bash
    python main.py
    ```

## Компиляция в запускаемый файл
1. Установить `pip install auto-py-to-exe`
2. Запустить из консоли `auto-py-to-exe`. Смотрите инструкцию на [сайте](https://pypi.org/project/auto-py-to-exe/).
