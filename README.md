# Open NotebookLM

Open NotebookLM 是一款开源工具，能够将 PDF 文档和网页内容转换为引人入胜的播客内容。它集成了国内主流大模型和 TTS 服务，为用户提供了一种全新的内容消费方式。

## 核心价值

- **高效内容转换**：将静态文档转换为动态播客，提高内容消费效率
- **多平台支持**：集成多种国内大模型和 TTS 服务，灵活选择
- **易于使用**：直观的 Web 界面，无需复杂操作
- **高度可扩展**：模块化设计，支持轻松添加新模型和服务

## 适用场景

- 学术论文解读
- 技术文档讲解
- 新闻资讯播客
- 教育内容制作
- 个人笔记分享

## 功能特性

### 内容输入
- 📄 **PDF文档支持**：支持上传单个或多个PDF文件，自动提取文本内容
- 🔗 **网页内容提取**：支持从URL获取网页内容，自动解析和提取

### 大模型支持
- 🤖 **多平台集成**：支持多种国内大模型平台
  - 百度文心一言
  - 阿里通义千问
  - 硅基流动
- 🎯 **智能对话生成**：基于输入内容生成自然、流畅的对话脚本
- 🎭 **多种语气选择**：支持有趣、正式等多种语气
- ⏱️ **灵活长度控制**：支持短（1-2分钟）、中（3-5分钟）等多种长度

### TTS服务
- 🎤 **多服务支持**：集成多种国内TTS服务
  - 百度语音合成
  - 阿里语音合成
  - 讯飞语音合成
- 🔊 **多种音色选择**：支持不同性别、风格的音色
- 🌐 **多语言支持**：支持中文、英文等多种语言

### 用户体验
- 🎨 **直观Web界面**：简洁易用的图形化操作界面
- ⚡ **快速生成**：高效的内容处理和生成流程
- 📝 **自动生成字幕**：同步生成播客字幕
- 🔄 **灵活配置**：支持自定义各种参数

### 技术特性
- 📦 **模块化设计**：高度可扩展的代码架构
- 🔧 **易于部署**：简单的安装和配置流程
- 📖 **完整文档**：详细的使用和开发文档
- 🤝 **开源协作**：支持社区贡献和扩展

## 安装依赖

### 1. 准备工作

#### 虚拟环境建议
为了避免依赖冲突，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
env\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境变量管理

项目支持使用 `.env` 文件管理环境变量，建议使用 `python-dotenv` 库加载：

```bash
# 安装 python-dotenv（已包含在 requirements.txt 中）
pip install python-dotenv
```

### 4. 依赖说明

- **大模型依赖**：
  - `erniebot`：百度文心一言 SDK
  - `litellm`：大模型调用统一接口

- **TTS依赖**：
  - `baidu-aip`：百度语音合成 SDK

- **Web界面依赖**：
  - `gradio`：Web界面框架

- **其他核心依赖**：
  - `pydantic`：数据验证
  - `pypdf`：PDF解析
  - `pydub`：音频处理

## 环境变量配置

### 1. 使用.env文件配置

项目支持使用 `.env` 文件管理环境变量，创建一个 `.env` 文件在项目根目录，内容如下：

```env
# 百度文心一言配置
ERNIE_API_KEY="你的百度文心一言API密钥"
ERNIE_SECRET_KEY="你的百度文心一言Secret Key"

# 阿里通义千问配置（可选）
QIANWEN_API_KEY="你的阿里通义千问API密钥"
QIANWEN_SECRET_KEY="你的阿里通义千问Secret Key"

# 硅基流动配置（可选）
SILICONFLOW_API_KEY="你的硅基流动API密钥"

# 百度语音合成配置
BAIDU_APP_ID="你的百度语音合成App ID"
BAIDU_API_KEY="你的百度语音合成API Key"
BAIDU_SECRET_KEY="你的百度语音合成Secret Key"

# 阿里语音合成配置（可选）
ALI_ACCESS_KEY_ID="你的阿里云Access Key ID"
ALI_ACCESS_KEY_SECRET="你的阿里云Access Key Secret"
ALI_APP_KEY="你的阿里云语音合成App Key"

# 讯飞语音合成配置（可选）
XUNFEI_APP_ID="你的讯飞语音合成App ID"
XUNFEI_API_KEY="你的讯飞语音合成API Key"
XUNFEI_API_SECRET="你的讯飞语音合成API Secret"

# 默认配置
DEFAULT_LLM_PLATFORM="ernie"  # 默认大模型平台：ernie, qianwen, siliconflow
DEFAULT_TTS_SERVICE="baidu"   # 默认TTS服务：baidu, ali, xunfei
```

