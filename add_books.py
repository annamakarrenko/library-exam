#!/usr/bin/env python
"""
Скрипт для добавления тестовых книг и рецензий в базу данных.
Запуск: python add_books.py
"""

from app import create_app, db
from app.models import User, Genre, Book, Cover, Review, ReviewStatus
from datetime import datetime
import hashlib
import os

# Данные для добавления
books_data = [
    {
        'title': 'Мастер и Маргарита',
        'author': 'Михаил Булгаков',
        'year': 1967,
        'publisher': 'Художественная литература',
        'pages': 480,
        'short_description': 'Роман о визите сатаны в советскую Москву. Сатирическое, философское и мистическое произведение.',
        'genres': ['Роман', 'Фэнтези'],
        'cover_file': 'cover_1.jpg'
    },
    {
        'title': 'Преступление и наказание',
        'author': 'Фёдор Достоевский',
        'year': 1866,
        'publisher': 'Русский вестник',
        'pages': 672,
        'short_description': 'Роман о студенте Раскольникове, который совершает убийство и затем переживает муки совести.',
        'genres': ['Роман', 'Детектив'],
        'cover_file': 'cover_2.jpg'
    },
    {
        'title': 'Война и мир',
        'author': 'Лев Толстой',
        'year': 1869,
        'publisher': 'Русский вестник',
        'pages': 1225,
        'short_description': 'Эпопея о жизни русского общества в эпоху наполеоновских войн.',
        'genres': ['Роман', 'Историческая проза'],
        'cover_file': 'cover_3.jpg'
    },
    {
        'title': '1984',
        'author': 'Джордж Оруэлл',
        'year': 1949,
        'publisher': 'Secker & Warburg',
        'pages': 328,
        'short_description': 'Роман-антиутопия о тоталитарном режиме и слежке за гражданами.',
        'genres': ['Фантастика', 'Роман'],
        'cover_file': 'cover_4.jpg'
    },
    {
        'title': 'Евгений Онегин',
        'author': 'Александр Пушкин',
        'year': 1833,
        'publisher': 'Современник',
        'pages': 240,
        'short_description': 'Роман в стихах о судьбе дворянского интеллигента.',
        'genres': ['Поэзия', 'Роман'],
        'cover_file': 'cover_5.jpg'
    },
    {
        'title': 'Анна Каренина',
        'author': 'Лев Толстой',
        'year': 1877,
        'publisher': 'Русский вестник',
        'pages': 864,
        'short_description': 'Трагическая история любви замужней женщины и офицера.',
        'genres': ['Роман'],
        'cover_file': 'cover_6.jpg'
    },
    {
        'title': 'Двенадцать стульев',
        'author': 'Илья Ильф, Евгений Петров',
        'year': 1928,
        'publisher': 'Земля и фабрика',
        'pages': 432,
        'short_description': 'Сатирический роман о поисках бриллиантов, спрятанных в одном из двенадцати стульев.',
        'genres': ['Роман', 'Приключения'],
        'cover_file': 'cover_7.jpg'
    },
    {
        'title': 'Властелин колец',
        'author': 'Джон Р. Р. Толкин',
        'year': 1954,
        'publisher': 'Allen & Unwin',
        'pages': 1137,
        'short_description': 'Эпическое фэнтези о борьбе добра и зла в мире Средиземья.',
        'genres': ['Фэнтези', 'Приключения'],
        'cover_file': 'cover_8.jpg'
    },
    {
        'title': 'Гарри Поттер и философский камень',
        'author': 'Джоан Роулинг',
        'year': 1997,
        'publisher': 'Bloomsbury',
        'pages': 332,
        'short_description': 'Первый роман о мальчике-волшебнике, поступающем в школу чародейства.',
        'genres': ['Фэнтези', 'Приключения'],
        'cover_file': 'cover_9.jpg'
    },
    {
        'title': 'Мёртвые души',
        'author': 'Николай Гоголь',
        'year': 1842,
        'publisher': 'Современник',
        'pages': 352,
        'short_description': 'Поэма о похождениях Чичикова, скупающего мёртвые души.',
        'genres': ['Роман', 'Сатира'],
        'cover_file': 'cover_10.jpg'
    }
]

# Рецензии
reviews_data = [
    {'rating': 5, 'text': 'Гениальное произведение! Читал на одном дыхании. Обязательно к прочтению.'},
    {'rating': 4, 'text': 'Очень хорошая книга, но местами затянута. В целом впечатление положительное.'},
    {'rating': 5, 'text': 'Шедевр мировой литературы! Перечитывал несколько раз.'},
    {'rating': 3, 'text': 'Неплохо, но ожидал большего. Некоторые моменты разочаровали.'},
    {'rating': 4, 'text': 'Хороший слог, интересные персонажи. Рекомендую.'},
    {'rating': 5, 'text': 'Лучшая книга, которую я читал в этом году!'},
    {'rating': 2, 'text': 'Не моё. Слишком скучно и затянуто.'},
    {'rating': 4, 'text': 'Интересный сюжет, но концовка предсказуема.'}
]

