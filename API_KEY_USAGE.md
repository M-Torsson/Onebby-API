# مثال على استخدام API Key في endpoint محمي

من ملف `app/api/v1/users.py`، يمكنك حماية أي endpoint بإضافة:

```python
from fastapi import Depends
from app.core.security.api_key import verify_api_key

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    api_key: str = Depends(verify_api_key)  # ← إضافة API Key
):
    """Get all users (requires authentication + API Key)"""
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users
```

## في Postman:

عند إرسال request لـ endpoint محمي بـ API Key:

**Headers:**
```
X-API-Key: Onebby_API_Key_2025_!P9mK@7xL#4rT8nW$2qF5vB*3cH6jD9zY
Content-Type: application/json
Authorization: Bearer {your_jwt_token}
```

## على Render:

أضف في Environment Variables:
```
X-API-KEY: Onebby_API_Key_2025_!P9mK@7xL#4rT8nW$2qF5vB*3cH6jD9zY
```
