#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wiki-fmt 命令行接口
"""

import sys
import logging
import argparse
from pathlib import Path

from .formatter import ConfluenceFormatter, FormatMode


def setup_logging(debug: bool = False):
    """设置日志配置"""
    level = logging.DEBUG if debug else logging.INFO
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 文件输出
    log_file = Path.cwd() / "wiki-fmt.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog='wiki-fmt',
        description='Confluence 文档处理工具 - 支持获取、格式化和智能处理功能',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 获取页面内容为HTML
  wiki-fmt get https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  
  # 获取页面内容并转换为Markdown
  wiki-fmt get markdown https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  wiki-fmt get md https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  
  # 格式化页面（仅排版优化，不修改内容）
  wiki-fmt format https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  
  # 格式化页面（不同重组织级别）
  wiki-fmt format --reorganize 1 https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  wiki-fmt format --reorganize 2 https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  wiki-fmt format --reorganize 3 https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  
  # 根据页面指令执行LLM任务
  wiki-fmt llm https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title
  
  # 上传本地文件到页面
  wiki-fmt upload content.md https://your-domain.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title

重组织级别说明:
  0 - 仅排版优化，不修改任何内容，只增加格式（默认）
  1 - 在0的基础上，修改错别字和语法错误
  2 - 在1的基础上，重新组织内容结构和逻辑
  3 - 在2的基础上，在原意范围内进行创意优化

环境变量配置:
  CONFLUENCE_BASE_URL     - Confluence 基础 URL (必需)
  CONFLUENCE_USERNAME     - Confluence 用户名 (Cloud版必需) 
  CONFLUENCE_API_TOKEN    - Confluence API Token (必需)
  OPENAI_API_KEY          - OpenAI API Key (必需)
  AZURE_OPENAI_API_KEY    - Azure OpenAI API Key (可选)
  AZURE_OPENAI_ENDPOINT   - Azure OpenAI 端点 (可选)
  OPENAI_MODEL            - OpenAI 模型名称 (可选)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 通用参数
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )
    
    # 1. get 命令 - 获取页面内容
    get_parser = subparsers.add_parser(
        'get',
        parents=[common_parser],
        help='获取页面内容'
    )
    get_subparsers = get_parser.add_subparsers(dest='get_format', help='输出格式')
    
    # get 默认（HTML）
    get_html_parser = get_subparsers.add_parser('html', help='获取HTML格式内容（默认）')
    get_html_parser.add_argument('url', help='Confluence 页面 URL')
    get_html_parser.add_argument('--output', '-o', help='输出文件路径（不指定则输出到控制台）')
    
    # get markdown
    get_md_parser = get_subparsers.add_parser('markdown', help='获取并转换为Markdown格式')
    get_md_parser.add_argument('url', help='Confluence 页面 URL')
    get_md_parser.add_argument('--output', '-o', help='输出文件路径（不指定则输出到控制台）')
    
    # get md (markdown的简写)
    get_md_short_parser = get_subparsers.add_parser('md', help='获取并转换为Markdown格式（简写）')
    get_md_short_parser.add_argument('url', help='Confluence 页面 URL')
    get_md_short_parser.add_argument('--output', '-o', help='输出文件路径（不指定则输出到控制台）')
    
    # 如果没有指定子命令，默认为 HTML
    get_parser.add_argument('url', nargs='?', help='Confluence 页面 URL（当不使用子命令时）')
    get_parser.add_argument('--output', '-o', help='输出文件路径（不指定则输出到控制台）')
    
    # 2. format 命令 - 格式化页面
    format_parser = subparsers.add_parser(
        'format',
        parents=[common_parser],
        help='格式化页面内容并写回'
    )
    format_parser.add_argument(
        'reorganize_level',
        type=int,
        choices=[0, 1, 2, 3],
        nargs='?',
        default=1,
        help='重组织级别: 0=仅排版, 1=修正错别字(默认), 2=重组内容, 3=创意优化'
    )
    format_parser.add_argument('url', help='Confluence 页面 URL')
    format_parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='演练模式，不实际更新页面'
    )
    
    # 3. llm 命令 - 根据页面指令执行LLM任务
    llm_parser = subparsers.add_parser(
        'llm',
        parents=[common_parser],
        help='根据页面内容中的指令执行LLM任务'
    )
    llm_parser.add_argument('url', help='包含LLM指令的Confluence页面 URL')
    llm_parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='演练模式，不实际更新页面'
    )
    
    # 4. upload 命令 - 上传文件内容
    upload_parser = subparsers.add_parser(
        'upload',
        parents=[common_parser],
        help='上传本地文件内容到页面'
    )
    upload_parser.add_argument('file', help='要上传的文件路径')
    upload_parser.add_argument('url', help='目标 Confluence 页面 URL')
    upload_parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'text'],
        default='markdown',
        help='输入文件格式（默认: markdown）'
    )
    upload_parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='演练模式，不实际更新页面'
    )
    
    # 5. test 命令 - 测试连接
    test_parser = subparsers.add_parser(
        'test',
        parents=[common_parser],
        help='测试 Confluence API 连接和认证'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def validate_environment():
    """验证环境变量配置"""
    import os
    
    required_vars = [
        'CONFLUENCE_BASE_URL',
        'CONFLUENCE_USERNAME', 
        'CONFLUENCE_API_TOKEN',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 错误：缺少必需的环境变量配置\n")
        print("请设置以下环境变量：")
        for var in missing_vars:
            print(f"  - {var}")
        
        print("\n您可以通过以下方式设置环境变量：")
        print("1. 创建 .env 文件：")
        for var in missing_vars:
            print(f"   {var}=your_value")
        
        print("\n2. 在命令行中设置：")
        for var in missing_vars:
            print(f"   export {var}='your_value'")
        
        return False
    
    return True


def cmd_get(args, formatter):
    """获取页面内容命令"""
    logger = logging.getLogger(__name__)
    
    try:
        # 获取URL - 修复参数传递问题
        url = None
        if hasattr(args, 'get_format') and args.get_format and hasattr(args, 'url'):
            url = args.url
        elif hasattr(args, 'url') and args.url:
            url = args.url
        
        if not url:
            print("❌ 缺少页面 URL 参数")
            return False
        
        # 处理子命令格式
        if hasattr(args, 'get_format') and args.get_format:
            if args.get_format in ['markdown', 'md']:
                # Markdown格式
                print(f"📄 获取页面并转换为Markdown: {url}")
                logger.info(f"获取页面并转换为 Markdown: {url}")
                
                result = formatter.convert_page_to_markdown(url)
                
                if not result['success']:
                    logger.error(f"转换失败: {result['error']}")
                    print(f"❌ 转换失败: {result['error']}")
                    return False
                    
                markdown_content = result['markdown']
                
                if args.output:
                    # 保存到文件
                    output_path = Path(args.output)
                else:
                    # 生成默认文件名
                    safe_title = "".join(c for c in result['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    output_path = Path(f"{safe_title}.md")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"✅ Markdown内容已保存到: {output_path}")
                
                return True
                
            elif args.get_format == 'html':
                # HTML格式 - URL已经在上面设置了
                pass
            else:
                print(f"❌ 未知的输出格式: {args.get_format}")
                return False
        
        # HTML格式处理
        print(f"📄 获取页面内容: {url}")
        logger.info(f"获取页面内容: {url}")
        logger.info(f"解析页面 URL: {url}")
        
        result = formatter.get_page_content_by_url(url)
        
        if not result['success']:
            logger.error(f"获取页面内容时发生错误: {result['error']}")
            print(f"❌ 获取失败: {result['error']}")
            
            # 显示调试信息
            if 'debug_info' in result and result['debug_info']:
                print("\n🔍 诊断信息:")
                debug_info = result['debug_info']
                
                if 'confluence_url' in debug_info:
                    print(f"   Confluence URL: {debug_info['confluence_url']}")
                if 'username' in debug_info:
                    print(f"   用户名: {debug_info['username']}")
                if 'detected_space' in debug_info:
                    print(f"   检测到的空间: {debug_info['detected_space']}")
                if 'detected_title' in debug_info:
                    print(f"   检测到的页面标题: {debug_info['detected_title']}")
                if 'api_connection' in debug_info:
                    print(f"   API 连接状态: {debug_info['api_connection']}")
                if 'accessible_spaces' in debug_info:
                    print(f"   可访问空间数量: {debug_info['accessible_spaces']}")
                if 'target_space_exists' in debug_info:
                    status = "✅ 存在" if debug_info['target_space_exists'] else "❌ 不存在"
                    print(f"   目标空间状态: {status}")
                if 'space_pages_count' in debug_info:
                    print(f"   空间中的页面数量: {debug_info['space_pages_count']}")
                
                print("\n💡 故障排除建议:")
                print("   1. 检查环境变量配置 (CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)")
                print("   2. 确认用户有访问目标空间和页面的权限")
                print("   3. 验证页面 URL 是否正确")
                print("   4. 尝试在浏览器中访问该页面确认其存在")
            
            return False
            
        html_content = result['content']
        
        if args.output:
            # 保存到文件
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 内容已保存到: {output_path}")
        else:
            # 输出到控制台
            print("="*60)
            print(f"页面标题: {result['title']}")
            print(f"页面ID: {result['page_id']}")
            print("="*60)
            print(html_content)
        
        return True
        
    except Exception as e:
        logger.error(f"获取页面内容失败: {str(e)}")
        print(f"❌ 获取页面内容失败: {str(e)}")
        return False


def cmd_format(args, formatter):
    """格式化页面命令"""
    logger = logging.getLogger(__name__)
    
    try:
        print(f"✨ 格式化页面: {args.url}")
        if args.dry_run:
            print("🧪 演练模式：不会实际更新页面")
        
        # 处理重组等级参数
        reorganize_level = getattr(args, 'reorganize_level', 1)  # 默认等级1
        
        # 显示重组等级说明
        reorganize_descriptions = {
            0: "等级0 - 仅修正格式，不改变内容结构",
            1: "等级1 - 修正格式和标题层级（默认）",
            2: "等级2 - 中等重组：调整段落顺序和内容结构",
            3: "等级3 - 深度重组：完全重新组织内容"
        }
        
        print(f"📊 重组等级: {reorganize_descriptions.get(reorganize_level, '未知等级')}")
        
        result = formatter.process_page_by_url(
            page_url=args.url,
            reorganize_level=reorganize_level,
            dry_run=args.dry_run
        )
        
        if result['success']:
            if result['dry_run']:
                print("✅ 演练模式执行完成")
                print(f"   页面标题: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                print("   ℹ️  这是演练模式，页面未实际更新")
            else:
                print("✅ 页面格式化完成")
                print(f"   页面标题: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                if 'formatted' in result and result['formatted']:
                    print("   🎨 页面内容已格式化并更新")
                else:
                    print("   ℹ️  页面内容无需更新")
        else:
            print(f"❌ 格式化失败: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        logger.error(f"格式化页面失败: {str(e)}")
        print(f"❌ 格式化页面失败: {str(e)}")
        return False


def cmd_upload(args, formatter):
    """上传文件内容命令"""
    logger = logging.getLogger(__name__)
    
    try:
        # 检查文件是否存在
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        print(f"📤 上传文件内容: {file_path} -> {args.url}")
        print(f"文件格式: {args.format}")
        if args.dry_run:
            print("🧪 演练模式：不会实际更新页面")
        
        result = formatter.upload_file_to_page(
            file_path=str(file_path),
            page_url=args.url,
            file_format=args.format,
            dry_run=args.dry_run
        )
        
        if result['success']:
            if result['dry_run']:
                print("✅ 演练模式执行完成")
                print(f"   目标页面: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                print("   ℹ️  这是演练模式，页面未实际更新")
            else:
                print("✅ 文件上传完成")
                print(f"   目标页面: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                print("   ✨ 页面内容已成功更新")
        else:
            print(f"❌ 上传失败: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        print(f"❌ 上传文件失败: {str(e)}")
        return False


def cmd_test(args, formatter):
    """测试连接命令"""
    logger = logging.getLogger(__name__)
    
    try:
        print("🔍 测试 Confluence API 连接...")
        print(f"   Confluence URL: {formatter.confluence_url}")
        print(f"   Confluence 类型: {formatter.confluence_type}")
        if formatter.confluence_type == "Cloud":
            print(f"   用户名: {formatter.username}")
        else:
            print(f"   认证方式: 个人访问令牌")
        
        # API Token 预览
        if formatter.api_token:
            token_preview = formatter.api_token[:8] + "..." + formatter.api_token[-4:] if len(formatter.api_token) > 12 else "****"
            if formatter.confluence_type == "Cloud":
                print(f"   API Token: {token_preview} (长度: {len(formatter.api_token)} 字符)")
            else:
                print(f"   个人访问令牌: {token_preview} (长度: {len(formatter.api_token)} 字符)")
        else:
            print("   ❌ 认证令牌: 未设置")
            return False
        
        print("\n1️⃣ 测试基础连接...")
        try:
            # 测试获取空间列表（使用正确的方法名）
            spaces = formatter.confluence.get_all_spaces(limit=1)
            print(f"   ✅ API 连接成功")
            
            # 尝试获取当前用户信息
            try:
                user_info = formatter.confluence.get_current_user()
                print(f"   👤 当前用户: {user_info.get('displayName', 'N/A')}")
                print(f"   📧 邮箱: {user_info.get('email', 'N/A')}")
            except Exception as user_e:
                print(f"   ⚠️  无法获取用户详情: {str(user_e)}")
                
        except Exception as e:
            print(f"   ❌ API 连接失败: {str(e)}")
            if "401" in str(e) or "Unauthorized" in str(e):
                print("   💡 这通常表示认证失败，请检查认证配置")
                print(f"   🔧 建议检查:")
                if formatter.confluence_type == "Cloud":
                    print(f"      - CONFLUENCE_USERNAME 应该是完整的邮箱地址")
                    print(f"      - CONFLUENCE_API_TOKEN 应该是有效的 API Token")
                    print(f"      - 在 https://id.atlassian.com/manage-profile/security/api-tokens 重新生成 Token")
                else:
                    print(f"      - CONFLUENCE_API_TOKEN 应该是有效的个人访问令牌")
                    print(f"      - 在 {formatter.confluence_url}/plugins/personalaccesstokens/usertokens.action 重新生成令牌")
                    print(f"      - 确保令牌有足够的权限访问所需的空间和页面")
                    print(f"      - CONFLUENCE_USERNAME 在 Server/Data Center 模式下不需要设置")
            elif "403" in str(e):
                print("   💡 权限不足，用户可能没有足够的权限")
            elif "404" in str(e):
                print("   💡 请检查 CONFLUENCE_BASE_URL 是否正确")
            return False
        
        print("\n2️⃣ 测试空间访问权限...")
        try:
            spaces = formatter.confluence.get_all_spaces(limit=5)
            if spaces and len(spaces) > 0:
                print(f"   ✅ 可访问 {len(spaces)} 个空间")
                # 安全地处理空间列表
                for i, space in enumerate(spaces):
                    if i >= 3:  # 只显示前3个
                        break
                    try:
                        # 处理不同的数据结构
                        if isinstance(space, dict):
                            space_key = space.get('key', 'N/A')
                            space_name = space.get('name', 'N/A')
                        else:
                            # 如果 space 是字符串或其他类型
                            space_key = str(space)
                            space_name = 'N/A'
                        print(f"      - {space_key}: {space_name}")
                    except Exception as space_error:
                        print(f"      - 空间 {i+1}: [数据格式错误: {str(space_error)}]")
                if len(spaces) > 3:
                    print(f"      ... 还有 {len(spaces) - 3} 个空间")
            else:
                print("   ⚠️  没有可访问的空间")
        except Exception as e:
            print(f"   ❌ 空间列表获取失败: {str(e)}")
            # 不要因为空间列表失败就返回 False，这不是致命错误
            print("   💡 这可能不影响基本功能，可以尝试直接使用页面 URL")
        
        print("\n3️⃣ 测试 OpenAI 连接...")
        try:
            print(f"   OpenAI Base URL: {formatter.openai_base_url}")
            print(f"   模型: {formatter.openai_model}")
            
            # 简单的测试请求
            response = formatter.openai_client.chat.completions.create(
                model=formatter.openai_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("   ✅ OpenAI API 连接成功")
        except Exception as e:
            print(f"   ❌ OpenAI API 连接失败: {str(e)}")
            if "401" in str(e):
                print("   💡 请检查 OPENAI_API_KEY 是否正确")
            elif "404" in str(e):
                print("   💡 请检查 OPENAI_BASE_URL 是否正确")
            return False
        
        print("\n🎉 所有连接测试通过！系统可以正常使用。")
        return True
        
    except Exception as e:
        logger.error(f"连接测试失败: {str(e)}")
        print(f"❌ 连接测试失败: {str(e)}")
        return False


def cmd_llm(args, formatter):
    """根据页面指令执行LLM任务命令"""
    logger = logging.getLogger(__name__)
    
    try:
        print(f"🤖 执行LLM指令任务: {args.url}")
        if args.dry_run:
            print("🧪 演练模式：不会实际更新页面")
        
        result = formatter.execute_llm_instruction(
            page_url=args.url,
            dry_run=args.dry_run
        )
        
        if result['success']:
            if result['dry_run']:
                print("✅ 演练模式执行完成")
                print(f"   页面标题: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                print("   ℹ️  这是演练模式，页面未实际更新")
            else:
                print("✅ LLM任务执行完成")
                print(f"   页面标题: {result['title']}")
                print(f"   页面ID: {result['page_id']}")
                print("   🤖 LLM任务已成功执行并更新页面")
        else:
            print(f"❌ LLM任务执行失败: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        logger.error(f"LLM任务执行失败: {str(e)}")
        print(f"❌ LLM任务执行失败: {str(e)}")
        return False


def main():
    """主函数"""
    
    # 显示启动横幅
    print("🚀 启动 wiki-fmt - Confluence 文档处理工具")
    print("=" * 60)
    
    try:
        # 解析命令行参数
        parser = create_parser()
        args = parser.parse_args()
        
        # 检查是否提供了命令
        if not args.command:
            parser.print_help()
            return
        
        # 设置日志
        setup_logging(args.debug)
        
        # 验证环境变量
        if not validate_environment():
            return
        
        # 初始化格式化器
        logger = logging.getLogger(__name__)
        logger.info("初始化 Confluence 格式化器...")
        formatter = ConfluenceFormatter()
        
        # 执行对应的命令
        success = False
        if args.command == 'get':
            success = cmd_get(args, formatter)
        elif args.command == 'format':
            success = cmd_format(args, formatter)
        elif args.command == 'upload':
            success = cmd_upload(args, formatter)
        elif args.command == 'test':
            success = cmd_test(args, formatter)
        elif args.command == 'llm':
            success = cmd_llm(args, formatter)
        else:
            print(f"❌ 未知命令: {args.command}")
        
        # 输出结果
        print("=" * 60)
        if success:
            print("✅ 操作成功")
        else:
            print("❌ 操作失败")
            
    except KeyboardInterrupt:
        print("\n⏹️  操作被用户中断")
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        logging.getLogger(__name__).error(f"程序执行失败: {str(e)}", exc_info=True)


if __name__ == '__main__':
    main() 