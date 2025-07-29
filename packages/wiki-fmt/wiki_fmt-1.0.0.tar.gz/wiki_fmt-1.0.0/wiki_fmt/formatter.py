#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confluence 文档格式化器核心模块
"""

import os
import re
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from atlassian import Confluence
from openai import OpenAI
import markdown
import html2text
import traceback


logger = logging.getLogger(__name__)


class FormatMode:
    """格式化模式枚举"""
    FORMAT_ONLY = "format_only"  # 只排版，不改动内容
    REORGANIZE = "reorganize"    # 重新组织内容文字并排版


class ConfluenceFormatter:
    """Confluence 文档格式化器"""
    
    def __init__(self):
        """初始化配置"""
        self.confluence_url = os.getenv('CONFLUENCE_BASE_URL')
        self.username = os.getenv('CONFLUENCE_USERNAME')
        self.api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.openai_model = os.getenv('OPENAI_MODEL', 'deepseek-v3')
        
        # 验证必需的配置
        if not all([self.confluence_url, self.username, self.api_token, self.openai_api_key]):
            missing = []
            if not self.confluence_url:
                missing.append('CONFLUENCE_BASE_URL')
            if not self.username:
                missing.append('CONFLUENCE_USERNAME')
            if not self.api_token:
                missing.append('CONFLUENCE_API_TOKEN')
            if not self.openai_api_key:
                missing.append('OPENAI_API_KEY')
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing)}")
        
        # 初始化 Confluence 客户端
        # 检测是否为 Confluence Server/Data Center（基于 URL 和认证方式）
        if '.atlassian.net' in self.confluence_url:
            # Atlassian Cloud
            self.confluence = Confluence(
                url=self.confluence_url,
                username=self.username,
                password=self.api_token,
                cloud=True
            )
            self.confluence_type = "Cloud"
        else:
            # Confluence Server/Data Center - 使用个人访问令牌
            self.confluence = Confluence(
                url=self.confluence_url,
                token=self.api_token,  # 使用 token 参数而不是 username/password
                cloud=False
            )
            self.confluence_type = "Server/Data Center"
        
        # 初始化 OpenAI 客户端，支持自定义 base_url
        self.openai_client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_base_url
        )
        
        if self.openai_base_url != 'https://api.openai.com/v1':
            logger.info(f"使用自定义 OpenAI Base URL: {self.openai_base_url}")
        
        logger.info("Confluence 格式化器初始化完成")
    
    def extract_page_id_from_url(self, page_url: str) -> Optional[str]:
        """
        从 Confluence URL 中提取页面 ID
        支持多种 URL 格式并使用 API 查询
        
        Args:
            page_url: 页面 URL
            
        Returns:
            页面 ID 或 None
        """
        try:
            logger.info(f"解析页面 URL: {page_url}")
            
            # 方法1: 从 /pages/pageId/ 格式提取
            pages_match = re.search(r'/pages/(\d+)/', page_url)
            if pages_match:
                page_id = pages_match.group(1)
                logger.info(f"从 /pages/ 格式提取到页面 ID: {page_id}")
                return page_id
            
            # 方法2: 从查询参数提取 pageId
            parsed_url = urlparse(page_url)
            query_params = parse_qs(parsed_url.query)
            if 'pageId' in query_params:
                page_id = query_params['pageId'][0]
                logger.info(f"从查询参数提取到页面 ID: {page_id}")
                return page_id
            
            # 方法3: 处理 /display/SPACE/PageTitle 格式
            display_match = re.search(r'/display/([^/]+)/([^/?#]+)', page_url)
            if display_match:
                space_key = display_match.group(1)
                page_title = display_match.group(2)
                # URL 解码页面标题
                page_title = page_title.replace('+', ' ')
                try:
                    from urllib.parse import unquote
                    page_title = unquote(page_title)
                except:
                    pass
                
                logger.info(f"从 /display/ 格式解析: space={space_key}, title={page_title}")
                
                # 通过 API 查询页面 ID
                try:
                    # 使用 Confluence API 查找页面
                    page_info = self.confluence.get_page_by_title(space_key, page_title)
                    if page_info:
                        page_id = str(page_info['id'])
                        logger.info(f"通过 API 查询到页面 ID: {page_id}")
                        return page_id
                    else:
                        logger.warning(f"API 查询未找到页面: space={space_key}, title={page_title}")
                        
                        # 尝试搜索页面
                        logger.info("尝试通过搜索查找页面...")
                        search_results = self.confluence.cql(f'space = "{space_key}" AND title ~ "{page_title}"')
                        if search_results and 'results' in search_results and search_results['results']:
                            page_id = str(search_results['results'][0]['content']['id'])
                            logger.info(f"通过搜索找到页面 ID: {page_id}")
                            return page_id
                        
                except Exception as api_error:
                    logger.error(f"API 查询页面失败: {str(api_error)}")
                    # 尝试更详细的错误信息
                    if "401" in str(api_error):
                        logger.error("认证失败 - 请检查 CONFLUENCE_USERNAME 和 CONFLUENCE_API_TOKEN")
                    elif "403" in str(api_error):
                        logger.error("权限不足 - 请检查用户是否有访问该空间的权限")
                    elif "404" in str(api_error):
                        logger.error("页面或空间不存在")
                    
                    return None
            
            # 方法4: 处理短链接格式 /wiki/x/...
            short_match = re.search(r'/wiki/x/([^/?#]+)', page_url)
            if short_match:
                logger.warning(f"检测到短链接格式，需要通过重定向获取真实 URL: {page_url}")
                try:
                    import requests
                    response = requests.get(page_url, allow_redirects=True, timeout=10)
                    if response.url != page_url:
                        logger.info(f"重定向到: {response.url}")
                        return self.extract_page_id_from_url(response.url)
                except Exception as e:
                    logger.error(f"处理短链接重定向失败: {str(e)}")
            
            logger.error(f"无法识别的 URL 格式: {page_url}")
            logger.error("支持的 URL 格式:")
            logger.error("1. https://domain.atlassian.net/wiki/spaces/SPACE/pages/123456/Page+Title")
            logger.error("2. https://domain.atlassian.net/wiki/display/SPACE/Page+Title")
            logger.error("3. https://domain.atlassian.net/wiki/display/SPACE/Page+Title?pageId=123456")
            
            return None
            
        except Exception as e:
            logger.error(f"解析页面 URL 时发生错误: {str(e)}")
            return None
    
    def get_page_content(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定页面的详细内容
        
        Args:
            page_id: 页面 ID
            
        Returns:
            页面内容字典或 None
        """
        try:
            logger.info(f"获取页面详细内容 (ID: {page_id})")
            
            # 获取页面内容
            page = self.confluence.get_page_by_id(
                page_id,
                expand='body.storage,version,space'
            )
            
            if not page:
                logger.error(f"页面不存在或无权访问 (ID: {page_id})")
                return None
            
            result = {
                'id': page['id'],
                'title': page['title'],
                'body': page['body']['storage']['value'],
                'version': page['version']['number'],
                'space_key': page['space']['key'],
                'space_name': page['space']['name']
            }
            
            logger.info(f"成功获取页面: {page['title']} (空间: {page['space']['key']})")
            return result
            
        except Exception as e:
            error_msg = f"获取页面内容失败 (ID: {page_id}): {str(e)}"
            logger.error(error_msg)
            
            # 为 401 错误提供详细的诊断信息
            if "401" in str(e) or "Unauthorized" in str(e):
                logger.error("🔑 认证失败详细诊断:")
                logger.error(f"   用户名: {self.username}")
                
                # 显示 API Token 的格式信息（不显示完整 Token）
                if self.api_token:
                    token_preview = self.api_token[:8] + "..." + self.api_token[-4:] if len(self.api_token) > 12 else "****"
                    logger.error(f"   API Token (预览): {token_preview}")
                    logger.error(f"   API Token 长度: {len(self.api_token)} 字符")
                    
                    # 检查 Token 格式
                    if len(self.api_token) < 20:
                        logger.error("   ⚠️  API Token 可能太短，请检查是否完整")
                    elif not self.api_token.replace('-', '').replace('_', '').isalnum():
                        logger.error("   ⚠️  API Token 包含异常字符，请检查复制是否正确")
                else:
                    logger.error("   ❌ API Token 为空")
                
                logger.error("   🔗 Confluence Base URL: " + self.confluence_url)
                logger.error("")
                logger.error("   💡 解决方案:")
                logger.error("   1. 检查 CONFLUENCE_USERNAME 是否为完整的邮箱地址")
                logger.error("   2. 检查 CONFLUENCE_API_TOKEN 是否为有效的 API Token")
                logger.error("   3. 重新生成 API Token: https://id.atlassian.com/manage-profile/security/api-tokens")
                logger.error("   4. 确认用户有访问该 Confluence 实例的权限")
                logger.error("   5. 检查 CONFLUENCE_BASE_URL 是否正确（应该是 https://your-domain.atlassian.net）")
            
            return None
    
    def html_to_markdown(self, html_content: str) -> str:
        """
        将 HTML 内容转换为 Markdown
        
        Args:
            html_content: HTML 内容
            
        Returns:
            Markdown 文本
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 简单的 HTML 到 Markdown 转换
            text = soup.get_text()
            
            # 基本清理
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
            return text
            
        except Exception as e:
            logger.error(f"HTML 转 Markdown 失败: {str(e)}")
            return ""
    
    def markdown_to_confluence_html(self, markdown_content: str) -> str:
        """
        将 Markdown 内容转换为 Confluence 兼容的 HTML
        
        Args:
            markdown_content: Markdown 内容
            
        Returns:
            Confluence HTML 内容
        """
        try:
            # 使用 markdown 库转换为 HTML
            html = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'nl2br']
            )
            
            # 进行 Confluence 特定的调整
            # 替换一些标准 HTML 标签为 Confluence 兼容的格式
            html = html.replace('<code>', '<code class="language-text">')
            
            return html
            
        except Exception as e:
            logger.error(f"Markdown 转 HTML 失败: {str(e)}")
            return markdown_content
    
    def format_with_llm(self, content: str, title: str, mode: str = FormatMode.FORMAT_ONLY) -> str:
        """
        使用 LLM 格式化内容
        
        Args:
            content: 原始内容（HTML 格式）
            title: 页面标题
            mode: 格式化模式
            
        Returns:
            格式化后的 HTML 内容
        """
        try:
            # 将 HTML 转换为 Markdown 以便 LLM 处理（使用高级转换方法）
            markdown_content = self.html_to_markdown_advanced(content)
            
            if mode == FormatMode.FORMAT_ONLY:
                prompt = f"""
