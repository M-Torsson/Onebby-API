# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, Header, File, UploadFile, Form
from typing import List, Optional
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import time
import hashlib
from app.core.config import settings

router = APIRouter()


# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API Key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


# Allowed image formats
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "svg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile):
    """Validate image file"""
    # Check file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    extension = file.filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return True


@router.post("/signature")
async def generate_upload_signature(
    folder: str = Form("categories"),
    api_key: str = Depends(verify_api_key)
):
    """
    Generate Cloudinary upload signature for client-side uploads
    
    - **folder**: Folder name in Cloudinary (e.g., categories, products, brands)
    
    Returns timestamp, signature, api_key, and cloud_name for direct upload
    """
    try:
        timestamp = int(time.time())
        
        # Parameters to sign
        params_to_sign = {
            "timestamp": timestamp,
            "folder": f"onebby/{folder}"
        }
        
        # Generate signature
        signature = cloudinary.utils.api_sign_request(
            params_to_sign,
            settings.CLOUDINARY_API_SECRET
        )
        
        return {
            "signature": signature,
            "timestamp": timestamp,
            "api_key": settings.CLOUDINARY_API_KEY,
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
            "folder": f"onebby/{folder}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signature: {str(e)}")


@router.post("/admin/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("products"),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload a single image to Cloudinary
    
    - **file**: Image file (JPG, PNG, WebP, SVG)
    - **folder**: Folder name in Cloudinary (default: products)
    
    Supported folders: products, brands, categories, banners, logos, deliveries, warranties, discounts
    """
    validate_image(file)
    
    try:
        # Read file content
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=f"onebby/{folder}",
            resource_type="image",
            transformation=[
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "size": result.get("bytes")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/admin/upload/images")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = Form("products"),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload multiple images to Cloudinary (max 10 images)
    
    - **files**: List of image files (JPG, PNG, WebP, SVG)
    - **folder**: Folder name in Cloudinary (default: products)
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
    
    uploaded_images = []
    errors = []
    
    for file in files:
        try:
            validate_image(file)
            
            # Read file content
            contents = await file.read()
            
            # Check file size
            if len(contents) > MAX_FILE_SIZE:
                errors.append({
                    "filename": file.filename,
                    "error": f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
                })
                continue
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                contents,
                folder=f"onebby/{folder}",
                resource_type="image",
                transformation=[
                    {"quality": "auto"},
                    {"fetch_format": "auto"}
                ]
            )
            
            uploaded_images.append({
                "filename": file.filename,
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "size": result.get("bytes")
            })
            
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "uploaded": uploaded_images,
        "errors": errors,
        "total_uploaded": len(uploaded_images),
        "total_errors": len(errors)
    }


@router.delete("/admin/upload/{public_id:path}")
def delete_image(
    public_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Delete an image from Cloudinary
    
    - **public_id**: Public ID of the image (e.g., onebby/products/abc123)
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        
        if result.get("result") == "ok":
            return {"message": "Image deleted successfully", "public_id": public_id}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
