"""
ASR工具处理器
"""
import os
import tempfile
import logging
from typing import List

import mcp.types as types
from src.clients.asr_client import MeituanASRClient
from src.utils.utils import is_url, is_file_path, HttpClient

from src.tools.base import BaseToolHandler

logger = logging.getLogger(__name__)


class ASRToolHandler(BaseToolHandler):
    """ASR工具处理器"""

    def __init__(self):
        self.asr_client = MeituanASRClient()

    @staticmethod
    def get_tool_definition() -> types.Tool:
        """获取ASR工具定义"""
        return types.Tool(
            name="audio_to_text",
            description="语音转文本（ASR）",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_source": {
                        "type": "string",
                        "description": "音频来源：可以是URL或本地文件路径"
                    },
                    "audio_format": {
                        "type": "string",
                        "description": "音频格式（mp3、pcm）",
                        "default": "wav"
                    },
                    "sample_rate": {
                        "type": "integer",
                        "description": "采样率（Hz）",
                        "default": 16000
                    },
                    "channel_num": {
                        "type": "integer",
                        "description": "声道数（1:单声道，2:双声道）",
                        "default": 1
                    },
                    "scene": {
                        "type": "integer",
                        "description": "场景参数（0:通用场景，方言用17，默认0）",
                        "default": 0
                    },
                    "text_normalization": {
                        "type": "integer",
                        "description": "文本标准化（0:不使用， 默认0）",
                        "default": 0
                    },
                    "enable_subtitle": {
                        "type": "integer",
                        "description": "字幕开关（0:关闭，1:打开， 默认0）",
                        "default": 0
                    }
                },
                "required": ["audio_source"]
            },
        )

    async def handle_request(self, arguments: dict) -> List[types.TextContent]:
        """处理ASR请求"""
        # 获取参数
        audio_source = arguments.get("audio_source")
        if not audio_source:
            raise ValueError("Missing required parameter: audio_source")

        audio_format = arguments.get("audio_format", "wav")
        sample_rate = arguments.get("sample_rate", 16000)
        channel_num = arguments.get("channel_num", 1)
        scene = arguments.get("scene", 0)
        text_normalization = arguments.get("text_normalization", 0)
        enable_subtitle = arguments.get("enable_subtitle", 0)

        # 自动判断音频来源类型
        if is_url(audio_source):
            source_type = "url"
            source_info = f"🔗 音频来源: {audio_source}"
        elif is_file_path(audio_source):
            source_type = "file"
            source_info = f"📁 文件路径: {audio_source}"
        else:
            raise ValueError(f"无效的音频来源: {audio_source}，必须是有效的URL或存在的本地文件路径")

        logger.info(f"ASR请求: 来源={source_type}, 格式={audio_format}, 采样率={sample_rate}, "
                    f"场景={scene}, 文本标准化={text_normalization}, 字幕={enable_subtitle}")

        temp_file_path = None
        try:
            # 统一处理：将音频转换为本地文件
            if source_type == "url":
                # 下载到临时文件
                local_file_path = await self._download_audio_to_temp_file(audio_source)
                temp_file_path = local_file_path  # 记录临时文件，用于清理
            else:  # source_type == "file"
                local_file_path = audio_source

            # 统一使用本地文件进行处理
            # 读取音频数据进行识别
            with open(local_file_path, 'rb') as f:
                audio_data = f.read()

            # 执行ASR识别（使用传入的参数）
            recognized_text = await self.asr_client.recognize_from_binary(
                audio_data=audio_data,
                audio_format=audio_format,
                sample_rate=sample_rate,
                channel_num=channel_num,
                scene=scene,
                text_normalization=text_normalization,
                enable_subtitle=enable_subtitle
            )

            # 返回结果
            return [
                types.TextContent(
                    type="text",
                    text=f"ASR识别成功！\n"
                         f"识别结果: {recognized_text}\n"
                         f"音频参数: 格式={audio_format}, "
                         f"采样率={sample_rate}Hz, "
                         f"声道数={channel_num}\n"
                         f"{source_info}"
                )
            ]

        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"ASR识别失败: {str(e)}\n"
                         f"请检查音频文件格式和参数是否正确。"
                )
            ]

        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

    async def _download_audio_to_temp_file(self, audio_url: str) -> str:
        """
        下载音频文件到临时目录

        参数:
            audio_url: 音频文件URL

        返回:
            临时文件路径
        """
        # 下载音频数据
        audio_data = await HttpClient.get_request(
            url=audio_url,
            timeout=60.0
        )

        if not isinstance(audio_data, bytes):
            raise RuntimeError("下载的音频数据格式错误")

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        return temp_file_path