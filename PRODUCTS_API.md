# Products API Documentation

## Overview
Complete Products API with support for:
- **Configurable Products**: Products with variants (e.g., iPhone with different colors and storage)
- **Simple Products**: Regular products without variants
- **Service Products**: Shipping, installation services
- **Warranty Products**: Extended warranties

## Authentication
All endpoints require `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

---

## 1. Brands API

### Create Brand
**POST** `/api/admin/brands`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Apple",
  "slug": "apple",
  "image": "https://cdn.onebby.it/brands/apple.png",
  "is_active": true,
  "sort_order": 1
}
```

**Response:**
```json
{
  "id": 20,
  "name": "Apple",
  "slug": "apple",
  "image": "https://cdn.onebby.it/brands/apple.png",
  "is_active": true,
  "sort_order": 1,
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": null
}
```

### Get All Brands
**GET** `/api/admin/brands?active_only=true`

### Get Brand by ID
**GET** `/api/admin/brands/{brand_id}`

### Update Brand
**PUT** `/api/admin/brands/{brand_id}`

### Delete Brand
**DELETE** `/api/admin/brands/{brand_id}`

---

## 2. Tax Classes API

### Create Tax Class
**POST** `/api/admin/tax-classes`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Standard 22%",
  "rate": 22.0,
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Standard 22%",
  "rate": 22.0,
  "is_active": true,
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": null
}
```

### Get All Tax Classes
**GET** `/api/admin/tax-classes?active_only=true`

### Get Tax Class by ID
**GET** `/api/admin/tax-classes/{tax_class_id}`

### Update Tax Class
**PUT** `/api/admin/tax-classes/{tax_class_id}`

### Delete Tax Class
**DELETE** `/api/admin/tax-classes/{tax_class_id}`

---

## 3. Products API

### Create Product (Configurable - with Variants)
**POST** `/api/admin/products`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:** (Example: iPhone 15 with variants)
```json
{
  "product_type": "configurable",
  "reference": "IPH15-PARENT",
  "ean13": null,
  "is_active": true,
  "date_add": "2025-02-01T10:15:00Z",
  "date_update": null,
  "brand_id": 20,
  "tax": {
    "class_id": 1,
    "included_in_price": true
  },
  "price": {
    "list": 0,
    "currency": "EUR",
    "discounts": []
  },
  "condition": "new",
  "categories": [34],
  "stock": {
    "status": "in_stock",
    "quantity": 0
  },
  "images": [
    {
      "url": "https://cdn.onebby.it/products/iph15-main.jpg",
      "position": 1,
      "alt": {
        "it": "iPhone 15",
        "en": "iPhone 15",
        "fr": "iPhone 15",
        "de": "iPhone 15",
        "ar": "آيفون 15"
      }
    }
  ],
  "features": [
    {
      "code": "model_year",
      "translations": [
        { "lang": "it", "name": "Anno modello", "value": "2024" },
        { "lang": "en", "name": "Model year", "value": "2024" }
      ]
    }
  ],
  "attributes": [
    {
      "code": "device_type",
      "translations": [
        { "lang": "it", "name": "Tipo dispositivo", "value": "Smartphone" },
        { "lang": "en", "name": "Device type", "value": "Smartphone" }
      ]
    }
  ],
  "related_product_ids": [3001, 3002],
  "service_links": {
    "allowed_shipping_services": [9001, 9002],
    "allowed_warranties": [9100]
  },
  "translations": [
    {
      "lang": "it",
      "title": "iPhone 15",
      "sub_title": "Smartphone Apple di ultima generazione",
      "simple_description": "iPhone 15 con display Super Retina XDR.",
      "meta_description": "Acquista iPhone 15 con diverse capacità e colori."
    },
    {
      "lang": "en",
      "title": "iPhone 15",
      "sub_title": "Apple latest generation smartphone",
      "simple_description": "iPhone 15 with Super Retina XDR display.",
      "meta_description": "Buy iPhone 15 with different storage and colors."
    }
  ],
  "variant_attributes": [
    {
      "code": "color",
      "translations": [
        { "lang": "it", "label": "Colore" },
        { "lang": "en", "label": "Color" }
      ]
    },
    {
      "code": "storage",
      "translations": [
        { "lang": "it", "label": "Memoria" },
        { "lang": "en", "label": "Storage" }
      ]
    }
  ],
  "variants": [
    {
      "reference": "IPH15-BLK-128",
      "ean13": "1111111111111",
      "is_active": true,
      "condition": "new",
      "attributes": {
        "color": "black",
        "storage": "128"
      },
      "price": {
        "list": 899.00,
        "currency": "EUR",
        "discounts": []
      },
      "stock": {
        "status": "in_stock",
        "quantity": 5
      },
      "images": [
        {
          "url": "https://cdn.onebby.it/products/iph15-black-128-1.jpg",
          "position": 1,
          "alt": {
            "it": "iPhone 15 nero 128 GB",
            "en": "iPhone 15 black 128 GB"
          }
        }
      ]
    },
    {
      "reference": "IPH15-WHT-128",
      "ean13": "3333333333333",
      "is_active": true,
      "condition": "new",
      "attributes": {
        "color": "white",
        "storage": "128"
      },
      "price": {
        "list": 899.00,
        "currency": "EUR",
        "discounts": []
      },
      "stock": {
        "status": "in_stock",
        "quantity": 8
      },
      "images": []
    }
  ]
}
```

**Response:**
```json
{
  "message": "Product created successfully",
  "product_id": 1000,
  "reference": "IPH15-PARENT"
}
```

### Create Product (Simple)
**POST** `/api/admin/products`

**Request Body:** (Example: Single Product without variants)
```json
{
  "product_type": "simple",
  "reference": "HDMI-CABLE-2M",
  "ean13": "4444444444444",
  "is_active": true,
  "brand_id": 15,
  "tax": {
    "class_id": 1,
    "included_in_price": true
  },
  "price": {
    "list": 12.99,
    "currency": "EUR",
    "discounts": []
  },
  "condition": "new",
  "categories": [45],
  "stock": {
    "status": "in_stock",
    "quantity": 50
  },
  "images": [
    {
      "url": "https://cdn.onebby.it/products/hdmi-cable.jpg",
      "position": 1,
      "alt": {
        "it": "Cavo HDMI 2m",
        "en": "HDMI Cable 2m"
      }
    }
  ],
  "features": [],
  "attributes": [],
  "related_product_ids": [],
  "translations": [
    {
      "lang": "it",
      "title": "Cavo HDMI 2 metri",
      "sub_title": "Alta velocità 4K",
      "simple_description": "Cavo HDMI premium per connessioni 4K.",
      "meta_description": "Acquista cavo HDMI 2m alta velocità."
    }
  ],
  "variant_attributes": [],
  "variants": []
}
```

### Create Product (Service)
**POST** `/api/admin/products`

**Request Body:** (Example: Delivery Service)
```json
{
  "product_type": "service",
  "reference": "DELIVERY-FRIDGE",
  "ean13": null,
  "is_active": true,
  "brand_id": null,
  "tax": {
    "class_id": 1,
    "included_in_price": true
  },
  "price": {
    "list": 59.00,
    "currency": "EUR",
    "discounts": []
  },
  "condition": "new",
  "categories": [100],
  "stock": {
    "status": "in_stock",
    "quantity": 999
  },
  "images": [],
  "features": [],
  "attributes": [],
  "related_product_ids": [],
  "translations": [
    {
      "lang": "it",
      "title": "Consegna al Piano - Frigorifero",
      "sub_title": null,
      "simple_description": "Consegna al piano per grandi elettrodomestici.",
      "meta_description": null
    }
  ],
  "variant_attributes": [],
  "variants": []
}
```

### Create Product (Warranty)
**POST** `/api/admin/products`

**Request Body:** (Example: Extended Warranty)
```json
{
  "product_type": "warranty",
  "reference": "WARRANTY-3Y-1000",
  "ean13": null,
  "is_active": true,
  "brand_id": null,
  "tax": {
    "class_id": 1,
    "included_in_price": true
  },
  "price": {
    "list": 57.90,
    "currency": "EUR",
    "discounts": []
  },
  "condition": "new",
  "categories": [101],
  "stock": {
    "status": "in_stock",
    "quantity": 999
  },
  "images": [],
  "features": [],
  "attributes": [],
  "related_product_ids": [],
  "duration_months": 36,
  "translations": [
    {
      "lang": "it",
      "title": "GARANZIA3 – 3 anni in più Massimale 1000€",
      "sub_title": null,
      "simple_description": "Estensione di garanzia di 3 anni (36 mesi).",
      "meta_description": null
    }
  ],
  "variant_attributes": [],
  "variants": []
}
```

### Get Product by ID
**GET** `/api/v1/products/{product_id}?lang=it&include=options`

**Headers:**
```
X-API-Key: your-api-key-here
```

**Query Parameters:**
- `lang`: Language code (it, en, fr, de, ar) - default: it
- `include`: Include additional data (options) - optional

**Response:**
```json
{
  "data": {
    "id": 1000,
    "product_type": "configurable",
    "reference": "IPH15-PARENT",
    "ean13": null,
    "is_active": true,
    "date_add": "2025-02-01T10:15:00Z",
    "date_update": null,
    "brand": {
      "id": 20,
      "name": "Apple",
      "image": "https://cdn.onebby.it/brands/apple.png"
    },
    "tax": {
      "class_id": 1,
      "name": "Standard 22%",
      "rate": 22.0,
      "included_in_price": true
    },
    "categories": [
      {
        "id": 34,
        "name": "Smartphone",
        "slug": "smartphone"
      }
    ],
    "condition": "new",
    "title": "iPhone 15",
    "sub_title": "Smartphone Apple di ultima generazione",
    "simple_description": "iPhone 15 con display Super Retina XDR.",
    "meta_description": "Acquista iPhone 15 con diverse capacità e colori.",
    "images": [
      {
        "url": "https://cdn.onebby.it/products/iph15-main.jpg",
        "position": 1,
        "alt": "iPhone 15"
      }
    ],
    "features": [
      {
        "name": "Anno modello",
        "value": "2024"
      }
    ],
    "attributes": [
      {
        "code": "device_type",
        "name": "Tipo dispositivo",
        "value": "Smartphone"
      }
    ],
    "related_product_ids": [3001, 3002],
    "variant_attributes": [
      {
        "code": "color",
        "label": "Colore",
        "options": [
          { "value": "black", "label": "Black" },
          { "value": "white", "label": "White" }
        ]
      },
      {
        "code": "storage",
        "label": "Memoria",
        "options": [
          { "value": "128", "label": "128" }
        ]
      }
    ],
    "variants": [
      {
        "id": 1001,
        "reference": "IPH15-BLK-128",
        "ean13": "1111111111111",
        "is_active": true,
        "attributes": {
          "color": "black",
          "storage": "128"
        },
        "price": {
          "list": 899.00,
          "currency": "EUR",
          "discounts": []
        },
        "stock": {
          "status": "in_stock",
          "quantity": 5
        },
        "images": [
          {
            "url": "https://cdn.onebby.it/products/iph15-black-128-1.jpg",
            "position": 1,
            "alt": "iPhone 15 nero 128 GB"
          }
        ]
      },
      {
        "id": 1003,
        "reference": "IPH15-WHT-128",
        "ean13": "3333333333333",
        "is_active": true,
        "attributes": {
          "color": "white",
          "storage": "128"
        },
        "price": {
          "list": 899.00,
          "currency": "EUR",
          "discounts": []
        },
        "stock": {
          "status": "in_stock",
          "quantity": 8
        },
        "images": []
      }
    ],
    "options": {
      "shipping_services": [
        {
          "id": 9001,
          "type": "shipping_service",
          "title": "Consegna al Piano - Frigorifero",
          "description": "Consegna al piano per grandi elettrodomestici.",
          "price": {
            "amount": 59.00,
            "currency": "EUR"
          }
        }
      ],
      "warranties": [
        {
          "id": 9100,
          "type": "warranty",
          "title": "GARANZIA3 – 3 anni in più Massimale 1000€",
          "description": "Estensione di garanzia di 3 anni (36 mesi).",
          "price": {
            "amount": 57.90,
            "currency": "EUR"
          },
          "duration_months": 36
        }
      ]
    }
  },
  "meta": {
    "requested_lang": "it",
    "resolved_lang": "it"
  }
}
```

---

## 4. Stock Management API

### Update Product Stock
**PUT** `/api/admin/products/{product_id}/stock`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "stock_status": "in_stock",
  "stock_quantity": 10
}
```

