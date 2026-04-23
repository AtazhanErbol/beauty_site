@echo off
REM Windows-скрипт установки проекта.

echo === Beauty Master - автоматическая установка ===

REM 1. venv
if not exist "venv" (
    echo [1/5] Создание виртуального окружения...
    python -m venv venv
) else (
    echo [1/5] venv уже существует, пропускаем
)

REM 2. Установка зависимостей
echo [2/5] Активация venv и установка зависимостей...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 3. Миграции
echo [3/5] Применение миграций...
python manage.py migrate

REM 4. Демо-контент
set /p answer=[4/5] Загрузить демо-контент (услуги, FAQ, преимущества)? [y/N]: 
if /i "%answer%"=="y" python manage.py seed_data

REM 5. Суперпользователь
echo [5/5] Создание суперпользователя для админки
echo     Нажмите Ctrl+C, если уже создан.
python manage.py createsuperuser

echo.
echo === Готово! Запустите сервер: ===
echo     venv\Scripts\activate
echo     python manage.py runserver

pause
