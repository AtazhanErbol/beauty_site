# 💅 Beauty Master — сайт мастера бьюти-услуг


git add .
git commit -m "описание изменений"
git push origin main


**Django 5 · Python 3.10+ · SQLite · Vanilla JS**

Одностраничный сайт для мастера по наращиванию ресниц и ламинированию бровей + отдельная страница онлайн‑записи с календарём. Сайт включает блок **Портфолио с lightbox**, защищённые формы (CAPTCHA + honeypot + rate‑limit), защиту админки от брутфорса и готовую прод‑конфигурацию с HTTPS / HSTS.

---

## ✨ Что умеет

### Главная страница
- Полноэкранный **Hero‑блок** (fullscreen, full‑screen hero) с картинкой-фоном, заголовком, подзаголовком, CTA‑кнопками и быстрыми контактами
- Блок **«Услуги»** — карточки с ценой, длительностью и кнопкой «Записаться»
- Блок **«Преимущества»** — карточки с иконками Font Awesome
- Блок **«Портфолио»** — сетка работ, **клик открывает изображение в lightbox** (стрелки, swipe, клавиатура Esc/←/→)
- **FAQ‑аккордеон**
- **Форма обратной связи** с серверной валидацией, CAPTCHA и honeypot
- **Контакты** (телефон, адрес, часы работы, соцсети)
- Адаптивный футер

### Страница «Запись»
- Пошаговая форма: услуга → дата → время → контакты
- Интерактивный календарь (собственный, без внешних библиотек)
- Динамические слоты через API (`/api/slots/?date=YYYY-MM-DD`)
- Интервал между записями настраивается (`BOOKING_SLOT_INTERVAL_MINUTES`)
- Серверная валидация + UniqueConstraint в БД, чтобы исключить гонки
- Страница успеха с деталями записи и кнопкой WhatsApp
- Email‑уведомление мастеру

### Админ‑панель (`/admin/`)
- Настройки сайта (синглтон): имя мастера, контакты, Hero
- Услуги / Преимущества / FAQ — полное CRUD + массовая правка порядка/активности
- Записи клиентов с цветовыми бейджами статуса
- Заявки с формы обратной связи + фильтр «обработана»
- **Портфолио**: загрузка изображений прямо из админки, превью миниатюры, сортировка

### Безопасность
- `django-axes` — блокирует вход после 5 неверных попыток (по IP+username)
- `django-honeypot` + собственное hidden‑поле `website` — ловит ботов
- Арифметическая **CAPTCHA** в ContactForm (подписана cryptographic signature, без JS)
- `django-ratelimit` — лимит на POST‑запросы форм (10–20 в минуту / IP) и API (60 / min)
- CSRF защита (встроена в Django)
- XSS — Django auto‑escape + `{{ value|escape }}` в data‑атрибутах
- SQL‑инъекции — всегда ORM, никакого raw SQL
- HTTP security headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`
- В проде: HTTPS redirect, HSTS 30 дней, `Secure` и `HttpOnly` куки
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECRET_KEY` берутся из ENV
- Пароль‑валидаторы (минимум 8 символов, запрет на `common passwords`)
- Ограничение размера загружаемого файла — 5 МБ (чтобы не положили сервер)
- Админка защищена стандартной авторизацией; URL можно сменить в `beauty_site/urls.py`

---

## 🚀 Быстрый старт (локально)

### 1. Клонируйте проект и перейдите в папку
```bash
cd beauty_site
```

### 2. Создайте виртуальное окружение

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Установите зависимости
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Примените миграции
```bash
python manage.py migrate
```

### 5. (опционально) Заполните демо‑контент
```bash
python manage.py seed_data
```

### 6. Создайте суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Запустите сервер
```bash
python manage.py runserver
```

Откройте:
- **Сайт** — http://127.0.0.1:8000/
- **Запись** — http://127.0.0.1:8000/booking/
- **Админка** — http://127.0.0.1:8000/admin/

---

## 🧰 Запуск в VS Code (пошагово)

1. **Открыть проект**: `File → Open Folder… → beauty_site`
2. Установить расширения Python и Pylance (если ещё не стоят)
3. Открыть встроенный терминал (`Ctrl + \``)
4. Выполнить команды из «Быстрого старта» (шаги 2–7)
5. В нижнем правом углу выбрать интерпретатор: `./venv/bin/python` (или `.\venv\Scripts\python.exe` на Windows)
6. (опционально) Создать файл `.vscode/launch.json` для удобной отладки:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "--noreload"],
            "django": true,
            "justMyCode": false
        }
    ]
}
```

---

## 🌐 Деплой в продакшн

### Генерация секретного ключа
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Переменные окружения (`.env` или окружение хостинга)

Смотри файл `.env.example`. Основное:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<длинный_рандомный_ключ>
DJANGO_ALLOWED_HOSTS=yoursite.com,www.yoursite.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yoursite.com,https://www.yoursite.com
DJANGO_SECURE_SSL_REDIRECT=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=app_password
```

### Сбор статики и миграции

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### Запуск Gunicorn

