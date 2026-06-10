from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField('Категория', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_RENTED = 'rented'
    STATUS_SOLD = 'sold'
    STATUS_UNAVAILABLE = 'unavailable'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Доступна'),
        (STATUS_RENTED, 'В аренде'),
        (STATUS_SOLD, 'Продана'),
        (STATUS_UNAVAILABLE, 'Недоступна'),
    ]

    title = models.CharField('Название', max_length=255)
    author = models.CharField('Автор', max_length=255)
    year = models.PositiveIntegerField('Год написания')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='books', verbose_name='Категория'
    )
    description = models.TextField('Описание', blank=True)
    cover_url = models.URLField('Обложка (URL)', blank=True)
    price = models.DecimalField('Цена покупки', max_digits=10, decimal_places=2)
    rent_price_2w = models.DecimalField('Аренда 2 недели', max_digits=10, decimal_places=2)
    rent_price_1m = models.DecimalField('Аренда 1 месяц', max_digits=10, decimal_places=2)
    rent_price_3m = models.DecimalField('Аренда 3 месяца', max_digits=10, decimal_places=2)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE
    )
    is_active = models.BooleanField('В каталоге', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} — {self.author}'

    @property
    def is_available(self):
        return self.status == self.STATUS_AVAILABLE and self.is_active


class Purchase(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases'
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='purchases')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ['-purchased_at']

    def __str__(self):
        return f'{self.user.username} — {self.book.title}'


class Rental(models.Model):
    PERIOD_2W = '2w'
    PERIOD_1M = '1m'
    PERIOD_3M = '3m'
    PERIOD_CHOICES = [
        (PERIOD_2W, '2 недели'),
        (PERIOD_1M, '1 месяц'),
        (PERIOD_3M, '3 месяца'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активна'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_OVERDUE, 'Просрочена'),
    ]

    PERIOD_DAYS = {
        PERIOD_2W: 14,
        PERIOD_1M: 30,
        PERIOD_3M: 90,
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rentals'
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='rentals')
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.book.title} ({self.get_period_display()})'

    def get_rent_price(self):
        prices = {
            self.PERIOD_2W: self.book.rent_price_2w,
            self.PERIOD_1M: self.book.rent_price_1m,
            self.PERIOD_3M: self.book.rent_price_3m,
        }
        return prices[self.period]


class RentalReminder(models.Model):
    CHANNEL_EMAIL = 'email'
    CHANNEL_IN_APP = 'in_app'
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_IN_APP, 'В приложении'),
    ]

    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='reminders')
    sent_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)

    class Meta:
        verbose_name = 'Напоминание об аренде'
        verbose_name_plural = 'Напоминания об аренде'
        ordering = ['-sent_at']

    def __str__(self):
        return f'Напоминание для {self.rental}'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.message[:50]}'
