#!/usr/bin/env python

from app import create_app, db
from app.models import Cover
import os
import hashlib

covers_data = {
    1: 'cover_1.jpg',
    2: 'cover_2.jpg',
    3: 'cover_3.jpg',
    4: 'cover_4.jpg',
    5: 'cover_5.jpg',
    6: 'cover_6.jpg',
    7: 'cover_7.jpg',
    8: 'cover_8.jpg',
    9: 'cover_9.jpg',
    10: 'cover_10.jpg',
}

def update_covers():
    app = create_app()
    with app.app_context():
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        
        for book_id, filename in covers_data.items():
            file_path = os.path.join(uploads_dir, filename)
            
            if not os.path.exists(file_path):
                print(f" Файл {filename} не найден для книги ID {book_id}")
                continue
            
            cover = Cover.query.filter_by(book_id=book_id).first()
            if cover:
                # Вычисляем MD5 реального файла
                with open(file_path, 'rb') as f:
                    md5_hash = hashlib.md5(f.read()).hexdigest()
                
                cover.filename = filename
                cover.md5_hash = md5_hash
                db.session.commit()
                print(f" Книга ID {book_id} ({cover.book.title}): обложка обновлена на {filename}")
            else:
                print(f" Книга ID {book_id}: обложка не найдена в БД")
        
        print("\n Готово! Обложки обновлены.")

if __name__ == '__main__':
    update_covers()