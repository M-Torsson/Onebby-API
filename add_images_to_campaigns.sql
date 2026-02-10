-- Migration: Add image column to discount_campaigns
-- Date: 2026-02-10

-- Add image column to discount_campaigns table
ALTER TABLE discount_campaigns 
ADD COLUMN IF NOT EXISTS image VARCHAR(500);

-- Add comment
COMMENT ON COLUMN discount_campaigns.image IS 'Cloudinary image URL for campaign banner';
