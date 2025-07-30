import moviepy as mpe
from moviepy.config import change_settings;
from qcloud_cos import CosConfig, CosS3Client
import tempfile
import requests
import datetime
import os
import random
from typing import Any, Dict
import configparser
# 新增：用于测试的工具（生成临时测试文件）
import uuid

# --- 全局配置 (从 config.ini 加载) ---
API_KEY = None
BASE_URL = None
DEFAULT_CHAT_MODEL = None
DEFAULT_IMAGE_MODEL = None
DEFAULT_VIDEO_MODEL = None

TTS_API_KEY = None
TTS_BASE_URL = None
COS_REGION = None
COS_SECRET_ID = None
COS_SECRET_KEY = None
COS_BUCKET = None
IMAGEMAGICK_BINARY = None

change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

# --- 加载配置 ---
def load_config():
    """从 config.ini 文件加载配置"""
    global API_KEY, BASE_URL, DEFAULT_CHAT_MODEL, DEFAULT_IMAGE_MODEL, DEFAULT_VIDEO_MODEL
    global TTS_API_KEY, TTS_BASE_URL, COS_REGION, COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET
    
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    if not os.path.exists(config_file):
        print(f"错误: 配置文件 '{config_file}' 未找到。")
        print("请在脚本同目录下创建一个 'config.ini' 文件，并包含所需内容")
        return

    config.read(config_file)

    try:
        API_KEY = config.get('API', 'api_key', fallback=None)
        BASE_URL = config.get('API', 'base_url', fallback='https://ark.cn-beijing.volces.com/api/v3')
        DEFAULT_CHAT_MODEL = config.get('Models', 'chat_model', fallback='deepseek-V3')
        DEFAULT_IMAGE_MODEL = config.get('Models', 'image_model', fallback='doubao-seedream-3-0-t2i-250415')
        DEFAULT_VIDEO_MODEL = config.get('Models', 'video_model', fallback='doubao-seedance-1-0-lite-t2v-250428')
        
        TTS_API_KEY = config.get('edgetts', 'tts_api_key', fallback=None)
        TTS_BASE_URL = config.get('edgetts', 'tts_base_url', fallback=None)
        
        COS_REGION = config.get('common', 'cos_region', fallback=None)
        COS_SECRET_ID = config.get('common', 'cos_secret_id', fallback=None)
        COS_SECRET_KEY = config.get('common', 'cos_secret_key', fallback=None)
        COS_BUCKET = config.get('common', 'cos_bucket', fallback=None)
        IMAGEMAGICK_BINARY = config.get('common', 'imagemagick_binary', fallback=None)

        print("配置已从 config.ini 成功加载。")
        if not API_KEY or API_KEY == 'YOUR_DOUBAO_API_KEY_HERE':
            print("警告: 'config.ini' 中的 [API] api_key 未设置或仍为占位符。")
            API_KEY = None
        if not COS_SECRET_ID or 'YOUR_COS_SECRET_ID' in COS_SECRET_ID:
            print("警告: 'config.ini' 中的 [common] COS配置 未正确设置。TTS和视频合成功能将不可用。")

    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"读取配置文件时出错: {e}")
        print("请确保 'config.ini' 包含 [API], [Models], [edgetts] 和 [common] 部分")


load_config()


# --- 视频、音频、文字合成函数 ---
def _combine_video_audio_text(video_url: str, audio_url: str, subtitle_text: str, herb_name: str) -> Dict[str, Any]:
    """
    将视频、音频和文字（字幕）合成为一个新的视频文件，并上传到COS。
    """
    if not mpe:
        return {"success": False, "error": "MoviePy library is not available. Cannot combine video."}
    if not all([COS_REGION, COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET]):
        return {"success": False, "error": "COS configuration is missing. Cannot upload final video."}

    video_clip = audio_clip = final_clip = None
    try:
        # 使用临时文件处理下载和最终输出
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file, \
             tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
            
            # 1. 下载视频和音频
            print("Downloading video and audio for processing...")
            video_content = requests.get(video_url, stream=True).content
            temp_video_file.write(video_content)
            temp_video_file.flush()

            audio_content = requests.get(audio_url, stream=True).content
            temp_audio_file.write(audio_content)
            temp_audio_file.flush()

            # 2. 使用 moviepy 加载和处理
            print("Combining video, audio, and subtitles with MoviePy...")
            video_clip = mpe.VideoFileClip(temp_video_file.name)
            audio_clip = mpe.AudioFileClip(temp_audio_file.name)

            # 将新音频设置到视频上
            final_clip = video_clip.set_audio(audio_clip)

            # 确保视频时长不超过音频时长
            if final_clip.duration > audio_clip.duration:
                 final_clip = final_clip.subclip(0, audio_clip.duration)

            # 3. 创建和添加字幕
            txt_clip = mpe.TextClip(
                subtitle_text,
                fontsize=40,
                color='yellow',
                font='SimHei',  # 确保服务器有此字体（无则替换为系统字体）
                bg_color='rgba(0, 0, 0, 0.5)',
                size=(final_clip.w * 0.9, None),
                method='caption'
            )
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(final_clip.duration)
            
            # 组合视频和字幕
            video_with_subs = mpe.CompositeVideoClip([final_clip, txt_clip])

            # 4. 导出最终视频到临时文件
            print("Exporting final video...")
            final_filename = f"{_generate_timestamp_filename('mp4')}"
            final_filepath_temp = os.path.join(tempfile.gettempdir(), final_filename)
            video_with_subs.write_videofile(final_filepath_temp, codec="libx264", audio_codec="aac")

            # 5. 上传到COS
            print(f"Uploading final video '{final_filename}' to COS...")
            with open(final_filepath_temp, 'rb') as f_final:
                final_video_content = f_final.read()
            
            upload_result = _upload_to_cos_from_memory(final_video_content, final_filename)
            os.remove(final_filepath_temp)  # 删除本地临时文件
            return upload_result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Failed during video combination process: {str(e)}"}
    finally:
        # 清理资源
        if video_clip: video_clip.close()
        if audio_clip: audio_clip.close()
        if final_clip: final_clip.close()
        # 删除临时文件
        for temp_file in [temp_video_file.name, temp_audio_file.name]:
            if os.path.exists(temp_file):
                os.remove(temp_file)


