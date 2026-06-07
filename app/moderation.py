from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Review, ReviewStatus

bp = Blueprint('moderation', __name__, url_prefix='/moderation')

@bp.route('/reviews')
@login_required
def reviews():
    if current_user.role.name != 'moderator' and current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pending_status = ReviewStatus.query.filter_by(name='pending').first()
    
    pagination = Review.query.filter_by(status_id=pending_status.id).order_by(Review.created_at.asc()).paginate(page=page, per_page=per_page, error_out=False)
    reviews = pagination.items
    
    return render_template('moderation/reviews.html', reviews=reviews, pagination=pagination)

@bp.route('/review/<int:review_id>')
@login_required
def review_detail(review_id):
    """Просмотр рецензии для модерации"""
    if current_user.role.name != 'moderator' and current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    review = Review.query.get_or_404(review_id)
    return render_template('moderation/review_detail.html', review=review)

@bp.route('/review/<int:review_id>/approve', methods=['POST'])
@login_required
def approve_review(review_id):
    """Одобрить рецензию"""
    if current_user.role.name != 'moderator' and current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    review = Review.query.get_or_404(review_id)
    approved_status = ReviewStatus.query.filter_by(name='approved').first()
    review.status_id = approved_status.id
    db.session.commit()
    
    flash('Рецензия одобрена.', 'success')
    return redirect(url_for('moderation.reviews'))

@bp.route('/review/<int:review_id>/reject', methods=['POST'])
@login_required
def reject_review(review_id):
    """Отклонить рецензию"""
    if current_user.role.name != 'moderator' and current_user.role.name != 'admin':
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('main.index'))
    
    review = Review.query.get_or_404(review_id)
    rejected_status = ReviewStatus.query.filter_by(name='rejected').first()
    review.status_id = rejected_status.id
    db.session.commit()
    
    flash('Рецензия отклонена.', 'success')
    return redirect(url_for('moderation.reviews'))