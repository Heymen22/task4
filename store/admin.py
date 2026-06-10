from django.contrib import admin

from .models import Book, Category, Notification, Purchase, Rental, RentalReminder


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'category', 'price', 'status', 'is_active')
    list_filter = ('category', 'status', 'is_active')
    search_fields = ('title', 'author')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'price', 'purchased_at')
    list_filter = ('purchased_at',)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'period', 'start_date', 'end_date', 'status', 'reminder_sent')
    list_filter = ('status', 'period')


@admin.register(RentalReminder)
class RentalReminderAdmin(admin.ModelAdmin):
    list_display = ('rental', 'channel', 'sent_at')
    list_filter = ('channel',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
