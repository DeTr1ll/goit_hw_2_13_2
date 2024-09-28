from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from .forms import AuthorForm, QuoteForm, CustomUserCreationForm
from .models import Author, Quote

def home(request):
    query = request.GET.get('q', '')
    quotes = Quote.objects.filter(
        Q(quote__icontains=query) | Q(author__fullname__icontains=query)
    )
    return render(request, 'quotes/home.html', {'quotes': quotes, 'query': query})


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

class LoginView(LoginView):
    template_name = 'registration/login.html'

def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    quotes = Quote.objects.filter(author=author)
    return render(request, 'quotes/author_detail.html', {'author': author, 'quotes': quotes})

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AuthorForm()
    return render(request, 'quotes/add_author.html', {'form': form})

@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        
        # Отладка: выводим входные данные
        print("Входные данные:", request.POST)
        
        if form.is_valid():
            tags_input = form.cleaned_data.get('tags', '')
            if tags_input: 
                # Разделяем теги по запятой и убираем лишние пробелы
                tags_array = [tag.strip() for tag in tags_input.split(',')]
                form.instance.tags = tags_array  # Присваиваем теги экземпляру формы
            else:
                form.instance.tags = []
            
            try:
                form.save()  # Сохраняем форму
                return redirect('home')  # Перенаправление на главную страницу
            except Exception as e:
                print("Ошибка при сохранении:", str(e))  # Выводим ошибку, если она возникла
        else:
            # Отладка: выводим ошибки формы
            print("Ошибки формы:", form.errors)
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})