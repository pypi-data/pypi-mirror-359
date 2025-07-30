# zhongyao_mcp_server.py
import time
import json
import requests
import configparser
import os
from typing import Any, Dict
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("Zhongyao AI Generation Server")

# --- 全局配置 (将从 config.ini 加载) ---
API_KEY = None
BASE_URL = None
DEFAULT_CHAT_MODEL = None
DEFAULT_IMAGE_MODEL = None
DEFAULT_VIDEO_MODEL = None

# --- 加载配置 ---
def load_config():
    """从 config.ini 文件加载配置"""
    global API_KEY, BASE_URL, DEFAULT_CHAT_MODEL, DEFAULT_IMAGE_MODEL, DEFAULT_VIDEO_MODEL
    
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    if not os.path.exists(config_file):
        print(f"错误: 配置文件 '{config_file}' 未找到。")
        print("请在脚本同目录下创建一个 'config.ini' 文件，并包含以下内容:")
        print("""
[API]
api_key = YOUR_API_KEY_HERE
base_url = https://ark.cn-beijing.volces.com/api/v3

[Models]
chat_model = deepseek-V3
image_model = doubao-seedream-3-0-t2i-250415
video_model = doubao-seedance-1-0-lite-t2v-250428
        """)
        return

    config.read(config_file)

    try:
        API_KEY = config.get('API', 'api_key', fallback=None)
        BASE_URL = config.get('API', 'base_url', fallback='https://ark.cn-beijing.volces.com/api/v3')

        DEFAULT_CHAT_MODEL = config.get('Models', 'chat_model', fallback='deepseek-V3')
        DEFAULT_IMAGE_MODEL = config.get('Models', 'image_model', fallback='doubao-seedream-3-0-t2i-250415')
        DEFAULT_VIDEO_MODEL = config.get('Models', 'video_model', fallback='doubao-seedance-1-0-lite-t2v-250428')
        
        print("配置已从 config.ini 成功加载。")
        if not API_KEY or API_KEY == 'YOUR_API_KEY_HERE':
            print("警告: 'config.ini' 中的 API_KEY 未设置或仍为占位符。请设置有效的密钥。")
            API_KEY = None # 确保如果未正确设置，API_KEY 为 None

    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"读取配置文件时出错: {e}")
        print("请确保 'config.ini' 包含 [API] 和 [Models] 部分，以及所有必需的键。")

# 在脚本启动时调用函数加载配置
load_config()

# --- 提示词模板 ---
# 使用模板来确保生成内容的格式和风格一致
PROMPT_TEMPLATES = {
    "info": {
        "system": "你是一个专业的中医药专家，请提供准确、详细且格式正确的中药材信息。",
        "user": """请以JSON格式返回关于中药材"{herb_name}"的详细信息，必须包含以下字段：
1. "name": 药材名称 (string)
2. "property": 药性, 例如: '寒', '热', '温', '凉' (string)
3. "taste": 药味, 例如: '酸', '苦', '甘', '辛', '咸' (list of strings)
4. "meridian": 归经, 例如: '肝经', '心经' (list of strings)
5. "function": 功效主治 (string)
6. "usage_and_dosage": 用法用量 (string)
7. "contraindications": 使用禁忌 (string)
8. "description": 简要描述，介绍药材来源和形态特征 (string)

请确保返回的是一个结构完整的、合法的JSON对象，不要在JSON前后添加任何多余的文字或解释。
"""
    },
    "image": {
        "prompt": "一张关于中药'{herb_name}'的高清摄影照片，展示其作为药材的真实形态、颜色和纹理细节。背景干净纯白，光线明亮均匀，突出药材本身，具有百科全书式的专业质感。"
    },
    "video": {
        "prompt": "一段关于中药'{herb_name}'的短视频。视频风格：纪录片、特写镜头。画面内容：首先是{herb_name}药材的特写镜头，缓慢旋转展示细节；然后展示其生长的自然环境；最后是它被用于传统中医的场景，比如煎药或者入药。整个视频节奏舒缓，配乐为典雅的中国古典音乐。"
    }
}

# --- 辅助函数 ---
def initialize_client():
    """初始化并返回OpenAI客户端"""
    if not API_KEY:
        raise ValueError("API key is required. Please set it using the set_api_key tool or in config.ini.")
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)

# --- 核心高层工具 (推荐使用) ---

@mcp.tool()
def get_chinese_herb_info(herb_name: str, model: str = None) -> Dict[str, Any]:
    """
    获取指定中药材的详细信息。

    Args:
        herb_name: 中药材的名称，例如 "人参" 或 "枸杞"。
        model: 用于生成信息的大语言模型。如果未提供，则使用配置文件中的默认模型。

    Returns:
        包含药材详细信息的JSON对象或错误信息。
    """
    model_to_use = model or DEFAULT_CHAT_MODEL
    try:
        system_prompt = PROMPT_TEMPLATES["info"]["system"]
        user_prompt = PROMPT_TEMPLATES["info"]["user"].format(herb_name=herb_name)
        
        response = _chat_completion(prompt=user_prompt, system_prompt=system_prompt, model=model_to_use)

        if not response.get("success"):
            return response

        raw_content = response.get("content", "")
        
        # 尝试清理和解析模型返回的JSON字符串
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()

        try:
            parsed_json = json.loads(raw_content)
            return {"success": True, "data": parsed_json}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse model response as JSON: {e}", "raw_content": raw_content}

    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred while getting herb info: {str(e)}"}

