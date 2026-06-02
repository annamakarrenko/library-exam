import os
import hashlib
import bleach
import markdown
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Book, Genre, Cover

bp = Blueprint('books', __name__, url_prefix='/books')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_cover(file, book_id):
    """Сохранение обложки с проверкой MD5"""
    md5_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    
    # Проверяем, есть ли уже такое изображение
    existing = Cover.query.filter_by(md5_hash=md5_hash).first()
    if existing:
        existing.book_id = book_id
        db.session.commit()
        return existing
    
    # Сохраняем новое изображение
    filename = secure_filename(file.filename)
    # Используем ID книги как имя файла
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{book_id}.{ext}"
    
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename))
    
    cover = Cover(
        filename=new_filename,
        mime_type=file.mimetype,
        md5_hash=md5_hash,
        book_id=book_id
    )
    db.session.add(cover)
    db.session.commit()
    return cover

@bp.route('/<int:book_id>')
def show(book_id):
    book = Book.query.get_or_404(book_id)
    # Преобразуем Markdown в HTML
    safe_html = bleach.clean(markdown.markdown(book.short_description), tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'a', 'code', 'pre'], attributes={'a': ['href', 'title']})
    return render_template('books/show.html', book=book, description_html=safe_html)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role.name not in ['admin']:
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    genres = Genre.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        short_description = request.form.get('short_description')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        author = request.form.get('author')
        pages = request.form.get('pages')
        genre_ids = request.form.getlist('genre_ids')
        
        # Валидация
        if not all([title, short_description, year, publisher, author, pages]):
            flash('Пожалуйста, заполните все обязательные поля.', 'danger')
            return render_template('books/form.html', genres=genres)
        
        # Санитайзинг описания
        cleaned_description = bleach.clean(short_description, tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'a', 'code', 'pre'], attributes={'a': ['href', 'title']})
        
        try:
            # Создаём книгу
            book = Book(
                title=title,
                short_description=cleaned_description,
                year=int(year),
                publisher=publisher,
                author=author,
                pages=int(pages)
            )
            db.session.add(book)
            db.session.flush()  # Получаем ID книги
            
            # Добавляем жанры
            for genre_id in genre_ids:
                genre = Genre.query.get(int(genre_id))
                if genre:
                    book.genres.append(genre)
            
            db.session.commit()
            
            # Сохраняем обложку
            if 'cover' in request.files:
                file = request.files['cover']
                if file and file.filename and allowed_file(file.filename):
                    save_cover(file, book.id)
            
            flash(f'Книга "{book.title}" успешно добавлена!', 'success')
            return redirect(url_for('books.show', book_id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'При сохранении данных возникла ошибка. Проверьте корректность введённых данных. ({str(e)})', 'danger')
    
    return render_template('books/form.html', genres=genres)

@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    
    if current_user.role.name not in ['admin', 'moderator']:
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    genres = Genre.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        short_description = request.form.get('short_description')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        author = request.form.get('author')
        pages = request.form.get('pages')
        genre_ids = request.form.getlist('genre_ids')
        
        if not all([title, short_description, year, publisher, author, pages]):
            flash('Пожалуйста, заполните все обязательные поля.', 'danger')
            return render_template('books/form.html', book=book, genres=genres)
        
        cleaned_description = bleach.clean(short_description, tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'a', 'code', 'pre'], attributes={'a': ['href', 'title']})
        
        try:
            book.title = title
            book.short_description = cleaned_description
            book.year = int(year)
            book.publisher = publisher
            book.author = author
            book.pages = int(pages)
            
            # Обновляем жанры
            book.genres.clear()
            for genre_id in genre_ids:
                genre = Genre.query.get(int(genre_id))
                if genre:
                    book.genres.append(genre)
            
            db.session.commit()
            flash(f'Книга "{book.title}" успешно обновлена!', 'success')
            return redirect(url_for('books.show', book_id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    return render_template('books/form.html', book=book, genres=genres)

@bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    
    if current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        title = book.title
        # Удаляем файл обложки
        if book.cover:
            cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], book.cover.filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        
        db.session.delete(book)
        db.session.commit()
        flash(f'Книга "{title}" успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'При удалении книги возникла ошибка.', 'danger')
    
    return redirect(url_for('main.index'))