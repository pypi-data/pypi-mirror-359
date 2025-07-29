# Wiki Format Tool

一个的 Confluence 页面格式化和处理 CLI 工具，支持通过 LLM 自动优化文档排版和内容组织。

## 功能特性

- 🔄 **获取页面内容**：从 Confluence 页面 URL 获取内容并转换为 Markdown
- 📝 **智能格式化**：使用 LLM (OpenAI/Azure OpenAI) 自动优化页面排版和内容结构
- 📤 **内容上传**：将本地 Markdown 或文本文件上传到 Confluence 页面
- 🔍 **连接测试**：测试 Confluence API 连接和权限
- 🌐 **多平台支持**：支持 Confluence Cloud 和 Server/Data Center
- 🛡️ **安全认证**：支持多种身份验证方式

## 安装

### 通过 pip 安装（推荐）

```bash
pip install wiki-fmt
```

### 从源码安装

```bash
git clone <repository-url>
cd wiki_fmt
pip install -e .
```

## 配置

### 环境变量配置

工具需要配置以下环境变量来连接 Confluence 和 LLM 服务：

#### Confluence 配置

**对于 Confluence Cloud：**
```bash
export CONFLUENCE_BASE_URL="https://your-domain.atlassian.net"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

**对于 Confluence Server/Data Center：**
```bash
export CONFLUENCE_BASE_URL="https://your-confluence.example.com"
export CONFLUENCE_API_TOKEN="your-personal-access-token"
# 注意：Server/Data Center 不需要设置 CONFLUENCE_USERNAME
```

#### OpenAI 配置（任选其一）

**使用 OpenAI：**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL="gpt-4"  # 可选，默认为 gpt-3.5-turbo
export OPENAI_BASE_URL=

```

**使用 Azure OpenAI：**
```bash
export AZURE_OPENAI_API_KEY="your-azure-openai-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"  # 可选
export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment-name"
```

### 获取 API Token

#### Confluence Cloud API Token

1. 访问 [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. 点击 "Create API token"
3. 输入标签名称（如 "wiki-fmt"）
4. 复制生成的 token

#### Confluence Server/Data Center Personal Access Token

1. 登录到你的 Confluence 实例
2. 进入 Settings → Personal Access Tokens
3. 点击 "Create token"
4. 输入 token 名称并设置权限
5. 复制生成的 token

#### OpenAI API Key

1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 点击 "Create new secret key"
3. 复制生成的 API key

## 使用方法

### 基本命令

```bash
# 测试连接
wiki-fmt test

# 获取页面内容并转换为 Markdown
wiki-fmt get <page-url>

# 格式化页面（仅优化排版，不修改内容）
wiki-fmt format <page-url> [--dry-run]

# 重新组织页面内容和排版
wiki-fmt format <page-url> --reorganize [--dry-run]

# 上传本地文件到页面
wiki-fmt upload <file-path> <page-url> [--format markdown|text] [--dry-run]
```

### 详细使用示例

#### 1. 测试连接

```bash
wiki-fmt test
```

输出示例：
```
✅ Confluence API 连接成功
🔗 连接到: https://your-domain.atlassian.net
👤 认证方式: 用户名/API Token
📁 可访问的空间 (前3个):
   - PROJ → 项目文档
   - TEAM → 团队知识库
   - DEV → 开发文档
✅ 连接测试完成
```

#### 2. 获取页面内容

```bash
wiki-fmt get "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title"
```

这将：
- 获取页面的 HTML 内容
- 转换为 Markdown 格式
- 保存到本地文件 `Page_Title.md`

#### 3. 格式化页面（仅排版优化）

```bash
# 预览模式（不实际更新）
wiki-fmt format "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --dry-run

# 实际更新页面
wiki-fmt format "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title"
```

仅排版模式会：
- 保持原有内容完全不变
- 优化标题层级结构
- 改善段落和列表格式
- 添加适当的强调标记
- 优化代码块和表格格式

#### 4. 重新组织页面内容

```bash
# 预览模式
wiki-fmt format "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --reorganize --dry-run

# 实际更新
wiki-fmt format "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --reorganize
```

重新组织模式会：
- 分析内容逻辑，重新组织结构
- 优化文字表达，提高可读性
- 完善标题层级和段落结构
- 保持技术细节和关键信息准确性

#### 5. 上传本地文件

```bash
# 上传 Markdown 文件
wiki-fmt upload "./my-document.md" "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --format markdown

# 上传纯文本文件
wiki-fmt upload "./notes.txt" "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --format text

# 预览模式（不实际上传）
wiki-fmt upload "./my-document.md" "https://your-domain.atlassian.net/wiki/spaces/PROJ/pages/123456/Page+Title" --dry-run
```

### 命令行选项说明

#### 全局选项

- `--help`: 显示帮助信息
- `--version`: 显示版本信息

#### format 命令选项

- `--reorganize`: 启用内容重新组织模式（默认为仅排版模式）
- `--dry-run`: 预览模式，显示处理结果但不实际更新页面

#### upload 命令选项

- `--format {markdown,text}`: 指定文件格式（默认：markdown）
- `--dry-run`: 预览模式，显示上传内容但不实际更新页面

## 最佳实践

### 1. 使用建议

- **首次使用**：建议先运行 `wiki-fmt test` 确保连接正常
- **格式化操作**：首次使用时建议先用 `--dry-run` 参数预览效果
- **批量操作**：处理重要页面时建议先备份原始内容
- **权限检查**：确保使用的账户对目标页面有编辑权限

### 2. 安全注意事项

- **环境变量**：不要在代码或配置文件中硬编码 API Token
- **权限最小化**：使用具有最小必要权限的账户
- **测试环境**：建议先在测试环境中验证功能

### 3. 性能优化

- **Token 权限**：确保 API Token 有足够权限访问目标空间
- **网络连接**：确保网络连接稳定，特别是处理大页面时
- **LLM 配额**：注意 OpenAI API 的使用配额和限制

### 4. 故障排除

#### 常见错误

**连接失败：**
```
❌ Confluence API 连接失败: 401 Unauthorized
```
- 检查 `CONFLUENCE_BASE_URL` 是否正确
- 检查 API Token 是否有效
- 确认用户名和密码配置正确

**页面不存在：**
```
❌ 无法获取页面内容
```
- 确认页面 URL 正确
- 检查页面访问权限
- 确认页面未被删除

**LLM 服务错误：**
```
❌ LLM 格式化失败: Invalid API key
```
- 检查 OpenAI API Key 是否正确
- 确认 API Key 有足够配额
- 检查网络连接到 OpenAI 服务

#### 调试模式

设置环境变量启用详细日志：
```bash
export LOG_LEVEL=DEBUG
wiki-fmt test
```

## 开发

### 项目结构

```
wiki_fmt/
├── __init__.py
├── cli.py          # 命令行接口
└── formatter.py    # 核心功能实现
```

### 本地开发

```bash
# 克隆项目
git clone <repository-url>
cd wiki_fmt

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行测试
wiki-fmt test
```

## 版本历史

- **v1.0.0**: 初始版本
  - 支持页面内容获取和转换
  - 支持 LLM 格式化
  - 支持本地文件上传
  - 支持 Confluence Cloud 和 Server

## 许可证

[许可证信息]

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如果遇到问题或有功能建议，请：

1. 查看本文档的故障排除部分
2. 在项目仓库中提交 Issue
3. 联系项目维护者 