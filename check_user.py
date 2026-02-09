# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from app.db.session import SessionLocal
from app.crud.user import get_user_by_username

db = SessionLocal()
user = get_user_by_username(db, 'Muthana')

if user:
    pass
else:
    from app.crud.user import get_users
    users = get_users(db)
    for u in users:
        pass

db.close()
