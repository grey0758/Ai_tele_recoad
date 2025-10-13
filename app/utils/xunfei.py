"""讯飞音频转写工具"""

import os
import time
import json
import hashlib
import base64
import hmac
import requests
from urllib.parse import urlencode
from typing import Optional, Dict, Any
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class XunfeiTranscriptionService:
    """讯飞音频转写服务"""
    
    def __init__(self):
        self.app_id = settings.xunfei_app_id
        self.access_key_id = settings.xunfei_access_key_id
        self.access_key_secret = settings.xunfei_access_key_secret
        self.api_url = settings.xunfei_api_url
        
    def transcribe_audio(
        self,
        audio_path_or_url: str,
        language: str = "autodialect",
        max_wait_time: int = 300,
        poll_interval: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        转录音频文件
        
        Args:
            audio_path_or_url: 音频文件路径或URL
            language: 语言代码
            max_wait_time: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）
            **kwargs: 其他参数
            
        Returns:
            转录结果
        """
        try:
            if audio_path_or_url.startswith("http"):
                return self._transcribe_from_url(audio_path_or_url, language, max_wait_time, poll_interval, **kwargs)
            else:
                return self._transcribe_from_file(audio_path_or_url, language, max_wait_time, poll_interval, **kwargs)
        except Exception as e:
            logger.error(f"讯飞音频转写失败: {str(e)}")
            raise
    
    def _transcribe_from_url(
        self,
        audio_url: str,
        language: str,
        max_wait_time: int,
        poll_interval: int,
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
                return self._transcribe_from_file(temp_file_path, language, max_wait_time, poll_interval, **kwargs)
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"从URL转录音频失败: {str(e)}")
            raise
    
    def _transcribe_from_file(
        self,
        audio_path: str,
        language: str,
        max_wait_time: int,
        poll_interval: int,
        **kwargs
    ) -> Dict[str, Any]:
        """从文件转录音频"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_path}")
            
            task_id = self._submit_transcription_task(audio_path, language, **kwargs)
            return self._wait_for_result(task_id, max_wait_time, poll_interval)
            
        except Exception as e:
            logger.error(f"从文件转录音频失败: {str(e)}")
            raise
    
    def _submit_transcription_task(
        self,
        audio_path: str,
        language: str,
        **kwargs
    ) -> str:
        """提交转录任务"""
        try:
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            
            request_data = {
                "app_id": self.app_id,
                "language": language,
                "audio": audio_base64,
                **kwargs
            }
            
            headers = self._get_headers()
            
            response = requests.post(
                f"{self.api_url}/v1/audio/transcription",
                json=request_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"提交转录任务失败: {result.get('message', '未知错误')}")
            
            return result.get("data", {}).get("task_id")
            
        except Exception as e:
            logger.error(f"提交转录任务失败: {str(e)}")
            raise
    
    def _wait_for_result(
        self,
        task_id: str,
        max_wait_time: int,
        poll_interval: int
    ) -> Dict[str, Any]:
        """等待转录结果"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                result = self._get_task_result(task_id)
                
                if result.get("status") == "completed":
                    return result
                elif result.get("status") == "failed":
                    raise Exception(f"转录任务失败: {result.get('error', '未知错误')}")
                
                time.sleep(poll_interval)
            
            raise Exception(f"转录任务超时，等待时间超过 {max_wait_time} 秒")
            
        except Exception as e:
            logger.error(f"等待转录结果失败: {str(e)}")
            raise
    
    def _get_task_result(self, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        try:
            headers = self._get_headers()
            
            response = requests.get(
                f"{self.api_url}/v1/audio/transcription/{task_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"获取任务结果失败: {result.get('message', '未知错误')}")
            
            return result.get("data", {})
            
        except Exception as e:
            logger.error(f"获取任务结果失败: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        timestamp = str(int(time.time()))
        nonce = hashlib.md5(timestamp.encode()).hexdigest()
        
        signature = self._generate_signature(timestamp, nonce)
        
        return {
            "Content-Type": "application/json",
            "X-Request-Id": nonce,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
    
    def _generate_signature(self, timestamp: str, nonce: str) -> str:
        """生成签名"""
        string_to_sign = f"{self.access_key_id}{timestamp}{nonce}"
        signature = hmac.new(
            self.access_key_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()


def transcribe_audio_xunfei(
    audio_path_or_url: str,
    language: str = "autodialect",
    max_wait_time: int = 300,
    poll_interval: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    讯飞音频转写
    
    Args:
        audio_path_or_url: 音频文件路径或URL
        language: 语言代码
        max_wait_time: 最大等待时间（秒）
        poll_interval: 轮询间隔（秒）
        **kwargs: 其他参数
        
    Returns:
        转录结果
    """
    service = XunfeiTranscriptionService()
    return service.transcribe_audio(audio_path_or_url, language, max_wait_time, poll_interval, **kwargs)


def main():
    """测试讯飞音频转写（整合官方示例）"""
    audio_url = "https://test-1301845733.cos.ap-guangzhou.myqcloud.com/call-records/1860/OUT20251009162316T03P18628980557.mp3"

    logger.info("开始讯飞音频转写")
    result = transcribe_audio_xunfei(
        audio_url, language="autodialect", max_wait_time=300, poll_interval=5
    )

    logger.info("讯飞音频转写完成")
    logger.info(f"转录结果: {result}")


if __name__ == "__main__":
    main()
