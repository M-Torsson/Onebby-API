# 📚 API Endpoints Guide

## 🔗 Base URL
```
https://onebby-api.onrender.com/api/users
```

## 🔑 Authentication
All endpoints require API Key in headers:
```json
{
  "X-API-Key": "YOUR_API_KEY"
}
```

---

## 👤 CUSTOMERS ENDPOINTS

| Method | Endpoint | Request Body |
|--------|----------|--------------|
| **POST** | `/customers/register` | `{ "reg_type": "user", "title": "Sig.", "first_name": "Mario", "last_name": "Rossi", "email": "mario@example.com", "password": "123456" }` |
| **POST** | `/customers/login` | `{ "email": "mario@example.com", "password": "123456" }` |
| **GET** | `/customers` | No body |
| **GET** | `/customers/{id}` | No body |
| **PUT** | `/customers/{id}` | `{ "first_name": "Mario Updated", "email": "newemail@example.com" }` |
| **DELETE** | `/customers/{id}` | No body |

---

## 🏢 COMPANIES ENDPOINTS

| Method | Endpoint | Request Body |
|--------|----------|--------------|
| **POST** | `/companies/register` | **Italian:** `{ "reg_type": "company", "company_name": "My Company SRL", "email": "info@company.it", "password": "123456", "vat_number": "12345678901", "tax_code": "ABCDEF12G34H567I", "sdi_code": "ABC1234", "pec": "company@pec.it" }` |
| **POST** | `/companies/register` | **Foreign:** `{ "reg_type": "company", "company_name": "Foreign Company", "email": "info@foreign.com", "password": "123456", "vat_number": "98765432109", "tax_code": null, "sdi_code": "XYZ5678", "pec": null }` |
| **POST** | `/companies/login` | `{ "email": "info@company.it", "password": "123456" }` |
| **GET** | `/companies` | No body |
| **GET** | `/companies/{id}` | No body |
| **PUT** | `/companies/{id}` | **Update Info:** `{ "company_name": "New Name", "email": "new@company.it" }` |
| **PUT** | `/companies/{id}` | **Approve/Reject:** `{ "approval_status": "approved" }` |
| **DELETE** | `/companies/{id}` | No body |

---

## 📊 APPROVAL STATUS (Companies Only)

| Status | Description | Login Behavior |
|--------|-------------|----------------|
| `"pending"` | ✋ Default - Company waiting for approval | **Cannot login** - Error: "Your account is pending approval. Please wait for administrator approval." |
| `"approved"` | ✅ Company approved by admin | **Can login** - Full access granted |
| `"rejected"` | ❌ Company rejected by admin | **Cannot login** - Error: "Your account has been rejected. Please contact administration for more information." |

**Note:** 
- All new companies start with `approval_status = "pending"`
- Companies **cannot login** until status is changed to `"approved"` by admin
- Admin changes status using `PUT /companies/{id}` endpoint

---

## 📝 Response Examples

### Login Response (Both Customers & Companies):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 7
}
```

### Customer Response:
```json
{
  "id": 1,
  "reg_type": "user",
  "title": "Sig.",
  "first_name": "Mario",
  "last_name": "Rossi",
  "email": "mario@example.com",
  "is_active": true,
  "created_at": "2026-02-13T10:00:00Z",
  "updated_at": null
}
```

### Company Response:
```json
{
  "id": 2,
  "reg_type": "company",
  "company_name": "My Company SRL",
  "email": "info@company.it",
  "vat_number": "12345678901",
  "tax_code": "ABCDEF12G34H567I",
  "sdi_code": "ABC1234",
  "pec": "company@pec.it",
  "approval_status": "pending",
  "is_active": true,
  "created_at": "2026-02-13T10:00:00Z",
  "updated_at": null
}
```

---

## ⚠️ Important Notes

1. **Italian Companies:** Must provide `tax_code` AND `pec`
2. **Foreign Companies:** Can set `tax_code` and `pec` to `null`
3. **Approval Status:** Only companies have this field (customers don't)
4. **Email Uniqueness:** Each email can only be used once across all users
5. **Query Parameters:** For GET all endpoints: `?skip=0&limit=100`

---

## ⚠️ Error Responses

### Company Login Errors:

**Pending Approval (403):**
```json
{
  "detail": "Your account is pending approval. Please wait for administrator approval."
}
```

**Rejected Account (403):**
```json
{
  "detail": "Your account has been rejected. Please contact administration for more information."
}
```

**Invalid Credentials (401):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

## 🎯 Frontend Implementation Tips

```javascript
// Example: Register Customer
const registerCustomer = async (data) => {
  const response = await fetch('https://onebby-api.onrender.com/api/users/customers/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify(data)
  });
  return await response.json();
};

// Example: Company Login with Error Handling
const loginCompany = async (email, password) => {
  const response = await fetch('https://onebby-api.onrender.com/api/users/companies/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify({ email, password })
  });
  
  if (response.status === 403) {
    const data = await response.json();
    // Show appropriate message based on approval status
    alert(data.detail);
    return null;
  }
  
  return await response.json();
};

// Example: Approve Company
const approveCompany = async (companyId) => {
  const response = await fetch(`https://onebby-api.onrender.com/api/users/companies/${companyId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify({ approval_status: 'approved' })
  });
  return await response.json();
};
```
