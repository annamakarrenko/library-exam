import bleach
import markdown
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Book, Review, ReviewStatus

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

@bp.route('/book/<int:book_id>/create', methods=['GET', 'POST'])
@login_required
def create(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Проверяем, не писал ли пользователь уже рецензию
    existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.show', book_id=book_id))
    
    # Получаем статус "на рассмотрении"
    pending_status = ReviewStatus.query.filter_by(name='pending').first()
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        text = request.form.get('text')
        
        if rating is None or rating not in range(0, 6):
            flash('Пожалуйста, выберите корректную оценку.', 'danger')
            return render_template('reviews/form.html', book=book)
        
        if not text:
            flash('Текст рецензии не может быть пустым.', 'danger')
            return render_template('reviews/form.html', book=book)
        
        # Санитайзинг текста рецензии
        cleaned_text = bleach.clean(text, tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'a', 'code', 'pre'], attributes={'a': ['href', 'title']})
        
        try:
            review = Review(
                rating=rating,
                text=cleaned_text,
                book_id=book_id,
                user_id=current_user.id,
                status_id=pending_status.id
            )
            db.session.add(review)
            db.session.commit()
            flash('Ваша рецензия отправлена на модерацию.', 'success')
            return redirect(url_for('books.show', book_id=book_id))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении рецензии возникла ошибка.', 'danger')
    
    return render_template('reviews/form.html', book=book)

@bp.route('/my')
@login_required
def my_reviews():
    """Мои рецензии (для пользователя)"""
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('reviews/my_reviews.html', reviews=reviews)