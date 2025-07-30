"""
TTS工具处理器
"""
import os
import uuid
import logging
from typing import List

import mcp.types as types

from src.tools.base import BaseToolHandler
from src.clients.tts_client import MeituanTTSClient
from src.config import config

logger = logging.getLogger(__name__)


class TTSToolHandler(BaseToolHandler):
    """TTS工具处理器"""

    def __init__(self):
        self.tts_client = MeituanTTSClient()

    @staticmethod
    def get_tool_definition() -> types.Tool:
        """获取TTS工具定义"""
        return types.Tool(
            name="text_to_audio",
            description="文本转语音（TTS）",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要合成的文本内容"
                    },
                    "voice_name": {
                        "type": "string",
                        "description": "合成音色名称",
                        "default": "meishuyao"
                    },
                    "speed": {
                        "type": "integer",
                        "description": "语速(0-100)",
                        "default": 50
                    },
                    "volume": {
                        "type": "integer",
                        "description": "音量(0-100)",
                        "default": 50
                    },
                    "sample_rate": {
                        "type": "integer",
                        "description": "采样率",
                        "default": 24000
                    },
                    "audio_format": {
                        "type": "string",
                        "description": "音频格式",
                        "default": "mp3"
                    },
                    "audio_type": {
                        "type": "string",
                        "description": "音频形式，可选[file]",
                        "default": "file"
                    },
                    "subtitle_mode": {
                        "type": "integer",
                        "description": "字幕模式（0:不打开，1:字级别，2:句级别）",
                        "default": 0
                    },
                    "extend_params": {
                        "type": "string",
                        "description": "扩展参数（JSON格式转义后字符串）",
                        "default": "{}"
                    },
                    "instructions": {
                        "type": "string",
                        "description": "指令参数（JSON格式转义后字符串）",
                        "default": "{}"
                    }
                },
                "required": ["text"]
            },
        )

    async def handle_request(self, arguments: dict) -> List[types.TextContent]:
        """处理TTS请求"""
        # 获取参数
        text = arguments.get("text")
        if not text:
            raise ValueError("Missing required parameter: text")

        voice_name = arguments.get("voice_name", "meishuyao")
        speed = arguments.get("speed", 50)
        volume = arguments.get("volume", 50)
        sample_rate = arguments.get("sample_rate", 24000)
        audio_format = arguments.get("audio_format", "mp3")
        audio_type = arguments.get("audio_type", "file")
        subtitle_mode = arguments.get("subtitle_mode", 0)
        extend_params = arguments.get("extend_params", "{}")
        instructions = arguments.get("instructions", "{}")


        logger.info(f"TTS请求: 文本='{text[:30]}...', 音色={voice_name}")

        audio_bytes = await self.tts_client.synthesize(
            text=text,
            voice_name=voice_name,
            speed=speed,
            volume=volume,
            sample_rate=sample_rate,
            audio_format=audio_format,
            subtitle_mode=subtitle_mode,
            extend_params=extend_params,
            instructions=instructions

        )

        # 保存音频文件
        if audio_type == "file":
            file_path = self._save_audio_to_file(audio_bytes, audio_format)
            result = f"TTS合成成功，音频文件已保存: {file_path}\n访问路径: file://{file_path}"
            logger.info(f"TTS文件保存成功: {file_path}")
        else:
            result = "暂不支持URL形式输出"

        return [
            types.TextContent(
                type="text",
                text=result
            )
        ]

    def _save_audio_to_file(self, audio_bytes: bytes, audio_format: str, filename: str = None) -> str:
        """
        保存音频数据到本地文件

        参数:
            audio_bytes: 音频字节数据
            audio_format: 音频格式（如mp3, wav等）
            filename: 可选的文件名，不提供则自动生成

        返回:
            保存的文件路径
        """
        # 确保临时目录存在
        os.makedirs(config.TEMP_DIR, exist_ok=True)

        # 生成文件名
        if filename is None:
            filename = f"tts_output_{uuid.uuid4().hex[:8]}.{audio_format}"
        elif not filename.endswith(f".{audio_format}"):
            filename = f"{filename}.{audio_format}"

        # 构建完整文件路径
        file_path = os.path.join(config.TEMP_DIR, filename)

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        return file_path