@mcp.tool()
def get_chinese_herb_image(herb_name: str, size: str = "1024x1024", model: str = None) -> Dict[str, Any]:
    """
    生成指定中药材的图片。

    Args:
        herb_name: 中药材的名称，例如 "人参" 或 "枸杞"。
        size: 图片尺寸。
        model: 使用的文生图模型。如果未提供，则使用配置文件中的默认模型。

    Returns:
        包含图片URL或错误信息的字典。
    """
    model_to_use = model or DEFAULT_IMAGE_MODEL
    try:
        prompt = PROMPT_TEMPLATES["image"]["prompt"].format(herb_name=herb_name)
        result = _text_to_image(prompt=prompt, size=size, model=model_to_use)
        
        if result.get("success"):
            return {"success": True, "herb_name": herb_name, "image_url": result.get("image_url"), "message": f"Image for '{herb_name}' generated successfully."}
        else:
            return result
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred while generating herb image: {str(e)}"}

@mcp.tool()
def get_chinese_herb_video(herb_name: str, duration: str = "8", ratio: str = "9:16", model: str = None) -> Dict[str, Any]:
    """
    生成关于指定中药材的短视频。

    Args:
        herb_name: 中药材的名称，例如 "人参" 或 "枸杞"。
        duration: 视频时长（秒）。
        ratio: 视频比例。
        model: 使用的文生视频模型。如果未提供，则使用配置文件中的默认模型。

    Returns:
        包含视频URL或错误信息的字典。
    """
    model_to_use = model or DEFAULT_VIDEO_MODEL
    try:
        prompt = PROMPT_TEMPLATES["video"]["prompt"].format(herb_name=herb_name)
        result = _text_to_video(prompt=prompt, duration=duration, ratio=ratio, model=model_to_use)

        if result.get("success"):
            return {"success": True, "herb_name": herb_name, "video_url": result.get("video_url"), "message": f"Video task for '{herb_name}' succeeded.", "task_id": result.get("task_id")}
        else:
            return result
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred while generating herb video: {str(e)}"}


# --- 底层API工具 (由高层工具调用) ---

@mcp.tool()
def set_api_key(api_key: str) -> str:
    """设置豆包API密钥 (会覆盖配置文件中的值)"""
    global API_KEY
    API_KEY = api_key
    print(f"API key has been temporarily set via tool.")
    return "API key set successfully for this session."

def _chat_completion(prompt: str, model: str, system_prompt: str) -> Dict[str, Any]:
    """底层函数：调用语言模型生成文本"""
    try:
        client = initialize_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return {"success": True, "content": response.choices[0].message.content}
    except Exception as e:
        return {"success": False, "error": f"Text generation failed: {str(e)}"}

def _text_to_image(prompt: str, size: str, model: str) -> Dict[str, Any]:
    """底层函数：根据文本描述生成图片"""
    try:
        client = initialize_client()
        response = client.images.generate(model=model, prompt=prompt, size=size, response_format="url", n=1)
        if response.data and len(response.data) > 0:
            return {"success": True, "image_url": response.data[0].url}
        else:
            return {"success": False, "error": "No image data returned from API."}
    except Exception as e:
        return {"success": False, "error": f"Image generation failed: {str(e)}"}

def _text_to_video(prompt: str, duration: str, ratio: str, model: str) -> Dict[str, Any]:
    """底层函数：根据文本描述生成视频"""
    try:
        # 自动将参数添加到提示词中，以符合豆包API的要求
        if ratio and "--ratio" not in prompt:
            prompt += f" --ratio {ratio}"
        if duration and "--duration" not in prompt and "--dur" not in prompt:
            prompt += f" --duration {duration}"
        
        client = initialize_client() # 确保API_KEY已设置
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        request_data = {"model": model, "content": [{"type": "text", "text": prompt}]}
        
        # 1. 创建视频生成任务
        create_resp = requests.post(f"{BASE_URL}/contents/generations/tasks", headers=headers, json=request_data)
        if create_resp.status_code != 200:
            return {"success": False, "error": f"Failed to create video task. Status: {create_resp.status_code}, Info: {create_resp.text}"}
        
        task_id = create_resp.json().get("id")
        if not task_id:
            return {"success": False, "error": "Could not get task ID from response."}
        
        # 2. 轮询任务状态
        for _ in range(60):  # 最多等待 5*60=300 秒
            time.sleep(5)
            task_resp = requests.get(f"{BASE_URL}/contents/generations/tasks/{task_id}", headers=headers)
            if task_resp.status_code != 200:
                continue # 忽略单次查询失败，继续轮询
            
            task_data = task_resp.json()
            status = task_data.get("status")
            
            if status == "succeeded":
                video_url = task_data.get("content", {}).get("video_url")
                return {"success": True, "video_url": video_url, "task_id": task_id}
            elif status in ("failed", "canceled"):
                return {"success": False, "error": f"Video task status: {status}"}
        
        return {"success": False, "error": "Video generation timed out."}
    except Exception as e:
        return {"success": False, "error": f"Video generation failed: {str(e)}"}

# --- 服务器入口 ---
def main():
    """主函数入口点"""
    print("Zhongyao AI Generation Server is running.")
    print("Available Tools: set_api_key, get_chinese_herb_info, get_chinese_herb_image, get_chinese_herb_video")
    # 推荐的运行方式，也可以改为 "sse" 等其他 transport
    mcp.settings.host  = "0.0.0.0"
    mcp.settings.port = 8003
    mcp.run(transport="sse")

if __name__ == "__main__":
    main()