**Response:**
```json
{
  "id": 1000,
  "reference": "IPH15-PARENT",
  "stock_status": "in_stock",
  "stock_quantity": 10,
  "updated_at": "2025-12-03T14:30:00Z"
}
```

### Update Variant Stock
**PUT** `/api/admin/variants/{variant_id}/stock`

**Headers:**
```
X-API-Key: your-api-key-here
Content-Type: application/json
```

**Request Body:**
```json
{
  "stock_status": "low_stock",
  "stock_quantity": 2
}
```

**Response:**
```json
{
  "id": 1001,
  "reference": "IPH15-BLK-128",
  "stock_status": "low_stock",
  "stock_quantity": 2,
  "updated_at": "2025-12-03T14:35:00Z"
}
```

---

## Features

### 1. Automatic Translations
- When creating a product, provide translations in at least one language (preferably Italian)
- System automatically translates to: `it`, `en`, `fr`, `de`, `ar`
- Uses Google Translate API (deep-translator)
- Manual translation updates supported

### 2. Product Types
- **Configurable**: Products with variants (color, size, storage, etc.)
- **Simple**: Regular products without variations
- **Service**: Shipping, installation, delivery services
- **Warranty**: Extended warranty products

### 3. Multi-language Support
- All text fields support 5 languages
- Images have language-specific alt texts
- Features and attributes have translations
- API responses return data in requested language

