#!/usr/bin/env bash
# Bash-скрипт установки проекта (Linux / macOS).
set -e

echo "=== Beauty Master — автоматическая установка ==="

# 1. Виртуальное окружение
if [ ! -d "venv" ]; then
    echo "[1/5] Создание виртуального окружения..."
    python3 -m venv venv
else
    echo "[1/5] venv уже существует, пропускаем"
fi

# 2. Активация и обновление pip
echo "[2/5] Активация venv и установка зависимостей..."
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# 3. Миграции
echo "[3/5] Применение миграций..."
python manage.py migrate

# 4. Демо-данные (если запускается впервые)
read -r -p "[4/5] Загрузить демо-контент (услуги, FAQ, преимущества)? [y/N]: " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    python manage.py seed_data
fi

# 5. Суперпользователь
echo "[5/5] Создание суперпользователя для админки"
echo "    Пропустите (Ctrl+C), если уже создан."
python manage.py createsuperuser || true

echo ""
echo "✅ Готово! Запустите сервер:"
echo "   source venv/bin/activate && python manage.py runserver"
