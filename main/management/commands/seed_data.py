"""Команда для заполнения базы начальными данными.

Использование: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from main.models import SiteSettings, Service, Advantage, FAQ


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными для демонстрации'

    def handle(self, *args, **options):
        self.stdout.write('Заполнение начальных данных...')

        # Настройки сайта
        SiteSettings.load()
        self.stdout.write(self.style.SUCCESS('✓ Настройки сайта инициализированы'))

        # Услуги
        services_data = [
            {
                'title': 'Наращивание ресниц',
                'slug': 'naraschivanie-resnic',
                'short_description': 'Классика, 2D, 3D и голливудский объём. Гипоаллергенные материалы, стойкость до 4 недель.',
                'description': 'Профессиональное наращивание ресниц с индивидуальным подбором длины, изгиба и объёма под форму ваших глаз.',
                'price': 3500,
                'duration_minutes': 150,
                'icon': 'fa-solid fa-eye',
                'order': 1,
            },
            {
                'title': 'Ламинирование бровей',
                'slug': 'laminirovanie-brovey',
                'short_description': 'Укладка, питание и окрашивание. Идеальная форма бровей на 6–8 недель.',
                'description': 'Комплексная процедура: ламинирование, окрашивание краской или хной и коррекция формы.',
                'price': 2000,
                'duration_minutes': 90,
                'icon': 'fa-solid fa-feather',
                'order': 2,
            },
        ]

        for data in services_data:
            obj, created = Service.objects.update_or_create(
                slug=data['slug'], defaults=data
            )
            status = 'создана' if created else 'обновлена'
            self.stdout.write(self.style.SUCCESS(f'✓ Услуга «{obj.title}» {status}'))

        # Преимущества
        advantages_data = [
            {'title': 'Опыт мастера', 'description': 'Более 5 лет профессиональной практики и сотни довольных клиентов.', 'icon': 'fa-solid fa-award', 'order': 1},
            {'title': 'Качественные материалы', 'description': 'Использую только премиум-бренды — безопасно и долговечно.', 'icon': 'fa-solid fa-gem', 'order': 2},
            {'title': 'Индивидуальный подход', 'description': 'Подбираю форму и эффект под особенности каждого клиента.', 'icon': 'fa-solid fa-heart', 'order': 3},
            {'title': 'Стерильность', 'description': 'Все инструменты проходят тщательную дезинфекцию и стерилизацию.', 'icon': 'fa-solid fa-shield-heart', 'order': 4},
            {'title': 'Удобная запись', 'description': 'Онлайн-запись 24/7 — выберите удобное время в пару кликов.', 'icon': 'fa-solid fa-calendar-check', 'order': 5},
            {'title': 'Комфортная атмосфера', 'description': 'Уютный кабинет, приятная музыка и расслабляющая обстановка.', 'icon': 'fa-solid fa-spa', 'order': 6},
        ]

        for data in advantages_data:
            obj, created = Advantage.objects.update_or_create(
                title=data['title'], defaults=data
            )
            status = 'создано' if created else 'обновлено'
            self.stdout.write(self.style.SUCCESS(f'✓ Преимущество «{obj.title}» {status}'))

        # FAQ
        faq_data = [
            {
                'question': 'Сколько держится наращивание ресниц?',
                'answer': 'При правильном уходе наращивание держится 3–4 недели. Рекомендую делать коррекцию каждые 2–3 недели для поддержания идеального вида.',
                'order': 1,
            },
            {
                'question': 'Можно ли краситься после процедур?',
                'answer': 'Да, можно. Однако в первые 24 часа после наращивания ресниц и ламинирования бровей желательно избегать контакта с водой и декоративной косметикой.',
                'order': 2,
            },
            {
                'question': 'Безопасно ли ламинирование для бровей?',
                'answer': 'Абсолютно безопасно. Я использую профессиональные составы с ухаживающими компонентами, которые не повреждают волоски, а наоборот — питают их.',
                'order': 3,
            },
            {
                'question': 'Как подготовиться к процедуре?',
                'answer': 'Приходите без макияжа в зоне работы, без контактных линз (для наращивания ресниц). Откажитесь от кофе за 2 часа до процедуры — это поможет вам расслабиться.',
                'order': 4,
            },
            {
                'question': 'Как отменить или перенести запись?',
                'answer': 'Отменить или перенести запись можно, позвонив мне напрямую или написав в WhatsApp не менее чем за 3 часа до назначенного времени.',
                'order': 5,
            },
        ]

        for data in faq_data:
            obj, created = FAQ.objects.update_or_create(
                question=data['question'], defaults=data
            )
            status = 'создан' if created else 'обновлён'
            self.stdout.write(self.style.SUCCESS(f'✓ FAQ «{obj.question[:40]}…» {status}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Начальные данные успешно загружены!'))
        self.stdout.write('Теперь можно:')
        self.stdout.write('  1. Создать суперпользователя: python manage.py createsuperuser')
        self.stdout.write('  2. Запустить сервер: python manage.py runserver')
        self.stdout.write('  3. Открыть http://127.0.0.1:8000/ и http://127.0.0.1:8000/admin/')
