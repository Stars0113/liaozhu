# 1. 导入需要的模块
import os
import requests
import base64
from dotenv import load_dotenv

# 2. 加载环境变量
load_dotenv()

# 3. 读取千问 API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")


# 4. 定义图片文字提取函数
def extract_text_from_image(image_path: str) -> str:
    """
    从图片中提取文字（使用千问多模态模型）

    参数：
    - image_path: 图片文件路径

    返回：
    - 提取的文字内容（字符串）
    """
    try:
        # 1. 读取图片并编码为 Base64
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 2. 设置请求头
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }

        # 3. 构建请求数据（使用千问多模态模型）
        data = {
            "model": "qwen-vl-plus",  # 千问多模态模型
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "请提取这张图片中的所有文字，只返回文字内容，不要其他描述"},
                            {"type": "image", "image": f"data:image/png;base64,{image_base64}"}
                        ]
                    }
                ]
            },
            "parameters": {
                "temperature": 0.1  # 低温度，更确定性的输出
            }
        }

        # 4. 发送请求
        response = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            headers=headers,
            json=data
        )
        response.raise_for_status()

        # 5. 解析响应（修复：千问多模态 API 的响应格式）
        result = response.json()

        # 提取路径：output -> choices[0] -> message -> content[0] -> text
        if (result.get("output") and
                result["output"].get("choices") and
                len(result["output"]["choices"]) > 0 and
                result["output"]["choices"][0].get("message") and
                result["output"]["choices"][0]["message"].get("content") and
                len(result["output"]["choices"][0]["message"]["content"]) > 0 and
                result["output"]["choices"][0]["message"]["content"][0].get("text")):

            raw_text = result["output"]["choices"][0]["message"]["content"][0]["text"]

            # 清理文本：提取代码块内的内容
            # AI 可能返回格式："这张图片中的文字：\n\n```\n文字内容\n```\n描述"
            import re
            match = re.search(r'```\n([\s\S]*?)\n```', raw_text)
            if match:
                return match.group(1).strip()
            else:
                # 如果没有代码块格式，直接返回文本
                return raw_text.strip()
        else:
            print("OCR API response format error")
            print(f"Raw response: {result}")
            return ""

    except Exception as e:
        print(f"OCR error: {e}")
        return ""