def ensure_genres():
    """Проверяет и добавляет недостающие жанры"""
    required_genres = ['Роман', 'Фэнтези', 'Детектив', 'Историческая проза', 
                       'Фантастика', 'Поэзия', 'Приключения', 'Сатира']
    for genre_name in required_genres:
        if not Genre.query.filter_by(name=genre_name).first():
            genre = Genre(name=genre_name)
            db.session.add(genre)
            print(f"Добавлен жанр: {genre_name}")
    db.session.commit()

def add_books_and_reviews():
    app = create_app()
    with app.app_context():
        # Получаем пользователей
        admin = User.query.filter_by(login='admin').first()
        moderator = User.query.filter_by(login='moderator').first()
        user = User.query.filter_by(login='user').first()
        
        if not admin or not moderator or not user:
            print("Ошибка: не все пользователи найдены в БД!")
            return
        
        # Получаем статус "одобрено" для рецензий
        approved_status = ReviewStatus.query.filter_by(name='approved').first()
        if not approved_status:
            print("Ошибка: статус 'approved' не найден!")
            return
        
        # Создаём папку для обложек, если её нет
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Добавляем недостающие жанры
        ensure_genres()
        
        books_added = 0
        reviews_added = 0
        
        for i, book_data in enumerate(books_data):
            # Проверяем, есть ли уже такая книга
            existing = Book.query.filter_by(title=book_data['title']).first()
            if existing:
                print(f"Книга '{book_data['title']}' уже существует, пропускаем")
                continue
            
            # Находим жанры
            genres = []
            for genre_name in book_data['genres']:
                genre = Genre.query.filter_by(name=genre_name).first()
                if genre:
                    genres.append(genre)
                else:
                    print(f" Предупреждение: жанр '{genre_name}' не найден")
            
            # Создаём книгу
            book = Book(
                title=book_data['title'],
                author=book_data['author'],
                year=book_data['year'],
                publisher=book_data['publisher'],
                pages=book_data['pages'],
                short_description=book_data['short_description']
            )
            db.session.add(book)
            db.session.flush()  # Получаем ID книги
            
            # Добавляем жанры
            for genre in genres:
                book.genres.append(genre)
            
            # Проверяем, существует ли файл обложки
            cover_filename = book_data['cover_file']
            cover_path = os.path.join(uploads_dir, cover_filename)
            
            if os.path.exists(cover_path):
                # Используем реальный файл
                with open(cover_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()
                cover = Cover(
                    filename=cover_filename,
                    mime_type='image/jpeg',
                    md5_hash=md5_hash,
                    book_id=book.id
                )
                print(f" Обложка: {cover_filename} (реальный файл)")
            else:
                # Создаём заглушку
                md5_hash = hashlib.md5(book_data['title'].encode()).hexdigest()
                cover = Cover(
                    filename=f"cover_{book.id}.jpg",
                    mime_type='image/jpeg',
                    md5_hash=md5_hash,
                    book_id=book.id
                )
                print(f" Обложка: cover_{book.id}.jpg (заглушка, файл {cover_filename} не найден)")
            
            db.session.add(cover)
            db.session.commit()
            books_added += 1
            print(f"✅ Добавлена книга: {book_data['title']}")
            
            # Добавляем рецензии для первых 5 книг
            if i < 5:
                num_reviews = 2 if i % 2 == 0 else 3
                for j in range(num_reviews):
                    review_data = reviews_data[(i + j) % len(reviews_data)]
                    reviewer = [admin, moderator, user][j % 3]
                    
                    review = Review(
                        rating=review_data['rating'],
                        text=review_data['text'],
                        book_id=book.id,
                        user_id=reviewer.id,
                        status_id=approved_status.id,
                        created_at=datetime.now()
                    )
                    db.session.add(review)
                    reviews_added += 1
                    print(f"  ├─ Добавлена рецензия от {reviewer.login} (оценка: {review_data['rating']})")
            
            # Для остальных книг добавляем по 1 рецензии
            else:
                review_data = reviews_data[i % len(reviews_data)]
                reviewer = user
                review = Review(
                    rating=review_data['rating'],
                    text=review_data['text'],
                    book_id=book.id,
                    user_id=reviewer.id,
                    status_id=approved_status.id,
                    created_at=datetime.now()
                )
                db.session.add(review)
                reviews_added += 1
                print(f"  └─ Добавлена рецензия от {reviewer.login} (оценка: {review_data['rating']})")
        
        db.session.commit()
        print(f"\n🎉 Готово! Добавлено {books_added} книг и {reviews_added} рецензий.")


if __name__ == '__main__':
    add_books_and_reviews()