"""
美团TTS客户端
"""

import uuid
from src.clients.base_client import MeituanBaseClient
from src.config import config
from src.utils.utils import HttpClient


class MeituanTTSClient(MeituanBaseClient):
    """美团文本转语音客户端"""

    def __init__(self):
        super().__init__(service_type="tts")

    async def synthesize(self, text: str, voice_name: str = "meishuyao",
                        speed: int = 50, volume: int = 50,
                        sample_rate: int = 24000, audio_format: str = "mp3",
                        subtitle_mode: int = 0, extend_params: str = "{}",
                        instructions: str = "{}") -> bytes:
        """
        文本转语音合成

        参数:
            text: 要合成的文本内容
            voice_name: 合成音色名称
            speed: 语速(0-100)
            volume: 音量(0-100)
            sample_rate: 采样率
            audio_format: 音频格式
            subtitle_mode: 字幕模式（0:不打开，1:字级别，2:句级别）
            extend_params: 扩展参数（JSON格式字符串）
            instructions: 指令参数（JSON格式字符串）

        返回:
            音频数据字节
        """
        token = await self.get_token()

        headers = {
            'Token': token,
            'SessionID': str(uuid.uuid4())
        }

        # 构建基础payload
        payload = {
            'text': text,
            'voice_name': voice_name,
            'speed': speed,
            'volume': volume,
            'sample_rate': sample_rate,
            'audio_format': audio_format,
            'subtitle_mode': subtitle_mode,
            'extend_params': extend_params,
            'instructions': instructions
        }

        response_data, content_type = await HttpClient.post_request(
            url=config.MEITUAN_TTS_API_URL,
            json_data=payload,
            headers=headers,
            timeout=15.0,
            expect_json=False
        )

        # 根据Content-Type判断响应类型
        if content_type.startswith('audio/'):
            # 成功：返回音频数据
            if isinstance(response_data, bytes) and len(response_data) > 0:
                self.logger.info(f"TTS合成成功: {len(response_data)} bytes")
                return response_data
            else:
                raise RuntimeError("TTS服务返回空音频数据")
                
        elif content_type.startswith('application/json'):
            # 失败：返回JSON错误信息
            error_code = response_data.get('errcode', -1)
            error_msg = response_data.get('errmsg', '未知错误')
            raise RuntimeError(f"TTS合成失败: {error_msg} (错误码: {error_code})")
        else:
            raise RuntimeError(f"TTS服务返回了未知的Content-Type: {content_type}")
