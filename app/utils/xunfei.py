"""讯飞音频转写工具 - 基于官方demo实现"""

import os
import time
import json
import hashlib
import base64
import hmac
import requests
import tempfile
import urllib.parse
import datetime
import random
import string
import warnings
import wave
import subprocess
from typing import Optional, Dict, Any
from app.core.logger import get_logger
from app.core.config import settings

# 忽略SSL验证警告
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

logger = get_logger(__name__)

# 讯飞API基础配置
LFASR_HOST = "https://office-api-ist-dx.iflyaisol.com"
API_UPLOAD = "/v2/upload"
API_GET_RESULT = "/v2/getResult"


class XunfeiTranscriptionService:
    """讯飞音频转写服务 - 基于官方demo"""
    
    def __init__(self):
        self.app_id = str(settings.xunfei_app_id)
        self.access_key_id = str(settings.xunfei_access_key_id)
        self.access_key_secret = str(settings.xunfei_access_key_secret)
        self.signature_random = self._generate_random_str()
        self.order_id = None
    
    def _generate_random_str(self, length=16):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _get_local_time_with_tz(self):
        """生成带时区偏移的本地时间（格式：yyyy-MM-dd'T'HH:mm:ss±HHmm）"""
        local_now = datetime.datetime.now()
        tz_offset = local_now.astimezone().strftime('%z')  # 输出格式：+0800 或 -0500
        return f"{local_now.strftime('%Y-%m-%dT%H:%M:%S')}{tz_offset}"
    
    def _get_audio_duration_ms(self, audio_path: str) -> int:
        """获取音频时长（毫秒）- 基于官方demo实现"""
        try:
            # 检查文件扩展名
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext == '.wav':
                # 使用wave模块获取WAV文件时长
                with wave.open(audio_path, 'rb') as wav_file:
                    n_frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration_ms = int(round(n_frames / sample_rate * 1000))
                    logger.info("WAV文件时长: %d 毫秒", duration_ms)
                    return duration_ms
            else:
                # 对于非WAV文件，使用文件大小估算（粗略估算）
                file_size = os.path.getsize(audio_path)
                # 假设MP3文件大约128kbps，即16KB/秒
                estimated_duration_ms = int((file_size / 16000) * 1000)
                logger.info("非WAV文件，估算时长: %d 毫秒 (文件大小: %d 字节)", estimated_duration_ms, file_size)
                return max(estimated_duration_ms, 1000)  # 至少1秒
                
        except wave.Error as e:
            logger.warning("WAV文件解析失败: %s，使用文件大小估算", e)
            try:
                file_size = os.path.getsize(audio_path)
                estimated_duration_ms = int((file_size / 16000) * 1000)
                return max(estimated_duration_ms, 1000)
            except Exception:
                return 10000  # 默认10秒
        except Exception as e:
            logger.warning("获取音频时长失败: %s，使用默认值", e)
            return 10000
    
    def _convert_to_wav(self, input_path: str) -> str:
        """将音频文件转换为WAV格式（讯飞API要求）"""
        try:
            file_ext = os.path.splitext(input_path)[1].lower()
            if file_ext == '.wav':
                return input_path  # 已经是WAV格式
            
            # 创建临时WAV文件
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            
            # 使用ffmpeg转换音频格式
            cmd = [
                'ffmpeg', '-i', input_path, 
                '-acodec', 'pcm_s16le',  # 16位PCM编码
                '-ar', '16000',          # 16kHz采样率
                '-ac', '1',              # 单声道
                '-y',                    # 覆盖输出文件
                temp_wav.name
            ]
            
            logger.info("转换音频格式: %s -> %s", input_path, temp_wav.name)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("音频格式转换成功")
                return temp_wav.name
            else:
                logger.error("音频格式转换失败: %s", result.stderr)
                os.unlink(temp_wav.name)
                raise Exception(f"音频格式转换失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("音频格式转换超时")
            if 'temp_wav' in locals():
                os.unlink(temp_wav.name)
            raise Exception("音频格式转换超时")
        except FileNotFoundError:
            logger.error("ffmpeg未安装，无法转换音频格式")
            raise Exception("ffmpeg未安装，请安装ffmpeg或使用WAV格式音频")
        except Exception as e:
            logger.error("音频格式转换异常: %s", e)
            if 'temp_wav' in locals():
                os.unlink(temp_wav.name)
            raise
    
    def generate_signature(self, params):
        """生成签名（根据官方demo的算法）"""
        # 排除signature参数，按参数名自然排序
        sign_params = {k: v for k, v in params.items() if k != "signature"}
        sorted_params = sorted(sign_params.items(), key=lambda x: x[0])
        
        # 构建baseString：对key和value都进行URL编码
        base_parts = []
        for k, v in sorted_params:
            if v is not None and str(v).strip() != "":
                encoded_key = urllib.parse.quote(k, safe='')  # 参数名编码
                encoded_value = urllib.parse.quote(str(v), safe='')  # 参数值编码
                base_parts.append(f"{encoded_key}={encoded_value}")
        
        base_string = "&".join(base_parts)
        
        # HMAC-SHA1加密 + Base64编码
        hmac_obj = hmac.new(
            self.access_key_secret.encode("utf-8"),
            base_string.encode("utf-8"),
            digestmod="sha1"
        )
        signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")
        return signature
    
    def upload_audio(self, audio_path: str) -> Dict[str, Any]:
        """上传音频文件"""
        wav_path = None
        try:
            # 1. 转换为WAV格式（讯飞API要求）
            wav_path = self._convert_to_wav(audio_path)
            
            # 2. 基础参数准备
            audio_size = str(os.path.getsize(wav_path))  # 音频文件大小（字节）
            audio_name = os.path.basename(wav_path)      # 音频文件名
            date_time = self._get_local_time_with_tz()     # 带时区的本地时间
            duration = self._get_audio_duration_ms(wav_path)  # 音频时长（毫秒）
            
            logger.info("上传音频文件: %s, 大小: %s 字节, 时长: %s 毫秒", audio_name, audio_size, duration)

            # 2. 构建URL参数
            url_params = {
                "appId": self.app_id,
                "accessKeyId": self.access_key_id,
                "dateTime": date_time,
                "signatureRandom": self.signature_random,
                "fileSize": audio_size,
                "fileName": audio_name,
                "language": "autodialect",
                "duration": str(duration)  # 音频时长（毫秒，整数字符串）
            }

            # 3. 生成签名
            signature = self.generate_signature(url_params)
            if not signature:
                raise Exception("签名生成失败，结果为空")

            # 4. 构建请求头
            headers = {
                "Content-Type": "application/octet-stream",
                "signature": signature
            }

            # 5. 构建最终请求URL
            encoded_params = []
            for k, v in url_params.items():
                encoded_key = urllib.parse.quote(k, safe='')
                encoded_v = urllib.parse.quote(str(v), safe='')
                encoded_params.append(f"{encoded_key}={encoded_v}")
            upload_url = f"{LFASR_HOST}{API_UPLOAD}?{'&'.join(encoded_params)}"

            # 6. 读取音频文件并发送POST请求
            with open(wav_path, "rb") as f:
                audio_data = f.read()

            response = requests.post(
                url=upload_url,
                headers=headers,
                data=audio_data,
                timeout=30,
                verify=False  # 测试环境关闭SSL验证
            )
            response.raise_for_status()

            # 7. 解析响应结果
            result = json.loads(response.text)
            logger.info("上传结果: %s", result)

            # 8. 处理API业务错误
            if result.get("code") != "000000":
                raise Exception(
                    f"上传失败（API错误）：\n"
                    f"错误码：{result.get('code')}\n"
                    f"错误描述：{result.get('descInfo', '未知错误')}"
                )

            # 9. 上传成功，记录订单ID
            self.order_id = result["content"]["orderId"]
            logger.info("上传成功！订单ID：%s", self.order_id)
            return result

        except Exception as e:
            logger.error("上传音频文件失败: %s", e)
            raise
        finally:
            # 清理临时WAV文件
            if wav_path and wav_path != audio_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                    logger.info("已清理临时WAV文件: %s", wav_path)
                except Exception as e:
                    logger.warning("清理临时文件失败: %s", e)

    def get_transcribe_result(self) -> Dict[str, Any]:
        """查询音频转写结果（轮询直到完成/超时）"""
        if not self.order_id:
            raise Exception("未获取到订单ID，无法查询转写结果")

        # 构建查询参数
        query_params = {
            "appId": self.app_id,
            "accessKeyId": self.access_key_id,
            "dateTime": self._get_local_time_with_tz(),
            "ts": str(int(time.time())),  # 秒级时间戳
            "orderId": self.order_id,
            "signatureRandom": self.signature_random
        }

        # 生成查询签名
        query_signature = self.generate_signature(query_params)
        query_headers = {
            "Content-Type": "application/json",
            "signature": query_signature
        }

        # 构建查询URL
        encoded_query_params = []
        for k, v in query_params.items():
            encoded_key = urllib.parse.quote(k, safe='')
            encoded_v = urllib.parse.quote(str(v), safe='')
            encoded_query_params.append(f"{encoded_key}={encoded_v}")
        query_url = f"{LFASR_HOST}{API_GET_RESULT}?{'&'.join(encoded_query_params)}"

        # 轮询查询
        max_retry = 100
        retry_count = 0
        while retry_count < max_retry:
            try:
                response = requests.post(
                    url=query_url,
                    headers=query_headers,
                    data=json.dumps({}),
                    timeout=15,
                    verify=False
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise Exception(f"查询请求网络失败：{str(e)}")

            try:
                result = json.loads(response.text)
                # logger.info("查询结果: %s", result)
            except json.JSONDecodeError:
                raise Exception(f"查询响应非JSON数据：{response.text}")

            if result.get("code") != "000000":
                raise Exception(f"查询失败（API错误）：{result.get('descInfo', '未知错误')}")

            # 转写状态：3=处理中，4=完成，-1=失败
            process_status = result["content"]["orderInfo"]["status"]
            if process_status == 4:
                logger.info("转写完成！")
                return result
            elif process_status == -1:
                # 转写失败
                fail_type = result["content"]["orderInfo"].get("failType", "未知")
                raise Exception(f"转写失败：失败类型={fail_type}，描述={result.get('descInfo', '未知错误')}")
            elif process_status != 3:
                raise Exception(f"转写异常：状态码={process_status}，描述={result.get('descInfo', '未知错误')}")

            # 处理中，等待后重试
            retry_count += 1
            logger.info("转写处理中（已查询%d/%d次），10秒后再次查询...", retry_count, max_retry)
            time.sleep(10)

        raise Exception(f"查询超时：已重试{max_retry}次，订单ID：{self.order_id}")
        
    def transcribe_audio(
        self,
        audio_path_or_url: str,
        language: str = "autodialect",
        max_wait_time: int = 300,
        poll_interval: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        转录音频文件或URL
        
        Args:
            audio_path_or_url: 音频文件路径或URL
            language: 语言设置
            max_wait_time: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）
            
        Returns:
            转录结果字典
        """
        try:
            if audio_path_or_url.startswith(('http://', 'https://')):
                return self._transcribe_from_url(audio_path_or_url, language, max_wait_time, poll_interval)
            else:
                return self._transcribe_from_file(audio_path_or_url, language, max_wait_time, poll_interval)
        except Exception as e:
            logger.error("讯飞音频转写失败: %s", e)
            return {"success": False, "error": str(e), "text": ""}

    def _transcribe_from_file(self, audio_path: str, language: str, max_wait_time: int, poll_interval: int) -> Dict[str, Any]:
        """从文件转录音频"""
        try:
            if not os.path.exists(audio_path):
                raise Exception(f"音频文件不存在: {audio_path}")
            
            # 上传音频文件
            self.upload_audio(audio_path)
            
            # 获取转写结果
            result = self.get_transcribe_result()
            
            # 解析转写结果
            text = self._parse_transcription_result(result)
            
            return {
                "success": True,
                "text": text,
                "order_id": self.order_id,
                "raw_result": result
            }
            
        except Exception as e:
            logger.error("从文件转录音频失败: %s", e)
            return {"success": False, "error": str(e), "text": ""}

    def _transcribe_from_url(self, audio_url: str, language: str, max_wait_time: int, poll_interval: int) -> Dict[str, Any]:
        """从URL转录音频"""
        try:
            # 下载音频文件到临时文件
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                # 使用临时文件进行转录
                result = self._transcribe_from_file(temp_file_path, language, max_wait_time, poll_interval)
                return result
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error("从URL转录音频失败: %s", e)
            return {"success": False, "error": str(e), "text": ""}

    def _parse_transcription_result(self, result: Dict[str, Any]) -> str:
        """解析转写结果，提取文本"""
        try:
            # 从API响应中获取orderResult字段
            order_result_str = result.get('content', {}).get('orderResult', '{}')
            
            # 处理转义字符问题
            import re
            cleaned_str = re.sub(r'\\\\', r'\\', order_result_str)
            
            # 解析orderResult字符串为JSON对象
            order_result = json.loads(cleaned_str)
            
            # 提取所有w字段的值
            w_values = []
            
            # 遍历lattice数组
            if 'lattice' in order_result:
                for lattice_item in order_result['lattice']:
                    if 'json_1best' in lattice_item:
                        # 解析json_1best字段
                        json_1best = json.loads(lattice_item['json_1best'])
                        
                        # 处理st对象
                        if 'st' in json_1best and 'rt' in json_1best['st']:
                            for rt_item in json_1best['st']['rt']:
                                if 'ws' in rt_item:
                                    for ws_item in rt_item['ws']:
                                        if 'cw' in ws_item:
                                            for cw_item in ws_item['cw']:
                                                if 'w' in cw_item:
                                                    w_values.append(cw_item['w'])
            
            # 拼接所有w值
            return ''.join(w_values)
            
        except Exception as e:
            logger.error("解析转写结果失败: %s", e)
            return ""


def transcribe_audio_xunfei(
    audio_path_or_url: str,
    language: str = "autodialect",
    max_wait_time: int = 300,
    poll_interval: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    讯飞音频转写函数
    
    Args:
        audio_path_or_url: 音频文件路径或URL
        language: 语言设置
        max_wait_time: 最大等待时间（秒）
        poll_interval: 轮询间隔（秒）
        
    Returns:
        转录结果字典
    """
    service = XunfeiTranscriptionService()
    return service.transcribe_audio(audio_path_or_url, language, max_wait_time, poll_interval, **kwargs)