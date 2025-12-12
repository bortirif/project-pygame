@echo off
echo Установка зависимостей Python...

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверяем наличие виртуального окружения
if not exist ".venv" (
    echo Создание виртуального окружения...
    python -m venv .venv
)

REM Активируем виртуальное окружение
call .venv\Scripts\activate.bat

REM Обновляем pip
python -m pip install --upgrade pip

REM Устанавливаем зависимости
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Файл requirements.txt не найден!
    pause
    exit /b 1
)

echo Установка завершена!
echo.
echo Для активации виртуального окружения выполните:
echo .venv\Scripts\activate
pause