### 4. Stock Management
- Automatic stock status updates based on quantity:
  - `quantity = 0` → `out_of_stock`
  - `quantity <= 5` → `low_stock`
  - `quantity > 5` → `in_stock`
- Manual status override supported

### 5. Price Calculations
- Base price (list price)
- Tax included/excluded option
- Discount support (percentage or fixed amount)
- Final price calculation: `list_price ± discounts + tax`

### 6. Relations
- Products → Categories (many-to-many)
- Products → Brand (many-to-one)
- Products → Tax Class (many-to-one)
- Products → Related Products (many-to-many)
- Configurable Products → Variants (one-to-many)
- Configurable Products → Shipping Services (many-to-many)
- Configurable Products → Warranties (many-to-many)

---

## Error Handling

### Common Errors:
- **400 Bad Request**: Invalid data, validation errors
- **403 Forbidden**: Invalid or missing API key
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error

### Example Error Response:
```json
{
  "detail": "Product with this reference already exists"
}
```

---

## Testing on Postman

### Step 1: Create Brand
```
POST http://localhost:8000/api/admin/brands
X-API-Key: your-api-key-here

{
  "name": "Apple",
  "slug": "apple",
  "image": "https://cdn.onebby.it/brands/apple.png",
  "is_active": true,
  "sort_order": 1
}
```