# --- 辅助函数 ---
def _generate_timestamp_filename(extension='mp3'):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)
    filename = f"{timestamp}_{random_number}.{extension}"
    return filename


def _upload_to_cos_from_memory(file_content: bytes, file_name: str) -> Dict[str, Any]:
    try:
        config = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
        client = CosS3Client(config)
        
        response = client.put_object(
            Bucket=COS_BUCKET,
            Body=file_content,
            Key=file_name,
            EnableMD5=False
        )
        
        if response and response.get('ETag'):
            url = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{file_name}"
            return {"success": True, "url": url, "etag": response['ETag']}
        else:
            return {"success": False, "error": f"Upload to COS failed. Response: {response}"}
            
    except Exception as e:
        return {"success": False, "error": f"An error occurred during COS upload: {str(e)}"}


# --- 新增：测试函数 ---
def test_combine_video_audio_text():
    """
    测试视频、音频、字幕合成功能。
    注意：需确保有可用的测试视频/音频URL，或替换为本地文件路径。
    """
    print("\n===== Starting _combine_video_audio_text test =====")
    
    # 1. 测试用参数（可替换为实际可用的URL）
    # 这里使用公开的测试视频和音频URL（若不可用，需自行替换）
    test_video_url = "https://ark-content-generation-cn-beijing.tos-cn-beijing.volces.com/doubao-seedance-1-0-lite-t2v/02175112786717200000000000000000000ffffac15900ced14c2.mp4?X-Tos-Algorithm=TOS4-HMAC-SHA256&X-Tos-Credential=AKLTYjg3ZjNlOGM0YzQyNGE1MmI2MDFiOTM3Y2IwMTY3OTE%2F20250628%2Fcn-beijing%2Ftos%2Frequest&X-Tos-Date=20250628T162456Z&X-Tos-Expires=86400&X-Tos-Signature=0a9c68f29819b3a3e9eb77a7ed6c43ace23da01ab23307bd7ec79f56d55a254a&X-Tos-SignedHeaders=host"  # 10秒测试视频
    test_audio_url = "https://tts-1258720957.cos.ap-nanjing.myqcloud.com/20250629002419_4814.mp3"  # 测试音频
    test_subtitle = "麻黄为麻黄科植物草麻黄、中麻黄或木贼麻黄的干燥草质茎。多年生草本状小灌木，高20-40厘米。木质茎匍匐土中；草质茎直立，黄绿色，节间细长，有细纵槽纹。叶膜质鞘状，上部2裂，裂片锐三角形。雌雄异株，雄球花多成复穗状；雌球花单生枝顶，成熟时苞片增大，肉质，红色，成浆果状。种子2粒"  # 测试字幕
    test_herb_name = "麻黄"  # 药材名称（用于标识）
    
    # 2. 调用合成函数
    result = _combine_video_audio_text(
        video_url=test_video_url,
        audio_url=test_audio_url,
        subtitle_text=test_subtitle,
        herb_name=test_herb_name
    )
    
    # 3. 输出测试结果
    print("\n===== Test Result =====")
    if result["success"]:
        print(f"合成成功！视频URL: {result['url']}")
        print(f"ETag: {result['etag']}")
    else:
        print(f"合成失败！错误信息: {result['error']}")
    print("=======================")


# --- 当脚本直接运行时执行测试 ---
if __name__ == "__main__":
    # 执行测试（确保config.ini中COS配置正确，否则会上传失败）
    test_combine_video_audio_text()