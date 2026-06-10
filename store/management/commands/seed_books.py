from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from store.models import Book, Category


class Command(BaseCommand):
    help = 'Заполняет базу категориями, книгами и тестовыми пользователями'

    def handle(self, *args, **options):
        categories_data = ['Роман', 'Фантастика', 'Детектив', 'Классика', 'Научная литература']
        categories = {}
        for name in categories_data:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat

        books_data = [
            ('Мастер и Маргарита', 'М.А. Булгаков', 1967, 'Классика',
             'Мистический роман о добре и зле в Москве 1930-х годов.', 890, 150, 250, 600),
            ('Преступление и наказание', 'Ф.М. Достоевский', 1866, 'Классика',
             'Психологический роман о студенте Раскольникове.', 750, 120, 200, 500),
            ('1984', 'Джордж Оруэлл', 1949, 'Фантастика',
             'Антиутопия о тоталитарном обществе.', 650, 100, 180, 450),
            ('Маленький принц', 'Антуан де Сент-Экзюпери', 1943, 'Классика',
             'Философская сказка для детей и взрослых.', 450, 80, 140, 350),
            ('Убийство в Восточном экспрессе', 'Агата Кристи', 1934, 'Детектив',
             'Классический детектив с Эркюлем Пуаро.', 550, 90, 160, 400),
            ('Дюна', 'Фрэнк Герберт', 1965, 'Фантастика',
             'Эпическая сага о пустынной планете Арракис.', 920, 160, 280, 700),
            ('Анна Каренина', 'Л.Н. Толстой', 1877, 'Роман',
             'Роман о любви, долге и русском обществе XIX века.', 800, 130, 220, 550),
            ('Гарри Поттер и философский камень', 'Дж. К. Роулинг', 1997, 'Фантастика',
             'Первая книга о юном волшебнике Гарри Поттере.', 690, 110, 190, 480),
            ('Шерлок Холмс: Этюд в багровых тонах', 'Артур Конан Дойл', 1887, 'Детектив',
             'Первое появление великого сыщика.', 480, 85, 150, 380),
            ('Краткая история времени', 'Стивен Хокинг', 1988, 'Научная литература',
             'Популярное изложение космологии и физики.', 720, 125, 210, 520),
            ('Евгений Онегин', 'А.С. Пушкин', 1833, 'Классика',
             'Роман в стихах — энциклопедия русской жизни.', 420, 70, 120, 300),
            ('Солярис', 'Станислав Лем', 1961, 'Фантастика',
             'Философская фантастика о контакте с разумным океаном.', 580, 95, 170, 420),
            ('Идиот', 'Ф.М. Достоевский', 1869, 'Роман',
             'Роман о князе Мышкине и чистоте души.', 700, 115, 195, 490),
            ('Мы', 'Евгений Замятин', 1924, 'Фантастика',
             'Первая антиутопия XX века.', 510, 88, 155, 410),
            ('Три мушкетёра', 'Александр Дюма', 1844, 'Роман',
             'Приключенческий роман о дружбе и чести.', 620, 105, 185, 460),
        ]

        created_books = 0
        for title, author, year, cat_name, desc, price, r2w, r1m, r3m in books_data:
            _, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': author,
                    'year': year,
                    'category': categories[cat_name],
                    'description': desc,
                    'price': Decimal(str(price)),
                    'rent_price_2w': Decimal(str(r2w)),
                    'rent_price_1m': Decimal(str(r1m)),
                    'rent_price_3m': Decimal(str(r3m)),
                },
            )
            if created:
                created_books += 1

        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user('admin', 'admin@bookstore.local', 'admin123')
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('Создан admin / admin123'))

        if not User.objects.filter(username='user').exists():
            User.objects.create_user('user', 'user@bookstore.local', 'user123')
            self.stdout.write(self.style.SUCCESS('Создан user / user123'))

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {len(categories_data)} категорий, {created_books} новых книг.'
        ))
