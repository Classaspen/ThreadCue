# Attention Inbox

Attention Inbox 是一个本地优先的 Gmail 邮件关注度 Dashboard。它不使用 AI，而是通过关键词、正则表达式和 thread 状态机判断：

- 是否在等待你回复或等待客户回复
- 是否存在报价、付款、客户、任务或合同相关内容
- 是否检测到明确的行动短语和截止日期
- 哪些 thread 更值得优先处理

应用不会自动发信、删除邮件或修改邮件内容。邮件分析和 SQLite 数据默认保存在本机。

## 1. 环境要求

建议使用 Python 3.10 或更高版本。Windows PowerShell 示例中的路径按项目目录 `D:\ThreadCue` 编写。

进入项目目录：

```powershell
cd D:\ThreadCue
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止激活脚本，可以直接使用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

正常情况下安装依赖：

```powershell
python -m pip install -r requirements.txt
```

## 2. 第一次运行 Demo

Demo 不需要 Gmail 账号或 OAuth 文件，会加载两封本地样例邮件：

```powershell
python -m app.main --demo
```

窗口左侧显示 thread 的优先级、分数和主题。点击一条 thread 后，右侧会显示：

- 当前状态，例如 `QUOTE_REQUIRED`、`ACTION_REQUIRED`
- Attention Score
- 每一项加分的解释原因

关闭窗口即可结束程序。Demo 不会连接网络，也不会读取真实邮箱。

## 3. 运行测试

```powershell
python -m pytest -q
```

当前测试覆盖：

- 报价请求识别
- `WAITING_ON_USER` / `WAITING_ON_CUSTOMER` 状态判断
- 明确日期截止时间识别
- Gmail 分页读取、发件方向识别和 HTML 邮件正文解析

如果系统中没有 `pytest` 命令，使用 `python -m pytest -q`，这样可以确保测试使用当前 Python 环境。

## 4. Gmail OAuth 准备

要使用 Gmail provider，需要先在 Google Cloud Console 创建 OAuth 客户端：

1. 创建或选择一个 Google Cloud project。
2. 启用 Gmail API。
3. 配置 OAuth consent screen。
4. 创建 OAuth Client ID，应用类型选择 **Desktop app**。
5. 下载客户端 JSON 文件。
6. 将文件保存到安全位置。点击应用中的 **Connect Gmail** 时，通过系统文件选择器选择它，不需要复制到项目目录。

OAuth client JSON 包含敏感配置，不应提交到 Git 或发送给他人。第一次授权时 Google 会打开浏览器，授权范围是 Gmail 只读：

```text
https://www.googleapis.com/auth/gmail.readonly
```

OAuth token 会保存到操作系统 keyring，而不是写入项目目录。删除本地授权时，可以在系统 keyring 中删除 `attention-inbox` 服务下的 `gmail-oauth` 项。

## 5. 当前 Gmail 功能边界

Gmail provider 的调用方式如下：

```python
from datetime import datetime, timedelta, timezone
from app.providers.gmail import GmailProvider

provider = GmailProvider("credentials.json")
provider.authenticate()
messages = provider.fetch_messages(
		datetime.now(timezone.utc) - timedelta(days=7)
)
```

返回的数据统一为 `EmailMessage`，之后可以交给分析服务：

```python
from app.services.analysis_service import AnalysisService

