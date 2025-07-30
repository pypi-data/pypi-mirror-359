# 美团语音 MCP服务器

本项目是基于 MCP 协议的美团语音服务 Server，适用于中文开发者，支持通过 MCP 控制器（如 cursor）调用美团 TTS 能力，实现文本转语音等功能。

---

## 目录
- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [环境依赖与配置](#环境依赖与配置)
- [快速上手](#快速上手)
- [常见问题](#常见问题)
- [参考文档](#参考文档)

---

## 项目简介

本项目实现了一个 MCP 标准服务端，封装美团语音能力，适合对接 windsurf、Claude Desktop 等 MCP 控制器。支持标准的文本转语音接口，便于集成到各类自动化、AI 工具链。

---

## 功能特性
- 文本转语音（TTS）：支持指定文本、音色、语速、音量、采样率、音频格式等参数
- 语音转文本（ASR）: 支持指定音频文件格式、采样率、声道数、采样位数等参数
- 标准 MCP 协议，兼容 windsurf 等主流控制器
- 环境变量灵活配置，适合多环境部署

---

## 使用

### 依赖环境
- Python 3.10 及以上
- 已安装依赖包（见 requirements.txt）

### 获取APPKEY和SECRETKEY

| 变量名                     | 说明                   | 是否必须 |
|----------------------------|------------------------|----------|
| MEITUAN_TTS_APP_KEY        | 美团TTS服务AppKey      | 是       |
| MEITUAN_TTS_SECRET_KEY     | 美团TTS服务SecretKey   | 是       |
| MEITUAN_ASR_APP_KEY        | 美团ASR服务AppKey      | 是       |
| MEITUAN_ASR_SECRET_KEY     | 美团ASR服务SecretKey   | 是       |

### 安装uv
执行`` curl -LsSf https://astral.sh/uv/install.sh | sh ``或按照官网文档安装
### 配置MCP
已windsurf为例，在mcp_config.json中配置如下内容：
```json
{
  "mcpServers": {
    "meituan-speech-mcp-server": {
      "command": "uvx",
      "args": ["mt-speech-mcp-server", "-y"],
      "env": {
        "MEITUAN_TTS_APP_KEY": "你的TTS_AppKey",
        "MEITUAN_TTS_SECRET_KEY": "你的TTS_SecretKey",
        "MEITUAN_ASR_APP_KEY": "你的ASR_AppKey",
        "MEITUAN_ASR_SECRET_KEY": "你的ASR_SecretKey"
      }
    }
  }
}
```
具体位置参考：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
---
## 开发与调试

### 开发与调试

1. 同步依赖并更新锁文件：
   ```bash
   git clone <repository-url>
   cd speech-mcp-server
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**（见上文）

4. **配置 MCP 控制器**（windsurf 或 Claude Desktop，见上文）

5. **启动服务**：在 windsurf/Claude Desktop 中启动本服务，即可使用相关工具。

---

### 构建与发布

如需将本项目打包发布，可参考如下流程（需已安装 uv 工具）：

1. 同步依赖并更新锁文件：
   ```bash
   uv sync
   ```
2. 构建分发包：
   ```bash
   uv build
   ```
   构建结果将在 `dist/` 目录下生成。
3. 发布到 PyPI：
   ```bash
   uv publish
   ```
   发布前请配置好 PyPI 凭证，可用环境变量或命令行参数设置。

### 调试建议

由于 MCP Server 采用 stdio 通信，调试建议使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 工具。
可通过 npm 安装并运行：
```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```




- **认证失败**：检查 API 密钥是否正确配置
- **文件不存在**：确认音频文件路径是否正确
- **网络错误**：检查网络连接和 URL 有效性
- **格式不支持**：尝试使用其他音频格式或转换音频文件格式