#!/usr/bin/env python
"""
Скрипт для инициализации базы данных начальными данными.
"""

from app import create_app, db
from app.models import Role, ReviewStatus, Genre, User

def init_db():
    app = create_app()
    with app.app_context():
        # Создаём таблицы
        db.create_all()
        
        roles = [
            {'name': 'admin', 'description': 'Администратор (полный доступ)'},
            {'name': 'moderator', 'description': 'Модератор (может редактировать книги и модерировать рецензии)'},
            {'name': 'user', 'description': 'Пользователь (может оставлять рецензии)'}
        ]
        
        for role_data in roles:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)
                print(f"Добавлена роль: {role_data['name']}")
        
        statuses = [
            {'name': 'pending', 'description': 'На рассмотрении'},
            {'name': 'approved', 'description': 'Одобрена'},
            {'name': 'rejected', 'description': 'Отклонена'}
        ]
        
        for status_data in statuses:
            if not ReviewStatus.query.filter_by(name=status_data['name']).first():
                status = ReviewStatus(**status_data)
                db.session.add(status)
                print(f"Добавлен статус: {status_data['name']}")
        
        genres = ['Фантастика', 'Детектив', 'Роман', 'Поэзия', 'Научная литература', 
                  'Историческая проза', 'Приключения', 'Фэнтези', 'Триллер']
        
        for genre_name in genres:
            if not Genre.query.filter_by(name=genre_name).first():
                genre = Genre(name=genre_name)
                db.session.add(genre)
                print(f"Добавлен жанр: {genre_name}")
        
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role and not User.query.filter_by(login='admin').first():
            admin = User(
                login='admin',
                last_name='Админов',
                first_name='Админ',
                middle_name='Админ',
                role_id=admin_role.id
            )
            admin.set_password('Admin123!')
            db.session.add(admin)
            print("Добавлен пользователь: admin (пароль: Admin123!)")
        
        moderator_role = Role.query.filter_by(name='moderator').first()
        if moderator_role and not User.query.filter_by(login='moderator').first():
            moderator = User(
                login='moderator',
                last_name='Модераторов',
                first_name='Модератор',
                middle_name='Модератор',
                role_id=moderator_role.id
            )
            moderator.set_password('Moder123!')
            db.session.add(moderator)
            print("Добавлен пользователь: moderator (пароль: Moder123!)")
        
        user_role = Role.query.filter_by(name='user').first()
        if user_role and not User.query.filter_by(login='user').first():
            user = User(
                login='user',
                last_name='Юзеров',
                first_name='Юзер',
                middle_name='Юзер',
                role_id=user_role.id
            )
            user.set_password('User123!')
            db.session.add(user)
            print("Добавлен пользователь: user (пароль: User123!)")
        
        db.session.commit()
        print("\nБаза данных успешно инициализирована!")

if __name__ == '__main__':
    init_db()