# SQL Commands to delete all product discounts
# You can run these directly in your database console (Render.com dashboard)

# 1. Check current discounts
SELECT COUNT(*) as total_discounts FROM product_discounts;

# 2. View sample discounts (optional)
SELECT id, product_id, discount_value, campaign_id, is_active 
FROM product_discounts 
LIMIT 10;

# 3. DELETE ALL DISCOUNTS
DELETE FROM product_discounts;

# 4. Verify deletion
SELECT COUNT(*) as total_discounts FROM product_discounts;
-- Should return 0
