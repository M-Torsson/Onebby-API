from app.db.session import SessionLocal
from app.crud.user import get_user_by_username

db = SessionLocal()
user = get_user_by_username(db, 'Muthana')

if user:
    print("✅ User found!")
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Active: {user.is_active}")
    print(f"Superuser: {user.is_superuser}")
else:
    print("❌ User not found")
    print("\nLet's check all users:")
    from app.crud.user import get_users
    users = get_users(db)
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"  - {u.username} ({u.email})")

db.close()