### Step 2: Create Tax Class
```
POST http://localhost:8000/api/admin/tax-classes
X-API-Key: your-api-key-here

{
  "name": "Standard 22%",
  "rate": 22.0,
  "is_active": true
}
```

### Step 3: Create Category (if not exists)
Use the existing Categories API to create product categories.

### Step 4: Create Product
Use any of the product examples above (Configurable, Simple, Service, or Warranty).

### Step 5: Get Product
```
GET http://localhost:8000/api/v1/products/1?lang=it&include=options
X-API-Key: your-api-key-here
```

### Step 6: Update Stock
```
PUT http://localhost:8000/api/admin/products/1/stock
X-API-Key: your-api-key-here

{
  "stock_quantity": 20
}
```

---

## Database Schema

### Tables Created:
1. `brands` - Brand information
2. `tax_classes` - Tax rates and classes
3. `products` - Main products table
4. `product_translations` - Product multilingual content
5. `product_images` - Product images
6. `product_image_alts` - Image alt texts per language
7. `product_features` - Product specifications
8. `product_feature_translations` - Feature translations
9. `product_attributes` - Product attributes
10. `product_attribute_translations` - Attribute translations
11. `product_variant_attributes` - Variant attribute definitions
12. `product_variant_attribute_translations` - Variant attribute labels
13. `product_variants` - Product variants
14. `product_variant_images` - Variant images
15. `product_variant_image_alts` - Variant image alt texts
16. `product_discounts` - Product/variant discounts
17. `product_categories` - Product-category relationships
18. `product_related` - Related products
19. `product_shipping_services` - Allowed shipping services
20. `product_warranties` - Allowed warranties

---

## Notes
- All endpoints require `X-API-Key` header
- Dates in ISO 8601 format
- Prices in EUR (configurable per product)
- Stock auto-updates based on quantity
- Automatic translations from Italian
- Arabic text preserved in slugs and URLs
