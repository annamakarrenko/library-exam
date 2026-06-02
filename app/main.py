from flask import Blueprint, render_template
from app.models import Book
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = Book.query.order_by(Book.year.desc()).paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items
    
    return render_template('index.html', books=books, pagination=pagination)