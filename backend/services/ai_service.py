# 1. 导入需要的模块
import os
import requests
import json
import re
from dotenv import load_dotenv

# 2. 加载环境变量
load_dotenv()

# 3. 读取千问 API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


# 4. 定义一个辅助函数：安全解析 JSON
def safe_parse_json(text: str):
    """
    安全地解析 JSON 字符串，处理各种异常情况

    参数：
    - text: AI 返回的文本

    返回：
    - 解析成功返回字典，失败返回 None
    """
    try:
        # 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        # 情况1：尝试提取文本中的 JSON 块
        # 查找第一个 { 和最后一个 } 之间的内容
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # 情况2：尝试清理多余字符
        cleaned_text = text.strip()
        # 移除开头的 ```json 标记
        cleaned_text = re.sub(r'^```(json)?\s*', '', cleaned_text)
        # 移除结尾的 ``` 标记
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # 所有方法都失败，返回 None
            return None


# 5. 定义生成回复的函数
def generate_response(content: str, style: str, persona: str, chat_history: list = None):
    """
    调用阿里云千问 API 生成聊天回复

    参数：
    - content: 用户输入的内容
    - style: 回复风格
    - persona: 人设标签
    - chat_history: 历史聊天记录（可选）

    返回：
    - 包含 emotion（情绪）、strategy（策略）、replies（回复列表）的字典
    """

    # 构建系统提示词（更明确地要求 JSON 格式）
    system_prompt = f"""你是聊天回复助手"聊助"。当前关系：{persona}。

请严格按照以下格式输出，不要添加任何额外内容：

分析对方消息的情绪状态，给出沟通策略，并生成3条合适的回复。

输出格式（JSON）：
{{
"emotion": "情绪判断",
"strategy": "建议策略",
"replies": ["回复1", "回复2", "回复3"]
}}

注意：
- 只输出 JSON 格式，不要有其他任何文字
- emotion 字段描述对方的情绪状态
- strategy 字段给出沟通建议
- replies 字段是包含3个字符串的数组"""

    # 构建消息列表
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # 添加历史记录
    if chat_history:
        messages.extend(chat_history)

    # 添加用户输入
    messages.append({"role": "user", "content": content})

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建千问 API 请求数据
    data = {
        "model": "qwen-plus",  # 千问模型名称
        "input": {
            "messages": messages
        },
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1024
        }
    }

    try:
        # 发送请求
        response = requests.post(
            DASHSCOPE_BASE_URL,
            headers=headers,
            json=data
        )
        response.raise_for_status()

        # 解析千问 API 响应
        result = response.json()

        if result.get("output") and result["output"].get("text"):
            content = result["output"]["text"]

            # 使用安全解析函数
            parsed_result = safe_parse_json(content)

            if parsed_result:
                # 验证返回的数据结构是否完整
                if all(key in parsed_result for key in ["emotion", "strategy", "replies"]):
                    return parsed_result

            # 如果解析失败或数据不完整，打印原始内容供调试
            print(f"AI 返回内容（格式不符合预期）：{content}")

    except Exception as e:
        print(f"Qwen API error: {e}")

    # 返回默认值
    return {
        "emotion": "无法识别",
        "strategy": "保持友好",
        "replies": ["好的", "收到", "嗯嗯"]
    }