### 2. 环境变量说明

#### 大模型平台配置

| 环境变量 | 说明 | 必需 | 默认值 |
|---------|------|------|--------|
| ERNIE_API_KEY | 百度文心一言API密钥 | 是 | - |
| ERNIE_SECRET_KEY | 百度文心一言Secret Key | 是 | - |
| QIANWEN_API_KEY | 阿里通义千问API密钥 | 否 | - |
| QIANWEN_SECRET_KEY | 阿里通义千问Secret Key | 否 | - |
| SILICONFLOW_API_KEY | 硅基流动API密钥 | 否 | - |

#### TTS服务配置

| 环境变量 | 说明 | 必需 | 默认值 |
|---------|------|------|--------|
| BAIDU_APP_ID | 百度语音合成App ID | 是 | - |
| BAIDU_API_KEY | 百度语音合成API Key | 是 | - |
| BAIDU_SECRET_KEY | 百度语音合成Secret Key | 是 | - |
| ALI_ACCESS_KEY_ID | 阿里云Access Key ID | 否 | - |
| ALI_ACCESS_KEY_SECRET | 阿里云Access Key Secret | 否 | - |
| ALI_APP_KEY | 阿里云语音合成App Key | 否 | - |
| XUNFEI_APP_ID | 讯飞语音合成App ID | 否 | - |
| XUNFEI_API_KEY | 讯飞语音合成API Key | 否 | - |
| XUNFEI_API_SECRET | 讯飞语音合成API Secret | 否 | - |

#### 默认配置

| 环境变量 | 说明 | 必需 | 默认值 |
|---------|------|------|--------|
| DEFAULT_LLM_PLATFORM | 默认大模型平台 | 否 | ernie |
| DEFAULT_TTS_SERVICE | 默认TTS服务 | 否 | baidu |

### 3. 环境变量优先级

环境变量的加载优先级：
1. 命令行导出的环境变量
2. `.env` 文件中的配置
3. 代码中的默认值

### 4. 获取API密钥

