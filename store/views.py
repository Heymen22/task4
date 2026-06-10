from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookForm, BookQuickEditForm, RegisterForm
from .models import Book, Category, Notification, Purchase, Rental, RentalReminder


def catalog(request):
    books = Book.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)

    sort = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')
    prefix = '' if order == 'asc' else '-'

    sort_map = {
        'category': f'{prefix}category__name',
        'author': f'{prefix}author',
        'year': f'{prefix}year',
        'title': f'{prefix}title',
    }
    books = books.order_by(sort_map.get(sort, 'title'))

    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'store/catalog.html', {
        'books': books,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort,
        'current_order': order,
        'unread_count': unread_count,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'store/book_detail.html', {
        'book': book,
        'unread_count': unread_count,
    })


@login_required
@require_POST
@transaction.atomic
def purchase_book(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    if book.status != Book.STATUS_AVAILABLE:
        messages.error(request, 'Книга недоступна для покупки.')
        return redirect('book_detail', pk=pk)

    Purchase.objects.create(user=request.user, book=book, price=book.price)
    book.status = Book.STATUS_SOLD
    book.save(update_fields=['status'])
    messages.success(request, f'Вы успешно купили «{book.title}».')
    return redirect('my_orders')


@login_required
@require_POST
@transaction.atomic
def rent_book(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    period = request.POST.get('period')

    if book.status != Book.STATUS_AVAILABLE:
        messages.error(request, 'Книга недоступна для аренды.')
        return redirect('book_detail', pk=pk)

    if period not in Rental.PERIOD_DAYS:
        messages.error(request, 'Некорректный срок аренды.')
        return redirect('book_detail', pk=pk)

    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=Rental.PERIOD_DAYS[period])
    rental = Rental(
        user=request.user,
        book=book,
        period=period,
        start_date=start_date,
        end_date=end_date,
        price=_get_rent_price(book, period),
    )
    rental.save()

    book.status = Book.STATUS_RENTED
    book.save(update_fields=['status'])
    messages.success(
        request,
        f'Вы арендовали «{book.title}» до {end_date.strftime("%d.%m.%Y")}.',
    )
    return redirect('my_orders')


def _get_rent_price(book, period):
    prices = {
        Rental.PERIOD_2W: book.rent_price_2w,
        Rental.PERIOD_1M: book.rent_price_1m,
        Rental.PERIOD_3M: book.rent_price_3m,
    }
    return prices[period]


@login_required
def my_orders(request):
    purchases = Purchase.objects.filter(user=request.user).select_related('book')
    rentals = Rental.objects.filter(user=request.user).select_related('book')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'store/my_orders.html', {
        'purchases': purchases,
        'rentals': rentals,
        'notifications': notifications,
    })


@login_required
@require_POST
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect('my_orders')


def register(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('catalog')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'store/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'catalog'


# --- Admin panel ---

from django.contrib.admin.views.decorators import staff_member_required  # noqa: E402


@staff_member_required
def admin_dashboard(request):
    books = Book.objects.select_related('category').all()
    overdue_rentals = Rental.objects.filter(status=Rental.STATUS_OVERDUE).select_related('book', 'user')
    return render(request, 'store/admin/dashboard.html', {
        'books': books,
        'overdue_rentals': overdue_rentals,
        'status_choices': Book.STATUS_CHOICES,
    })


@staff_member_required
def admin_book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга добавлена.')
            return redirect('admin_dashboard')
    else:
        form = BookForm()
    return render(request, 'store/admin/book_form.html', {'form': form, 'title': 'Добавить книгу'})


@staff_member_required
def admin_book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Книга обновлена.')
            return redirect('admin_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'store/admin/book_form.html', {
        'form': form,
        'title': f'Редактировать: {book.title}',
        'book': book,
    })


@staff_member_required
@require_POST
def admin_book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    title = book.title
    book.delete()
    messages.success(request, f'Книга «{title}» удалена.')
    return redirect('admin_dashboard')


@staff_member_required
@require_POST
def admin_book_quick_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookQuickEditForm(request.POST, instance=book)
    if form.is_valid():
        form.save()
        messages.success(request, f'«{book.title}» обновлена.')
    else:
        messages.error(request, 'Ошибка при обновлении книги.')
    return redirect('admin_dashboard')


@staff_member_required
def admin_reminders(request):
    reminders = RentalReminder.objects.select_related(
        'rental__book', 'rental__user'
    ).all()[:100]
    overdue_rentals = Rental.objects.filter(
        status__in=[Rental.STATUS_OVERDUE, Rental.STATUS_ACTIVE],
        end_date__lt=timezone.now().date(),
    ).select_related('book', 'user')
    return render(request, 'store/admin/reminders.html', {
        'reminders': reminders,
        'overdue_rentals': overdue_rentals,
    })
