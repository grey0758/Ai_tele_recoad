import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

app = FastAPI()

# 创建uploads目录（如果不存在）
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 挂载静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"message": "录音文件上传服务", "endpoints": {
        "upload": "/upload (POST - 需要file_uuid参数)",
        "file_info": "/file/{file_uuid} (GET - 通过UUID获取文件信息)"
    }}


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...), file_uuid: str = Form(...)):
    """
    上传录音文件
    支持常见音频格式：mp3, wav, m4a, aac, ogg, flac
    需要传入唯一的UUID作为file_uuid参数
    """
    # 验证UUID格式
    try:
        uuid.UUID(file_uuid)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="无效的UUID格式"
        )
    
    # 检查文件类型
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式。支持的格式：{', '.join(allowed_extensions)}"
        )
    
    # 使用传入的UUID作为文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{file_uuid}{file_extension}"
    file_path = UPLOAD_DIR / new_filename
    
    # 检查文件是否已存在
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="文件已存在，请使用不同的UUID"
        )
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 生成访问链接
        file_url = f"/uploads/{new_filename}"
        
        return JSONResponse({
            "success": True,
            "message": "文件上传成功",
            "file_info": {
                "original_name": file.filename,
                "saved_name": new_filename,
                "file_uuid": file_uuid,
                "file_size": len(content),
                "file_type": file.content_type,
                "upload_time": datetime.now().isoformat(),
                "download_url": file_url,
                "direct_url": f"http://localhost:8022{file_url}"  # 完整URL
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败：{str(e)}")


@app.get("/file/{file_uuid}")
async def get_file_info(file_uuid: str):
    """
    通过UUID获取文件信息
    """
    # 验证UUID格式
    try:
        uuid.UUID(file_uuid)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="无效的UUID格式"
        )
    
    # 查找匹配的文件
    matching_files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file() and file_uuid in file_path.name:
            stat = file_path.stat()
            matching_files.append({
                "filename": file_path.name,
                "file_uuid": file_uuid,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "download_url": f"/uploads/{file_path.name}",
                "direct_url": f"http://localhost:8000/uploads/{file_path.name}"
            })
    
    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="未找到指定UUID的文件"
        )
    
    return JSONResponse({
        "success": True,
        "file_info": matching_files[0] if len(matching_files) == 1 else matching_files
    })


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8022)