# Установка и запуск проекта

Клонировать репозиторий

## Быстрый старт

### Windows:
Запустите
```commandline
setup.bat
run.bat
```

## Ручная установка

1. Откройте терминал, перейдите в папку с проектом.

2. Создайте виртуальное окружение:
    ```commandline
    python -m venv .venv
    ```

3. Активируйте окружение:

Windows: `.venv\Scripts\activate`

Linux/Mac: `source .venv/bin/activate`

4. Установите зависимости:
    ```commandline
    pip install -r requirements.txt
    ```

5. Запустите проект:
    ```commandline
    python main.py
    ```

## Компиляция в запускаемый файл
1. Установите `pip install auto-py-to-exe`
2. Запустите из консоли `auto-py-to-exe`