analyses = AnalysisService().analyze(messages)
```

当前 `app.main` 默认打开空 Dashboard；`--demo` 用于展示 UI 和分析效果。真实模式下可以直接点击顶部的 **Connect Gmail**，选择 OAuth client JSON 完成授权，再点击 **Sync now** 拉取邮件并刷新 Dashboard。

### 界面使用流程

1. 启动 `python -m app.main`。
2. 点击顶部 **Connect Gmail**，在文件选择器中选择 Google OAuth client JSON。
3. 在浏览器中完成 Google 授权。应用只申请 Gmail 只读权限。
4. 点击 **Settings**，选择行业和同步时间范围，然后点击 **Save**。
5. 点击 **Sync now**，等待邮件读取和规则分析完成。
6. 在左侧按优先级筛选 thread，点击邮件后在右侧查看状态、分数和具体原因。

应用使用 Gmail 官方 API 的 `users.messages.list`、`users.messages.get` 和 `users.getProfile` 接口。读取结果支持多页，不会因为 Gmail 返回下一页 token 而漏掉邮件；发件方向通过 Gmail 的 `SENT` 标签和已授权账号地址判断。

## 6. 行业 Profile

规则配置位于 `profiles/`：

- `profiles/contractor.yaml`：报价、估价、付款、发票
- `profiles/real_estate.yaml`：买家、看房、offer、合同、估价

示例：

```yaml
categories:
	NEW_ENQUIRY:
		keywords:
			- quote
			- estimate
			- pricing

followup:
	NEW_ENQUIRY_HOURS: 24
	QUOTE_SENT_DAYS: 3
```

加载 profile 并分析邮件：

```python
from app.analysis.classifier import load_rules
from app.services.analysis_service import AnalysisService

rules = load_rules("profiles/contractor.yaml")
analyses = AnalysisService(rules=rules).analyze(messages)
```

修改关键词通常不需要改 Python 代码。关键词匹配目前是不区分大小写的简单文本匹配，适合第一版的确定性规则，不等同于自然语言理解。

## 7. Attention Score 规则

当前评分会根据这些条件累加：

| 条件           | 分数 |
| -------------- | ---: |
| 新 lead        |  +30 |
| 等待你回复     |  +25 |
| 检测到报价请求 |  +25 |
| 报价后跟进到期 |  +20 |
| 检测到截止日期 |  +15 |
| 截止日期已过   |  +30 |
| 已有客户       |  +15 |
| 检测到行动短语 |  +15 |

优先级区间：

|      分数 | 优先级       |
| --------: | ------------ |
| 80 及以上 | `CRITICAL` |
|     60-79 | `HIGH`     |
|     30-59 | `MEDIUM`   |
|   低于 30 | `LOW`      |

每个分析结果都包含 `reasons`，例如 `+25 Quote request detected`，方便在 UI 中解释为什么一封邮件被提升优先级。

## 8. 本地数据库

默认数据库路径是：

```text
%USERPROFILE%\.attention-inbox\attention.db
```

数据库包含邮件记录和 thread 分析结果。程序会自动创建目录和表。测试或脚本中也可以指定路径：

```python
from app.db.database import create_database

engine = create_database("local-test.db")
```

真实邮箱数据属于敏感信息。不要把数据库文件、OAuth 文件或 token 提交到代码仓库。应用不会把邮件正文写入日志。

## 9. 打包 Windows EXE

安装依赖后执行：

```powershell
pyinstaller --name attention-inbox --windowed app/main.py
```

生成的文件通常位于 `dist\attention-inbox\`。首次使用 Gmail 时，在应用中选择 OAuth client JSON 并完成浏览器授权。

## 10. 目录说明

```text
app/
├── analysis/       关键词、行动、截止日期、评分规则
├── db/             SQLite 和 SQLAlchemy 数据访问
├── domain/         Email、Thread、Action 数据模型
├── providers/      Gmail provider；Outlook 预留
├── security/       OAuth 和 keyring
├── services/       同步、分析、排序、定时任务
└── ui/             PySide6 Dashboard、详情和设置
profiles/           行业规则 YAML
tests/              pytest 测试
```

## 隐私与安全

- 默认只读 Gmail，不自动发信。
- 不会自动删除或修改邮件。
- OAuth token 保存在系统 keyring。
- OAuth client JSON 由用户通过系统文件选择器提供，应用不会复制或上传它。
- Gmail API 使用只读 scope，不申请发送、删除或修改邮件的权限。
- 同步请求使用官方 Google API client，不自行实现 OAuth 或 Gmail 协议。
- 分析结果保存在本地 SQLite。
- OAuth client JSON 不会被应用复制到项目目录；虚拟环境、缓存和 smoke test 数据已加入 `.gitignore`。
