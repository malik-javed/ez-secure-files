from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status, Path, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from datetime import datetime

from ...core import config
from ...core.security import encrypt_url, decrypt_url
from ...models.user import FileResponse as FileResponseModel
from ...db.database import add_file, get_file_by_id, list_all_files
from .auth import get_ops_user, get_client_user, get_verified_user

router = APIRouter()

def validate_file_extension(filename: str) -> bool:
    """Validate if the file extension is allowed"""
    ext = filename.split(".")[-1].lower()
    return ext in config.ALLOWED_EXTENSIONS

@router.post("/upload", response_model=FileResponseModel)
async def upload_file(file: UploadFile = File(...), user = Depends(get_ops_user)):
    """Upload a file (only for operations users)"""
    
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{user['username']}_{timestamp}.{file_extension}"
    file_path = os.path.join(config.UPLOAD_DIR, unique_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Save file metadata to database
    file_data = {
        "filename": file.filename,
        "stored_filename": unique_filename,
        "file_path": file_path,
        "file_type": file_extension,
        "size": os.path.getsize(file_path),
        "uploaded_by": user["user_id"]
    }
    
    saved_file = await add_file(file_data)
    
    return FileResponseModel(
        id=str(saved_file["_id"]),
        filename=saved_file["filename"],
        file_type=saved_file["file_type"],
        size=saved_file["size"],
        upload_date=saved_file["upload_date"]
    )

@router.get("/list", response_model=List[FileResponseModel])
async def list_files(user = Depends(get_verified_user)):
    """List all available files (for both client and OPS users)"""
    files = await list_all_files()
    
    return [
        FileResponseModel(
            id=str(file["_id"]),
            filename=file["filename"],
            file_type=file["file_type"],
            size=file["size"],
            upload_date=file["upload_date"]
        ) for file in files
    ]

@router.get("/download/{file_id}")
async def get_download_url(file_id: str, user = Depends(get_verified_user)):
    """Get a secure download URL for a file (for all verified users)"""
    file = await get_file_by_id(file_id)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Generate encrypted download URL
    encrypted_url = encrypt_url(file_id, user["user_id"])
    download_url = f"http://localhost:8000/files/secure-download?token={encrypted_url}"
    
    return {"download_url": download_url}

@router.get("/secure-download")
async def secure_download(token: str = Query(...)):
    """Download a file using a secure token"""
    # Decrypt the token
    decrypted_data = decrypt_url(token)
    
    if not decrypted_data["valid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid or expired download URL: {decrypted_data.get('reason', 'Unknown error')}"
        )
    
    # Get file info
    file_id = decrypted_data["file_id"]
    user_id = decrypted_data["user_id"]
    
    file = await get_file_by_id(file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if the file exists on disk
    file_path = file["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Return the file
    return FileResponse(
        path=file_path, 
        filename=file["filename"],
        media_type="application/octet-stream"
    ) 