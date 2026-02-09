-- البحث عن منتجات بعنوان Test 3
SELECT 
    p.id,
    p.reference,
    p.ean,
    pt.lang,
    pt.title,
    p.is_active,
    p.stock_quantity,
    p.price_list,
    p.currency
FROM products p
LEFT JOIN product_translations pt ON p.id = pt.product_id
WHERE pt.title ILIKE '%Test 3%'
ORDER BY p.id;

-- إذا لم يجد شيء، ابحث في reference
SELECT 
    p.id,
    p.reference,
    pt.title
FROM products p
LEFT JOIN product_translations pt ON p.id = pt.product_id AND pt.lang = 'it'
WHERE p.reference ILIKE '%test%'
LIMIT 10;
