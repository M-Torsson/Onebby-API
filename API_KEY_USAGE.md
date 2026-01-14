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
X-API-Key: OnebbyAPIKey2025P9mK7xL4rT8nW2qF5vB3cH6jD9zYaXbRcGdTeUf1MwNyQsV
Content-Type: application/json
Authorization: Bearer {your_jwt_token}
```

## على Render:

أضف في Environment Variables:
```
X-API-KEY: OnebbyAPIKey2025P9mK7xL4rT8nW2qF5vB3cH6jD9zYaXbRcGdTeUf1MwNyQsV
```