你是一个专业的文档排版专家。请帮我优化以下 Confluence 页面的 Markdown 排版，但请严格保持原有内容不变。

页面标题: {title}

原始 Markdown 内容:
{markdown_content}

请按照以下要求进行排版优化（仅排版，不要修改内容）:

1. **严格保持内容完整性**：不要删除、添加或修改任何原有信息和文字内容
2. 优化标题层级结构，使用合适的 # ## ### #### 标记
3. 改善段落结构和换行，确保逻辑清晰
4. 对重要信息使用合适的强调标记（**粗体**、*斜体*等）
5. 如果有列表内容，使用规范的 - 或 1. 标记
6. 如果有表格数据，优化表格的 Markdown 格式
7. 添加适当的段落间距
8. 保持代码块的格式不变

请直接返回优化排版后的 Markdown 内容，不要包含任何解释文字。
"""
            elif mode == FormatMode.REORGANIZE:
                prompt = f"""
你是一个专业的文档编辑专家。请帮我重新组织并优化以下 Confluence 页面的内容结构和排版。

页面标题: {title}

原始 Markdown 内容:
{markdown_content}

请按照以下要求进行内容重组和排版优化:

1. 分析内容逻辑，重新组织段落和章节结构
2. 优化文字表达，使其更加清晰易懂（可以适当调整措辞）
3. 完善标题层级结构，使用合适的 # ## ### #### 标记
4. 对重要信息使用合适的强调标记（**粗体**、*斜体*等）
5. 规范化列表和表格格式
6. 添加适当的段落间距和分隔
7. 保持技术细节和关键信息的准确性
8. 如果内容过于冗长，可以适当精简，但不要删除重要信息

