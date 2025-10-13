"""音频转录工具"""

import os
import tempfile
import requests
from typing import Optional, Dict, Any
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def transcribe_audio(
    audio_path_or_url: str,
    model: str = "whisper-1",
    language: str = "zh",
    temperature: float = 0,
    **kwargs
) -> Dict[str, Any]:
    """
    转录音频文件
    
    Args:
        audio_path_or_url: 音频文件路径或URL
        model: 转录模型
        language: 语言代码
        temperature: 温度参数
        **kwargs: 其他参数
        
    Returns:
        转录结果
    """
    try:
        if audio_path_or_url.startswith("http"):
            return _transcribe_from_url(audio_path_or_url, model, language, temperature, **kwargs)
        else:
            return _transcribe_from_file(audio_path_or_url, model, language, temperature, **kwargs)
    except Exception as e:
        logger.error(f"音频转录失败: {str(e)}")
        raise


def _transcribe_from_url(
    audio_url: str,
    model: str,
    language: str,
    temperature: float,
    **kwargs
) -> Dict[str, Any]:
    """从URL转录音频"""
    try:
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        try:
            return _transcribe_from_file(temp_file_path, model, language, temperature, **kwargs)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"从URL转录音频失败: {str(e)}")
        raise


def _transcribe_from_file(
    audio_path: str,
    model: str,
    language: str,
    temperature: float,
    **kwargs
) -> Dict[str, Any]:
    """从文件转录音频"""
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        with open(audio_path, "rb") as audio_file:
            files = {"file": audio_file}
            data = {
                "model": model,
                "language": language,
                "temperature": temperature,
                **kwargs
            }
            
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}"
            }
            
            response = requests.post(
                f"{settings.openai_url}/v1/audio/transcriptions",
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
            return response.json()
            
    except Exception as e:
        logger.error(f"从文件转录音频失败: {str(e)}")
        raise


def main():
    """
    测试音频转录
    """
    audio_url = "https://test-1301845733.cos.ap-guangzhou.myqcloud.com/call-records/1860/OUT20251009162316T03P18628980557.mp3"
    logger.info("开始转录音频")
    result = transcribe_audio(
        audio_url, model="whisper-1", language="zh", temperature=0
    )

    logger.info("音频转录完成")
    logger.info(f"转录结果: {result}")


if __name__ == "__main__":
    main()