- **百度文心一言**：[百度智能云控制台](https://console.bce.baidu.com/)
- **阿里通义千问**：[阿里云控制台](https://console.aliyun.com/)
- **硅基流动**：[硅基流动官网](https://siliconflow.cn/)
- **百度语音合成**：[百度智能云控制台](https://console.bce.baidu.com/)
- **阿里语音合成**：[阿里云控制台](https://console.aliyun.com/)
- **讯飞语音合成**：[讯飞开放平台](https://www.xfyun.cn/)

## 运行项目

### 1. 基本运行

```bash
python app.py
```

运行成功后，在浏览器中访问输出的URL，通常是 `http://localhost:7860`。

### 2. 运行选项

```bash
# 自定义端口
python app.py --port 8080

# 允许外部访问
python app.py --share

# 启用调试模式
python app.py --debug

# 指定配置文件
python app.py --config config.json
```

### 3. 后台运行

在Linux/macOS系统上，可以使用 `nohup` 或 `screen` 命令在后台运行：

```bash
# 使用 nohup
nohup python app.py > app.log 2>&1 &

# 使用 screen
screen -S notebooklm python app.py
```

### 4. 常见问题解决

#### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :7860

# 终止占用端口的进程
kill -9 <PID>
```

#### 环境变量未加载
确保 `.env` 文件在项目根目录，并且 `python-dotenv` 已安装。

#### 依赖冲突
尝试使用虚拟环境重新安装依赖：
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### API调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查API服务是否正常

### 5. 停止项目

- **前台运行**：按 `Ctrl+C` 停止
- **后台运行**：
  ```bash
  # 查找进程ID
  ps aux | grep app.py
  # 终止进程
  kill -9 <PID>
  ```

### 6. 访问Web界面

成功运行后，在浏览器中访问：
- 本地访问：`http://localhost:7860`
- 外部访问（使用 --share）：输出的公网URL

### 7. API文档

项目提供了API接口，访问以下地址查看API文档：
- `http://localhost:7860/docs`
- `http://localhost:7860/redoc`

## 使用方法

### 1. 准备内容

#### 上传PDF文件
- 点击"上传您的PDF文件"按钮
- 选择一个或多个PDF文件
- 系统会自动提取PDF中的文本内容

#### 输入URL（可选）
- 在"粘贴URL"输入框中输入网页地址
- 系统会自动获取并解析网页内容
- 支持新闻、博客、文档等多种网页类型

### 2. 配置生成参数

#### 输入问题或主题
- 在"您有特定的问题或主题吗？"输入框中输入
- 例如："用5岁孩子能理解的方式解释这篇论文"
- 这将引导大模型生成相关的对话内容

#### 选择语气
- 从下拉菜单中选择播客的语气
- **有趣**：适合轻松、娱乐性内容
- **正式**：适合学术、专业内容

#### 选择长度
- 从下拉菜单中选择播客的长度
- **短（1-2分钟）**：适合快速了解核心内容
- **中（3-5分钟）**：适合深入探讨主题

#### 选择语言
- 从下拉菜单中选择播客的语言
- 支持中文、英文等多种语言

#### 选择大模型平台
- 从下拉菜单中选择要使用的大模型平台
- 百度文心一言、阿里通义千问、硅基流动

#### 选择TTS服务
- 从下拉菜单中选择要使用的TTS服务
- 百度语音合成、阿里语音合成、讯飞语音合成

#### 高级音频生成（可选）
- 勾选"使用高级音频生成？"复选框
- 提供更自然、流畅的语音效果
- 生成时间可能更长

### 3. 生成播客

- 点击"生成播客"按钮
- 等待系统处理和生成
- 生成时间取决于内容长度和复杂度

### 4. 查看和使用结果

#### 播放播客
- 在"播客"输出框中点击播放按钮
- 调整音量和播放进度
- 支持下载生成的音频文件

#### 查看文本记录
- 在"transcript"输出框中查看生成的对话文本
- 支持复制和保存文本
- 可以直接编辑和修改文本

### 5. 示例使用流程

```
1. 上传PDF文件：选择一篇学术论文
2. 输入问题："解释这篇论文的核心观点"
3. 选择语气：正式
4. 选择长度：中（3-5分钟）
5. 选择语言：中文
6. 选择大模型：百度文心一言
7. 选择TTS：百度语音合成
8. 点击生成播客
9. 等待生成完成
10. 播放播客并查看文本记录
```

### 6. 提示和技巧

- **内容选择**：选择清晰、结构化的PDF文件效果更好
- **问题设计**：具体、明确的问题会生成更准确的对话
- **语气匹配**：根据内容类型选择合适的语气
- **长度选择**：根据内容复杂度选择合适的长度
- **模型选择**：不同模型有不同的特点，建议尝试多种模型
- **TTS选择**：不同TTS服务有不同的音色和效果

### 7. 常见问题

#### 生成时间过长
- 尝试减少PDF页数或内容长度
- 选择较短的播客长度
- 关闭高级音频生成

#### 生成内容不符合预期
- 调整问题或主题描述
- 尝试不同的语气和长度
- 选择不同的大模型平台

#### 音频质量不佳
- 尝试不同的TTS服务
- 调整TTS参数
- 启用高级音频生成

#### 无法上传PDF
- 检查PDF文件大小和格式
- 确保PDF文件没有损坏
- 尝试转换PDF格式

### 8. 高级使用

#### 批量生成
- 支持上传多个PDF文件
- 系统会依次处理每个文件
- 适合批量生成播客内容

#### API调用
- 支持通过API接口调用
- 适合集成到其他系统
- 提供完整的API文档

#### 自定义配置
- 支持通过环境变量自定义配置
- 可以调整模型参数和TTS参数
- 适合高级用户定制化使用

## 项目结构

```
open-notebooklm/
├── .github/            # GitHub配置
│   └── workflows/      # CI/CD工作流
│       └── sync_with_hf.yml  # Hugging Face同步工作流
├── .trae/              # Trae AI配置
│   └── documents/      # 项目文档
├── examples/           # 示例文件
│   └── 1310.4546v1.pdf  # 示例PDF文件
├── examples_cached/    # 缓存示例
│   └── .gitkeep        # Git占位文件
├── .gitignore          # Git忽略配置
├── LICENSE             # 许可证文件
├── README.md           # 项目文档
├── app.py              # 主应用程序
├── constants.py        # 常量配置
├── prompts.py          # 提示词配置
├── requirements.txt    # 依赖列表
├── schema.py           # 数据模型
└── utils.py            # 工具函数
```

### 目录说明

- **.github/**：GitHub相关配置，包含CI/CD工作流
- **.trae/**：Trae AI相关配置和文档
- **examples/**：示例文件目录，包含示例PDF
- **examples_cached/**：缓存示例目录
- **根目录文件**：
  - `.gitignore`：Git忽略规则
  - `LICENSE`：项目许可证
  - `README.md`：项目说明文档
  - `app.py`：主应用程序入口
  - `constants.py`：常量和配置
  - `prompts.py`：提示词模板
  - `requirements.txt`：依赖列表
  - `schema.py`：数据模型定义
  - `utils.py`：工具函数集合

## 主要模块说明

### 1. app.py

**主应用程序入口**，负责：
- 使用Gradio创建Web界面
- 处理用户输入和请求
- 调用其他模块生成播客
- 管理Web界面的布局和交互
- 处理文件上传和URL解析

### 2. constants.py

**常量和配置管理**，包含：
- 大模型平台配置（百度文心一言、阿里通义千问、硅基流动）
- TTS服务配置（百度、阿里、讯飞语音合成）
- UI相关配置（输入输出标签、示例等）
- 重试机制配置
- 语言映射配置

### 3. prompts.py

**提示词模板管理**，包含：
- 系统提示词（定义AI角色和任务）
- 问题修饰符（添加用户问题）
- 语气修饰符（设置播客语气）
- 语言修饰符（指定输出语言）
- 长度修饰符（根据长度要求调整提示词）

### 4. schema.py

**数据模型定义**，使用Pydantic定义：
- `DialogueItem`：单个对话项模型
- `ShortDialogue`：短对话模型（11-17个对话项）
- `MediumDialogue`：中对话模型（19-29个对话项）

### 5. utils.py

**核心工具函数集合**，包含：
- **大模型调用**：
  - `generate_script`：生成播客脚本
  - `call_llm`：调用大模型API
  - `LLMClient`：大模型客户端抽象类
  - 支持多平台大模型调用

- **TTS语音合成**：
  - `generate_podcast_audio`：生成播客音频
  - `TTSClient`：TTS客户端抽象类
  - 支持多平台TTS调用

- **URL解析**：
  - `parse_url`：解析URL并提取文本内容

- **音频处理**：
  - 音频合成和拼接
  - 音频文件管理

### 6. requirements.txt

**项目依赖列表**，包含：
- 大模型SDK（erniebot等）
- TTS SDK（baidu-aip等）
- Web框架（gradio等）
- 核心库（pydantic、pypdf等）

### 7. examples/

**示例文件目录**，包含：
- 示例PDF文件
- 用于演示和测试的样本数据

### 8. 模块间关系

```
app.py
├── constants.py  # 配置管理
├── prompts.py    # 提示词模板
└── utils.py      # 工具函数
    ├── schema.py  # 数据模型
    └── constants.py  # 配置管理
```

## 扩展支持

Open NotebookLM 采用模块化设计，支持轻松添加新的大模型平台和TTS服务。

### 1. 添加新的大模型平台

#### 步骤

1. **添加配置**：在 `constants.py` 中添加新的大模型平台配置
2. **创建客户端类**：在 `utils.py` 中创建新的大模型客户端类，继承自 `LLMClient`
3. **注册客户端**：在 `LLMClientFactory` 中添加新的客户端创建逻辑

#### 示例：添加新的大模型平台

**步骤1：添加配置**

在 `constants.py` 中添加：

```python
# 新大模型平台配置
NEW_LLM_CONFIG = {
    "api_key": os.getenv("NEW_LLM_API_KEY"),
    "model_id": os.getenv("NEW_LLM_MODEL_ID", "new-llm-model"),
    "max_tokens": int(os.getenv("NEW_LLM_MAX_TOKENS", "16384")),
    "temperature": float(os.getenv("NEW_LLM_TEMPERATURE", "0.1")),
}

# 添加到大模型平台配置映射
LLM_PLATFORMS = {
    "ernie": ERNIE_CONFIG,
    "qianwen": QIANWEN_CONFIG,
    "siliconflow": SILICONFLOW_CONFIG,
    "new_llm": NEW_LLM_CONFIG,  # 添加新平台
}
```

**步骤2：创建客户端类**

在 `utils.py` 中添加：

```python
# 新大模型客户端
class NewLLMClient(LLMClient):
    """新大模型客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("请设置NEW_LLM_API_KEY环境变量")
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """生成对话"""
        # 实现新大模型的API调用逻辑
        # ...
        pass
```

**步骤3：注册客户端**

在 `LLMClientFactory` 中添加：

```python
@staticmethod
def create_client(platform: str, config: Dict[str, Any]) -> LLMClient:
    """创建大模型客户端"""
    if platform == "ernie":
        return ErnieClient(config)
    elif platform == "qianwen":
        return QianWenClient(config)
    elif platform == "siliconflow":
        return SiliconFlowClient(config)
    elif platform == "new_llm":  # 添加新平台支持
        return NewLLMClient(config)
    else:
        raise ValueError(f"不支持的大模型平台: {platform}")
```

### 2. 添加新的TTS服务

#### 步骤

1. **添加配置**：在 `constants.py` 中添加新的TTS服务配置
2. **创建客户端类**：在 `utils.py` 中创建新的TTS客户端类，继承自 `TTSClient`
3. **注册客户端**：在 `TTSClientFactory` 中添加新的客户端创建逻辑

#### 示例：添加新的TTS服务

**步骤1：添加配置**

在 `constants.py` 中添加：

```python
# 新TTS服务配置
NEW_TTS_CONFIG = {
    "api_key": os.getenv("NEW_TTS_API_KEY"),
    "secret_key": os.getenv("NEW_TTS_SECRET_KEY"),
    "voice": {
        "Host": "new_voice_1",
        "Guest": "new_voice_2"
    },
    "speed": int(os.getenv("NEW_TTS_SPEED", "5")),
    "pitch": int(os.getenv("NEW_TTS_PITCH", "5")),
    "volume": int(os.getenv("NEW_TTS_VOLUME", "5")),
    "retry_attempts": int(os.getenv("NEW_TTS_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("NEW_TTS_RETRY_DELAY", "5")),
}

# 添加到TTS服务配置映射
TTS_SERVICES = {
    "baidu": BAIDU_TTS_CONFIG,
    "ali": ALI_TTS_CONFIG,
    "xunfei": XUNFEI_TTS_CONFIG,
    "new_tts": NEW_TTS_CONFIG,  # 添加新服务
}
```

**步骤2：创建客户端类**

在 `utils.py` 中添加：

```python
# 新TTS客户端
class NewTTSClient(TTSClient):
    """新TTS客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")
        if not self.api_key or not self.secret_key:
            raise ValueError("请设置NEW_TTS_API_KEY和NEW_TTS_SECRET_KEY环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str) -> str:
        """合成语音"""
        # 实现新TTS服务的API调用逻辑
        # ...
        pass
```

**步骤3：注册客户端**

在 `TTSClientFactory` 中添加：

```python
@staticmethod
def create_client(service: str, config: Dict[str, Any]) -> TTSClient:
    """创建TTS客户端"""
    if service == "baidu":
        return BaiduTTSClient(config)
    elif service == "ali":
        return AliTTSClient(config)
    elif service == "xunfei":
        return XunfeiTTSClient(config)
    elif service == "new_tts":  # 添加新服务支持
        return NewTTSClient(config)
    else:
        raise ValueError(f"不支持的TTS服务: {service}")
```

### 3. 扩展注意事项

- **保持接口一致**：新客户端类必须实现父类的抽象方法
- **处理异常**：添加适当的异常处理和重试机制
- **测试充分**：确保新添加的模型或服务能正常工作
- **文档更新**：更新README和相关文档
- **遵循现有代码风格**：保持代码风格一致

### 4. 扩展场景

- 添加新的大模型平台
- 添加新的TTS服务
- 扩展现有模型的功能
- 添加新的内容输入类型
- 扩展音频处理功能

### 5. 贡献指南

欢迎提交Pull Request来扩展项目功能：

1. Fork项目
2. 创建特性分支
3. 实现扩展功能
4. 测试功能
5. 提交Pull Request

详细贡献指南请参考项目的CONTRIBUTING.md文件。

## 注意事项

### 1. 环境配置

- **环境变量**：请确保正确配置所有必要的环境变量，或使用 `.env` 文件管理
- **API密钥**：妥善保管API密钥，避免泄露
- **依赖版本**：确保依赖版本与 `requirements.txt` 一致，避免冲突

### 2. 服务使用

- **付费服务**：某些大模型和TTS服务可能需要付费使用，请确保有足够的配额
- **使用限制**：各服务可能有调用频率限制，注意控制请求频率
- **服务状态**：定期检查服务状态，避免使用不稳定的服务

### 3. 内容处理

- **内容长度**：过长的内容可能导致生成失败，建议分段处理
- **内容质量**：清晰、结构化的内容生成效果更好
- **版权问题**：确保您有权使用输入的内容，遵守版权法规

### 4. 性能优化

- **生成时间**：生成播客的时间取决于内容长度、复杂度和服务响应速度
- **资源占用**：大模型和TTS服务可能占用较多资源，建议在性能较好的设备上运行
- **并行处理**：避免同时处理过多请求，可能导致服务限流

### 5. 错误处理

- **网络问题**：确保网络连接稳定，避免在网络不稳定时使用
- **服务降级**：添加适当的错误处理和服务降级机制
- **日志记录**：保留必要的日志，便于排查问题

### 6. 合规性

- **使用条款**：遵守各大模型平台和TTS服务的使用条款和规定
- **数据隐私**：注意保护用户数据和隐私
- **内容审核**：生成的内容可能需要审核，确保符合相关规定

### 7. 其他

- **定期更新**：定期更新依赖和代码，获取最新功能和修复
- **备份数据**：定期备份生成的播客和配置
- **反馈问题**：遇到问题时，及时反馈并寻求帮助

### 8. 常见问题

#### 大模型调用失败
- 检查API密钥是否正确
- 检查网络连接
- 检查模型服务是否正常
- 尝试降低请求参数，如减少max_tokens

#### TTS合成失败
- 检查TTS服务配置
- 检查文本长度是否超过限制
- 尝试调整TTS参数
- 检查服务配额

#### Web界面无法访问
- 检查服务是否正在运行
- 检查端口是否被占用
- 检查防火墙设置
- 尝试重启服务

#### 生成内容不符合预期
- 调整提示词和参数
- 尝试更换模型平台
- 优化输入内容
- 调整语气和长度设置

#### 性能问题
- 减少输入内容长度
- 降低模型参数
- 关闭高级音频生成
- 尝试在性能更好的设备上运行

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献

### 1. 如何贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

#### 提交 Issue

- 提供清晰的问题描述
- 包含重现步骤
- 提供相关截图或日志
- 说明预期行为和实际行为

#### 提交 Pull Request

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "Add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 2. 贡献指南

- 遵循现有代码风格
- 添加必要的测试
- 更新文档
- 保持提交信息清晰
- 确保代码通过所有测试

### 3. 行为准则

- 尊重他人
- 欢迎新贡献者
- 提供建设性反馈
- 专注于项目目标

### 4. 联系方式

- **GitHub Issues**：用于报告问题和提出建议
- **GitHub Discussions**：用于讨论功能和设计
- **电子邮件**：如有需要，可通过项目主页联系维护者

## 致谢

感谢所有为项目做出贡献的开发者和用户！

## 版本历史

- **v1.0.0**：初始版本，支持基本功能
- **v1.1.0**：添加多模型支持
- **v1.2.0**：优化UI和用户体验
- **v2.0.0**：重构代码，支持更多扩展

## 未来计划

- 支持更多大模型平台
- 支持更多TTS服务
- 优化生成质量
- 添加更多内容输入类型
- 支持批量生成
- 优化性能和稳定性