请直接返回重新组织后的 Markdown 内容，不要包含任何解释文字。
"""
            else:
                raise ValueError(f"不支持的格式化模式: {mode}")

            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的文档编辑和排版专家，擅长优化 Markdown 文档的格式和结构。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            formatted_markdown = response.choices[0].message.content.strip()
            
            # 清理 LLM 响应中可能包含的代码块标记
            if formatted_markdown.startswith('```'):
                # 去除开头的代码块标记
                lines = formatted_markdown.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]  # 移除第一行的 ```标记
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]  # 移除最后一行的 ```标记
                formatted_markdown = '\n'.join(lines)
            
            # 将 Markdown 转换回 Confluence HTML
            formatted_html = self.markdown_to_confluence_html(formatted_markdown)
            
            logger.info(f"LLM 格式化完成，页面: {title}，模式: {mode}")
            logger.debug(f"原始内容长度: {len(content)} 字符")
            logger.debug(f"Markdown 长度: {len(markdown_content)} 字符") 
            logger.debug(f"格式化后 HTML 长度: {len(formatted_html)} 字符")
            
            return formatted_html
            
        except Exception as e:
            logger.error(f"LLM 格式化失败: {str(e)}")
            return content  # 返回原始内容
    
    def update_page_content(self, page_id, title, new_content, current_version):
        """
        更新页面内容
        """
        logger.info(f"Updating page \"{title}\"")
        logger.info(f"参数详情: page_id={page_id}, current_version={current_version}, content_length={len(new_content)}")
        logger.info(f"内容预览: {new_content[:300]}...")
        
        # 验证和修复HTML内容
        validation_result = self._validate_html_content(new_content)
        if not validation_result['valid']:
            logger.error(f"HTML内容格式错误: {validation_result['error']}")
            logger.error(f"错误的HTML片段: {validation_result['error_fragment']}")
            # 尝试自动修复
            original_content = new_content
            new_content = self._fix_html_content(new_content)
            if new_content != original_content:
                logger.info("已自动修复HTML格式错误")
                logger.info(f"修复后内容预览: {new_content[:300]}...")
            else:
                logger.warning("无法修复HTML格式错误")
        
        try:
            # 获取页面完整信息，确保有space信息
            page_info = self.get_page_content(page_id)
            if not page_info:
                logger.error(f"无法获取页面信息 (ID: {page_id})")
                return False
            
            logger.info(f"页面信息: space_key={page_info.get('space_key')}, space_name={page_info.get('space_name')}")
            
            # 调用atlassian-python-api更新页面
            logger.info("开始调用 confluence.update_page...")
            result = self.confluence.update_page(
                page_id=page_id,
                title=title,
                body=new_content,
                parent_id=None,
                type='page',
                representation='storage',
                minor_edit=False,
                version_comment=f"Updated by wiki_fmt - version {current_version + 1}"
            )
            
            logger.info(f"API调用结果: {type(result)}")
            logger.info(f"页面更新成功: {title}")
            return True
            
        except Exception as e:
            logger.error(f"页面更新失败: {title}, 错误: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"完整错误堆栈: {traceback.format_exc()}")
            return False
    
    def _validate_html_content(self, html_content: str) -> dict:
        """验证HTML内容格式"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            # 检查常见的HTML错误
            errors = []
            
            # 检查XML指令和特殊字符
            if '<![' in html_content and not html_content.startswith('<![CDATA['):
                # 查找问题字符位置
                for i, char in enumerate(html_content):
                    if i < len(html_content) - 2 and html_content[i:i+3] == '<![':
                        errors.append(f"在位置{i}发现未识别的XML指令: {html_content[max(0,i-10):i+20]}")
            
            # 检查是否有未转义的特殊字符
            problematic_chars = ['<![', '<!DOCTYPE', '<?xml']
            for char_seq in problematic_chars:
                if char_seq in html_content:
                    pos = html_content.find(char_seq)
                    errors.append(f"在位置{pos}发现问题字符序列: {char_seq}")
            
            # 检查自闭合的img标签
            img_tags = re.findall(r'<img[^>]*>', html_content)
            for img_tag in img_tags:
                if not (img_tag.endswith('/>') or img_tag.endswith('/>')):
                    # 检查是否有对应的闭合标签
                    if '</img>' not in html_content:
                        errors.append(f"img标签需要自闭合或有闭合标签: {img_tag}")
            
            # 使用BeautifulSoup验证整体结构
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                # 如果能成功解析，检查是否有未闭合的标签
            except Exception as soup_error:
                errors.append(f"HTML解析错误: {str(soup_error)}")
            
            if errors:
                return {
                    'valid': False,
                    'error': '; '.join(errors),
                    'error_fragment': html_content[:200] + '...' if len(html_content) > 200 else html_content
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"验证过程出错: {str(e)}",
                'error_fragment': ''
            }
    
    def _fix_html_content(self, html_content: str) -> str:
        """尝试修复HTML内容格式错误"""
        try:
            import re
            
            # 修复常见的HTML问题
            fixed_content = html_content
            
            # 移除XML指令和DOCTYPE声明
            fixed_content = re.sub(r'<\?xml[^>]*\?>', '', fixed_content)
            fixed_content = re.sub(r'<!DOCTYPE[^>]*>', '', fixed_content)
            fixed_content = re.sub(r'<![^>]*>', '', fixed_content)
            
            # 修复img标签 - 自闭合或添加闭合标签
            def fix_img_tag(match):
                tag = match.group(0)
                if tag.endswith('/>'):
                    return tag  # 已经是自闭合
                elif tag.endswith('>'):
                    return tag[:-1] + ' />'  # 添加自闭合
                return tag
            
            fixed_content = re.sub(r'<img[^>]*>', fix_img_tag, fixed_content)
            
            # 使用BeautifulSoup进行进一步清理
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(fixed_content, 'html.parser')
            
            # 重新生成HTML，这会自动修复一些格式问题
            fixed_content = str(soup)
            
            # 移除可能添加的html和body标签（BeautifulSoup有时会添加）
            fixed_content = re.sub(r'</?html[^>]*>', '', fixed_content)
            fixed_content = re.sub(r'</?body[^>]*>', '', fixed_content)
            fixed_content = fixed_content.strip()
            
            return fixed_content
            
        except Exception as e:
            logger.error(f"修复HTML失败: {str(e)}")
            return html_content  # 返回原内容而不是None
    
    def process_page_by_url(self, page_url, reorganize_level=1, dry_run=False):
        """
        根据页面URL处理并格式化页面内容
        
        Args:
            page_url: 页面URL
            reorganize_level: 重组等级 (0-3)
                0: 仅修正格式，不改变内容结构
                1: 修正格式和标题层级（默认）
                2: 中等重组：调整段落顺序和内容结构
                3: 深度重组：完全重新组织内容
            dry_run: 是否为演练模式
        """
        result = {
            'success': False,
            'page_id': None,
            'title': None,
            'error': None,
            'formatted': False,
            'dry_run': dry_run
        }
        
        try:
            logger.info(f"开始处理页面: {page_url}")
            
            # 提取页面ID
            page_id = self.extract_page_id_from_url(page_url)
            if not page_id:
                result['error'] = "无法从URL提取页面ID"
                return result
            
            result['page_id'] = page_id
            
            # 获取页面内容
            content_result = self.get_page_content_by_url(page_url)
            if not content_result['success']:
                result['error'] = content_result['error']
                return result
            
            result['title'] = content_result['title']
            original_content = content_result['content']
            
            # 使用LLM格式化内容（直接处理HTML）
            formatted_content = self.format_with_llm_direct(
                original_content, 
                reorganize_level=reorganize_level
            )
            
            if not formatted_content:
                result['error'] = "LLM格式化失败"
                return result
            
            # 检查内容是否有变化
            if self._content_unchanged(original_content, formatted_content):
                logger.info("内容无变化，跳过更新")
                result['success'] = True
                result['formatted'] = False
                return result
            
            result['formatted'] = True
            
            if dry_run:
                logger.info("演练模式：跳过实际更新")
                result['success'] = True
                return result
            
            # 更新页面
            try:
                # 获取页面详细信息用于更新
                page_info = self.get_page_content(page_id)
                if not page_info:
                    result['error'] = "无法获取页面信息用于更新"
                    return result
                
                success = self.update_page_content(
                    page_id=page_id,
                    title=result['title'],
                    new_content=formatted_content,
                    current_version=page_info['version']
                )
                
                if success:
                    logger.info(f"页面 {page_id} 更新成功")
                    result['success'] = True
                else:
                    result['error'] = "页面更新失败"
                
            except Exception as e:
                logger.error(f"更新页面失败: {str(e)}")
                result['error'] = f"更新页面失败: {str(e)}"
                
        except Exception as e:
            logger.error(f"处理页面失败: {str(e)}")
            result['error'] = str(e)
        
        return result

    def format_with_llm_direct(self, html_content, reorganize_level=1):
        """
        直接使用LLM格式化HTML内容，不进行markdown转换
        
        Args:
            html_content: 原始HTML内容
            reorganize_level: 重组等级
        """
        try:
            # 根据重组等级定义不同的提示词
            reorganize_prompts = {
                0: """请对以下HTML内容进行格式化，只修正明显的格式问题，不要改变内容结构和文字：
- 修正缩进和空行
- 统一标签格式
- 保持原有的标题层级和内容顺序
- 不要修改任何文字内容

请直接输出HTML内容，不要包含```html```等代码块标记。""",
                
                1: """请对以下HTML内容进行格式化和轻度优化：
- 修正格式问题（缩进、空行、标签格式）
- 调整标题层级使其更合理
- 修正明显的标点符号错误
- 保持主要内容结构不变

请直接输出HTML内容，不要包含```html```等代码块标记。""",
                
                2: """请对以下HTML内容进行中等程度的重组和优化：
- 调整段落顺序使逻辑更清晰
- 重新组织内容结构
- 优化标题和子标题
- 改进表达方式但保持原意

请直接输出HTML内容，不要包含```html```等代码块标记。""",
                
                3: """请对以下HTML内容进行深度重组和创意优化：
- 完全重新组织内容结构
- 优化内容逻辑和表达
- 适当增加或调整格式元素
- 创造性地改进整体呈现效果
- 保持内容的核心主题和信息

请直接输出HTML内容，不要包含```html```等代码块标记。"""
            }

            # 获取对应等级的提示词
            system_prompt = reorganize_prompts.get(reorganize_level, reorganize_prompts[1])
            
            # 调用OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"HTML内容:\n{html_content}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            formatted_content = response.choices[0].message.content.strip()
            
            # 处理LLM可能输出的代码块标记
            formatted_content = self._clean_llm_output(formatted_content)
            
            logger.info(f"LLM格式化完成，重组等级: {reorganize_level}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"LLM格式化失败: {str(e)}")
            return None

    def _clean_llm_output(self, content):
        """清理LLM输出中的代码块标记和其他格式标记"""
        import re
        
        # 移除代码块标记
        content = re.sub(r'^```html\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\s*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n```\s*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```$', '', content, flags=re.MULTILINE)
        
        # 移除开头和结尾的多余空白
        content = content.strip()
        
        return content

    def _content_unchanged(self, original_content, formatted_content):
        """检查内容是否有实质性变化"""
        try:
            # 简单的内容比较，去掉空白字符差异
            original_cleaned = re.sub(r'\s+', ' ', original_content.strip())
            formatted_cleaned = re.sub(r'\s+', ' ', formatted_content.strip())
            
            # 如果长度差异太大，认为有变化
            length_diff = abs(len(original_cleaned) - len(formatted_cleaned))
            if length_diff > len(original_cleaned) * 0.1:  # 10%的差异阈值
                return False
            
            # 简单的相似度检查
            return original_cleaned == formatted_cleaned
            
        except Exception as e:
            logger.error(f"内容比较失败: {str(e)}")
            return False

    def execute_llm_instruction(self, page_url, dry_run=False):
        """
        根据页面内容中的指令执行LLM任务
        
        Args:
            page_url: 页面URL
            dry_run: 是否为演练模式
        """
        result = {
            'success': False,
            'page_id': None,
            'title': None,
            'error': None,
            'dry_run': dry_run
        }
        
        try:
            logger.info(f"执行LLM指令任务: {page_url}")
            
            # 提取页面ID
            page_id = self.extract_page_id_from_url(page_url)
            if not page_id:
                result['error'] = "无法从URL提取页面ID"
                return result
            
            result['page_id'] = page_id
            
            # 获取页面内容
            content_result = self.get_page_content_by_url(page_url)
            if not content_result['success']:
                result['error'] = content_result['error']
                return result
            
            result['title'] = content_result['title']
            original_content = content_result['content']
            
            # 从内容中提取LLM指令
            instruction = self._extract_llm_instruction(original_content)
            if not instruction:
                result['error'] = "页面中未找到LLM指令"
                return result
            
            # 执行LLM指令
            processed_content = self._execute_llm_with_instruction(original_content, instruction)
            if not processed_content:
                result['error'] = "LLM指令执行失败"
                return result
            
            if dry_run:
                logger.info("演练模式：跳过实际更新")
                result['success'] = True
                return result
            
            # 更新页面
            try:
                # 获取页面详细信息用于更新
                page_info = self.get_page_content(page_id)
                if not page_info:
                    result['error'] = "无法获取页面信息用于更新"
                    return result
                
                success = self.update_page_content(
                    page_id=page_id,
                    title=result['title'],
                    new_content=processed_content,
                    current_version=page_info['version']
                )
                
                if success:
                    logger.info(f"页面 {page_id} LLM任务执行完成")
                    result['success'] = True
                else:
                    result['error'] = "页面更新失败"
                
            except Exception as e:
                logger.error(f"更新页面失败: {str(e)}")
                result['error'] = f"更新页面失败: {str(e)}"
                
        except Exception as e:
            logger.error(f"LLM任务执行失败: {str(e)}")
            result['error'] = str(e)
        
        return result

    def _extract_llm_instruction(self, html_content):
        """从HTML内容中提取LLM指令"""
        try:
            # 查找包含指令的模式，例如：
            # <!-- LLM: 指令内容 -->
            # <p>LLM: 指令内容</p>
            # 等等
            
            import re
            
            # 尝试从HTML注释中提取
            comment_pattern = r'<!--\s*LLM\s*:\s*(.*?)\s*-->'
            comment_match = re.search(comment_pattern, html_content, re.IGNORECASE | re.DOTALL)
            if comment_match:
                return comment_match.group(1).strip()
            
            # 尝试从段落标签中提取
            paragraph_pattern = r'<p[^>]*>\s*LLM\s*:\s*(.*?)\s*</p>'
            paragraph_match = re.search(paragraph_pattern, html_content, re.IGNORECASE | re.DOTALL)
            if paragraph_match:
                return paragraph_match.group(1).strip()
            
            # 尝试从任何文本中提取（去掉HTML标签）
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            
            text_pattern = r'LLM\s*:\s*(.*?)(?:\n|$)'
            text_match = re.search(text_pattern, text_content, re.IGNORECASE)
            if text_match:
                return text_match.group(1).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"提取LLM指令失败: {str(e)}")
            return None

    def _execute_llm_with_instruction(self, html_content, instruction):
        """根据指令执行LLM任务"""
        try:
            system_prompt = f"""你是一个智能文档处理助手。请根据用户的指令对提供的HTML内容进行处理。

用户指令：{instruction}

重要要求：
1. 严格按照用户指令执行任务
2. 输出必须是有效的HTML格式
3. 保持重要信息不丢失
4. 确保HTML标签正确闭合
5. 不要添加多余的HTML结构标签
6. 直接返回处理后的内容，无需任何解释"""
            
            user_prompt = f"请按照指令处理以下HTML内容：\n\n{html_content}"
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                max_tokens=8000,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            processed_content = response.choices[0].message.content.strip()
            logger.info("LLM指令执行完成")
            return processed_content
            
        except Exception as e:
            logger.error(f"LLM指令执行失败: {str(e)}")
            return None
    
    def get_page_content_by_url(self, page_url: str) -> Dict[str, Any]:
        """
        通过 URL 获取页面内容（HTML格式）
        
        Args:
            page_url: 页面 URL
            
        Returns:
            包含页面内容的结果字典
        """
        result = {
            'success': False,
            'page_id': None,
            'title': None,
            'content': None,
            'error': None,
            'url': page_url,
            'debug_info': {}
        }
        
        try:
            logger.info(f"获取页面内容: {page_url}")
            
            # 记录调试信息
            result['debug_info']['confluence_url'] = self.confluence_url
            result['debug_info']['username'] = self.username
            
            # 从 URL 提取页面 ID
            page_id = self.extract_page_id_from_url(page_url)
            if not page_id:
                # 更详细的错误信息
                error_msg = "无法从 URL 提取页面 ID"
                
                # 分析 URL 格式给出建议
                if '/display/' in page_url:
                    # 尝试解析 display 格式
                    display_match = re.search(r'/display/([^/]+)/([^/?#]+)', page_url)
                    if display_match:
                        space_key = display_match.group(1)
                        page_title = display_match.group(2).replace('+', ' ')
                        try:
                            from urllib.parse import unquote
                            page_title = unquote(page_title)
                        except:
                            pass
                        
                        result['debug_info']['detected_space'] = space_key
                        result['debug_info']['detected_title'] = page_title
                        
                        error_msg += f"\n检测到空间: {space_key}, 页面标题: {page_title}"
                        error_msg += f"\n这可能是因为:"
                        error_msg += f"\n1. API 认证问题 - 请检查 CONFLUENCE_USERNAME 和 CONFLUENCE_API_TOKEN"
                        error_msg += f"\n2. 权限问题 - 用户可能没有访问空间 '{space_key}' 的权限"
                        error_msg += f"\n3. 页面不存在 - 页面标题 '{page_title}' 可能不正确"
                        error_msg += f"\n4. 空间不存在 - 空间键 '{space_key}' 可能不正确"
                        
                        # 尝试测试连接
                        try:
                            # 测试 API 连接
                            logger.info("测试 Confluence API 连接...")
                            test_result = self.confluence.get_spaces()
                            if test_result:
                                logger.info(f"API 连接正常，可访问 {len(test_result)} 个空间")
                                result['debug_info']['api_connection'] = "成功"
                                result['debug_info']['accessible_spaces'] = len(test_result)
                                
                                # 检查目标空间是否存在
                                space_keys = [space['key'] for space in test_result]
                                if space_key in space_keys:
                                    result['debug_info']['target_space_exists'] = True
                                    error_msg += f"\n✅ 目标空间 '{space_key}' 存在且可访问"
                                    
                                    # 尝试列出空间中的页面
                                    try:
                                        pages = self.confluence.get_all_pages_from_space(space_key, limit=10)
                                        if pages:
                                            result['debug_info']['space_pages_count'] = len(pages)
                                            error_msg += f"\n✅ 空间中有 {len(pages)} 个页面可访问"
                                            
                                            # 寻找相似的页面标题
                                            similar_titles = []
                                            for page in pages:
                                                if page_title.lower() in page['title'].lower() or page['title'].lower() in page_title.lower():
                                                    similar_titles.append(page['title'])
                                            
                                            if similar_titles:
                                                error_msg += f"\n💡 找到相似的页面标题: {', '.join(similar_titles[:3])}"
                                        else:
                                            error_msg += f"\n❌ 空间中没有可访问的页面"
                                    except Exception as e:
                                        error_msg += f"\n❌ 无法列出空间中的页面: {str(e)}"
                                else:
                                    result['debug_info']['target_space_exists'] = False
                                    error_msg += f"\n❌ 目标空间 '{space_key}' 不存在或不可访问"
                                    error_msg += f"\n💡 可访问的空间: {', '.join(space_keys[:5])}"
                            else:
                                result['debug_info']['api_connection'] = "无法获取空间列表"
                                error_msg += f"\n❌ API 连接异常：无法获取空间列表"
                        except Exception as api_test_error:
                            result['debug_info']['api_connection'] = f"失败: {str(api_test_error)}"
                            error_msg += f"\n❌ API 连接测试失败: {str(api_test_error)}"
                            
                            if "401" in str(api_test_error):
                                error_msg += f"\n🔑 认证失败，请检查:"
                                error_msg += f"\n   - CONFLUENCE_USERNAME 是否正确"
                                error_msg += f"\n   - CONFLUENCE_API_TOKEN 是否有效"
                            elif "403" in str(api_test_error):
                                error_msg += f"\n🚫 权限不足，用户可能没有足够的权限"
                            elif "404" in str(api_test_error):
                                error_msg += f"\n🔗 连接失败，请检查 CONFLUENCE_BASE_URL 是否正确"
                
                result['error'] = error_msg
                return result
            
            result['page_id'] = page_id
            logger.info(f"提取到页面 ID: {page_id}")
            
            # 获取页面详细内容
            page_content = self.get_page_content(page_id)
            if not page_content:
                result['error'] = "无法获取页面内容"
                return result
            
            result['title'] = page_content['title']
            result['content'] = page_content['body']
            result['success'] = True
            
            logger.info(f"成功获取页面内容: {page_content['title']}")
            
        except Exception as e:
            error_msg = f"获取页面内容时发生错误: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
            result['debug_info']['exception'] = str(e)
        
        return result
    
    def convert_page_to_markdown(self, page_url: str) -> Dict[str, Any]:
        """
        获取页面内容并转换为 Markdown 格式
        
        Args:
            page_url: 页面 URL
            
        Returns:
            包含 Markdown 内容的结果字典
        """
        result = {
            'success': False,
            'page_id': None,
            'title': None,
            'markdown': None,
            'error': None,
            'url': page_url
        }
        
        try:
            logger.info(f"获取页面并转换为 Markdown: {page_url}")
            
            # 首先获取页面内容
            page_result = self.get_page_content_by_url(page_url)
            if not page_result['success']:
                result['error'] = page_result['error']
                return result
            
            result['page_id'] = page_result['page_id']
            result['title'] = page_result['title']
            
            # 转换 HTML 为 Markdown
            html_content = page_result['content']
            markdown_content = self.html_to_markdown_advanced(html_content)
            
            result['markdown'] = markdown_content
            result['success'] = True
            
            logger.info(f"成功转换页面为 Markdown: {page_result['title']}")
            
        except Exception as e:
            error_msg = f"转换页面为 Markdown 时发生错误: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
        
        return result
    
    def html_to_markdown_advanced(self, html_content: str) -> str:
        """
        将 HTML 内容转换为高质量的 Markdown
        
        Args:
            html_content: HTML 内容
            
        Returns:
            Markdown 文本
        """
        try:
            # 使用 html2text 库进行转换
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_tables = False
            h.body_width = 0  # 不限制行宽
            h.unicode_snob = True
            h.skip_internal_links = True
            
            markdown_content = h.handle(html_content)
            
            # 清理多余的空行
            lines = markdown_content.split('\n')
            cleaned_lines = []
            empty_line_count = 0
            
            for line in lines:
                if line.strip() == '':
                    empty_line_count += 1
                    if empty_line_count <= 2:  # 最多保留2个连续空行
                        cleaned_lines.append(line)
                else:
                    empty_line_count = 0
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            logger.error(f"HTML 转 Markdown 失败: {str(e)}")
            # 回退到简单方法
            return self.html_to_markdown(html_content)
    
    def upload_file_to_page(self, file_path: str, page_url: str, 
                           file_format: str = 'markdown', dry_run: bool = False) -> Dict[str, Any]:
        """
        上传本地文件内容到 Confluence 页面
        
        Args:
            file_path: 本地文件路径
            page_url: 目标页面 URL
            file_format: 文件格式 ('markdown', 'html', 'text')
            dry_run: 是否为演练模式
            
        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'page_id': None,
            'title': None,
            'error': None,
            'url': page_url,
            'file_path': file_path,
            'file_format': file_format,
            'dry_run': dry_run
        }
        
        try:
            logger.info(f"上传文件到页面: {file_path} -> {page_url}")
            logger.info(f"文件格式: {file_format}")
            logger.info(f"演练模式: {dry_run}")
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                result['error'] = f"文件不存在: {file_path}"
                return result
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            if not file_content.strip():
                result['error'] = "文件内容为空"
                return result
            
            # 从 URL 提取页面 ID
            page_id = self.extract_page_id_from_url(page_url)
            if not page_id:
                result['error'] = "无法从 URL 提取页面 ID"
                return result
            
            result['page_id'] = page_id
            logger.info(f"提取到页面 ID: {page_id}")
            
            # 获取目标页面信息
            page_content = self.get_page_content(page_id)
            if not page_content:
                result['error'] = "无法获取目标页面信息"
                return result
            
            result['title'] = page_content['title']
            logger.info(f"目标页面: {page_content['title']}")
            
            # 根据文件格式转换内容
            if file_format == 'markdown':
                # Markdown 转 HTML
                html_content = self.markdown_to_confluence_html(file_content)
            elif file_format == 'html':
                # 直接使用 HTML
                html_content = file_content
            elif file_format == 'text':
                # 纯文本转 HTML
                html_content = self.text_to_html(file_content)
            else:
                result['error'] = f"不支持的文件格式: {file_format}"
                return result
            
            # 如果是演练模式，只显示将要进行的操作
            if dry_run:
                logger.info(f"[演练模式] 将要更新页面: {page_content['title']}")
                logger.info(f"[演练模式] 文件内容长度: {len(file_content)} 字符")
                logger.info(f"[演练模式] 转换后内容长度: {len(html_content)} 字符")
                result['success'] = True
                return result
            
            # 更新页面
            logger.info("开始更新页面...")
            success = self.update_page_content(
                page_id=page_id,
                title=result['title'],
                new_content=html_content,
                current_version=page_content['version']
            )
            
            if success:
                logger.info(f"文件上传完成: {page_content['title']}")
                result['success'] = True
            else:
                result['error'] = "页面更新失败"
                
        except Exception as e:
            error_msg = f"上传文件时发生错误: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
        
        return result
    
    def text_to_html(self, text_content: str) -> str:
        """
        将纯文本转换为 HTML
        
        Args:
            text_content: 纯文本内容
            
        Returns:
            HTML 内容
        """
        try:
            # 简单的文本到 HTML 转换
            lines = text_content.split('\n')
            html_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # 转义 HTML 特殊字符
                    escaped_line = (line.replace('&', '&amp;')
                                   .replace('<', '&lt;')
                                   .replace('>', '&gt;')
                                   .replace('"', '&quot;')
                                   .replace("'", '&#x27;'))
                    html_lines.append(f'<p>{escaped_line}</p>')
                else:
                    html_lines.append('<br/>')
            
            return '\n'.join(html_lines)
            
        except Exception as e:
            logger.error(f"文本转 HTML 失败: {str(e)}")
            return f"<p>{text_content}</p>" 