```bash
gunicorn beauty_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### HTTPS / SSL‑сертификат

Простой способ — **nginx + certbot**:

```bash
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d yoursite.com -d www.yoursite.com
```

Минимальный nginx‑конфиг (certbot сам добавит HTTPS‑секцию):
```nginx
server {
    listen 80;
    server_name yoursite.com www.yoursite.com;

    location /static/ { alias /app/staticfiles/; }
    location /media/  { alias /app/media/; }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

После установки сертификата Django (при `DEBUG=False`) автоматически:
- редиректит с HTTP на HTTPS (`SECURE_SSL_REDIRECT`)
- отправляет заголовок HSTS на 30 дней
- ставит флаги `Secure` / `HttpOnly` на куки

### Расширенная безопасность (рекомендуется)
- Смените URL админки: в `beauty_site/urls.py` поменяйте `admin/` на `secret-admin-XYZ/`
- Настройте fail2ban для защиты SSH
- Регулярно обновляйте `pip install -U -r requirements.txt` и применяйте миграции
- Делайте бэкапы `db.sqlite3` и `media/`
- Добавьте мониторинг (Sentry, Healthchecks)

---

## 📂 Структура проекта

```
beauty_site/
├── beauty_site/                    # Настройки Django
│   ├── settings.py                 # Конфигурация (security, БД, email, слоты)
│   ├── urls.py                     # Корневой роутинг
│   ├── wsgi.py / asgi.py
├── main/                           # Основное приложение
│   ├── models.py                   # Все модели (+ PortfolioItem)
│   ├── admin.py                    # Админка (с превью для портфолио)
│   ├── forms.py                    # ContactForm (с CAPTCHA), BookingForm (honeypot)
│   ├── views.py                    # Контроллеры + API + rate limit
│   ├── urls.py                     # Маршруты
│   ├── utils.py                    # Слоты / email / WhatsApp helpers
│   ├── context_processors.py       # SiteSettings во все шаблоны
│   ├── migrations/
│   └── management/commands/
│       └── seed_data.py            # Демо‑контент
├── templates/main/
│   ├── base.html                   # Базовый шаблон (меню, футер)
│   ├── index.html                  # Главная (hero fullscreen + портфолио + lightbox)
│   ├── booking.html                # Страница записи (honeypot)
│   ├── booking_success.html        # Подтверждение записи
│   └── 404.html
├── static/
│   ├── css/style.css               # Стили + full-screen hero + portfolio + lightbox
│   └── js/
│       ├── main.js                 # Меню, FAQ, маска телефона
│       ├── booking.js              # Календарь и слоты
│       └── lightbox.js             # Lightbox для портфолио
├── media/                          # Загружаемые через админку файлы (hero, услуги, портфолио)
├── requirements.txt
├── .env.example
├── .gitignore
├── db.sqlite3                      # БД (не коммитится в прод)
├── manage.py
└── README.md
```

---

## 🗃️ Модели

| Модель          | Назначение                                      | Ключевые поля |
|-----------------|-------------------------------------------------|---------------|
| `SiteSettings`  | Синглтон настроек                               | master_name, phone, hero_image, hero_video_url |
| `Service`       | Услуги мастера                                  | title, slug, price, duration_minutes, icon |
| `Advantage`     | Карточки блока «Преимущества»                   | title, description, icon |
| `FAQ`           | Вопрос/ответ                                    | question, answer, order |
| `Booking`       | Запись клиента                                  | name, phone, service, date, time, status |
| `ContactRequest`| Заявка с формы обратной связи                   | name, phone, message, is_processed |
| **`PortfolioItem`** | **Работа в портфолио (НОВОЕ)**              | title, description, image, service, order |

---

## 🔗 Маршруты

| URL | Имя | Описание |
|-----|-----|----------|
| `/` | `index` | Главная + обработка формы обратной связи |
| `/booking/` | `booking` | Онлайн‑запись. `?service=<id>` предзаполняет услугу |
| `/api/slots/?date=YYYY-MM-DD` | `api_slots` | JSON со слотами на дату |
| `/admin/` | — | Админ‑панель |

---

## ⚙️ Настройки бронирования

В `beauty_site/settings.py`:

```python
BOOKING_SLOT_INTERVAL_MINUTES = 180   # интервал между записями (3 часа)
BOOKING_WORK_START_HOUR = 9           # начало рабочего дня
BOOKING_WORK_END_HOUR = 21            # конец рабочего дня
BOOKING_DAYS_AHEAD = 30               # глубина записи (дней)
```

---

## 🧪 Проверка безопасности (чек‑лист)

- [x] SECRET_KEY не в коде (берётся из ENV, дефолт только для dev)
- [x] DEBUG=False в проде (через ENV)
- [x] ALLOWED_HOSTS строго ограничен в проде
- [x] CSRF защита включена (встроенно)
- [x] SQL‑инъекции: только ORM
- [x] XSS: Django auto‑escape, `|escape` в data‑атрибутах
- [x] Clickjacking: `X-Frame-Options: DENY`
- [x] Brute‑force: `django-axes` (5 попыток / 1 час кулдаун)
- [x] Spam‑защита форм: honeypot + CAPTCHA + rate limit
- [x] HSTS + HTTPS redirect (при DEBUG=False)
- [x] Ограничение загружаемых файлов: 5 МБ
- [x] Валидация расширений изображений (jpg/png/webp/gif)
- [x] Логирование security‑событий
- [x] Пароли хешируются (PBKDF2, встроенно)
- [x] Секреты в ENV, не в коде

Для продакшна рекомендуется:
```bash
python manage.py check --deploy
```

---

## 🛠️ Стек

- **Backend:** Django 5.0 · Python 3.10+
- **Frontend:** HTML5, CSS3 (без фреймворков), Vanilla JS
- **Шрифты:** Inter + Playfair Display (Google Fonts)
- **Иконки:** Font Awesome 6 (CDN)
- **БД:** SQLite (легко меняется на PostgreSQL)
- **Безопасность:** django-axes, django-honeypot, django-ratelimit
- **Прод:** whitenoise, gunicorn

---

## 📝 Лицензия

Свободное использование для коммерческих и личных целей.
