# 1. 导入需要的模块
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from services.ocr_service import extract_text_from_image

# 2. 创建路由对象
router = APIRouter()

# 3. 图片文字提取接口
@router.post("/ocr")
async def ocr(image: UploadFile = File(...)):
    """
    上传图片并提取文字内容

    参数：
    - image: 图片文件（支持 jpg、png、jpeg 格式）

    返回：
    - text: 提取的文字内容
    """

    # 检查文件是否上传
    if not image.filename:
        raise HTTPException(status_code=400, detail="请上传图片文件")

    # 检查文件类型
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_ext = os.path.splitext(image.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持 jpg、png、jpeg 格式的图片")

    try:
        # 创建临时文件存储上传的图片
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = temp_file.name
            # 读取上传的文件内容并写入临时文件
            contents = await image.read()
            temp_file.write(contents)

        # 调用 OCR 服务提取文字
        text = extract_text_from_image(temp_path)

        return {"text": text}

    finally:
        # 清理临时文件
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
