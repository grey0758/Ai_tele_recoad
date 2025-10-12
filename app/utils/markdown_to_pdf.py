"""Markdown到PDF转换工具模块"""

import logging
from pathlib import Path
from typing import Optional
import sys
from io import StringIO
try:
    import markdown  # type: ignore
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    import weasyprint  # type: ignore
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from app.core.logger import get_logger

logger = get_logger(__name__)

# 关闭WeasyPrint的详细日志
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('weasyprint.document').setLevel(logging.ERROR)
logging.getLogger('weasyprint.css').setLevel(logging.ERROR)
logging.getLogger('weasyprint.html').setLevel(logging.ERROR)
logging.getLogger('weasyprint.text').setLevel(logging.ERROR)
logging.getLogger('weasyprint.layout').setLevel(logging.ERROR)
logging.getLogger('weasyprint.draw').setLevel(logging.ERROR)
logging.getLogger('weasyprint.fonts').setLevel(logging.ERROR)
logging.getLogger('weasyprint.progress').setLevel(logging.ERROR)
logging.getLogger('weasyprint.utils').setLevel(logging.ERROR)

# 关闭其他可能产生调试信息的日志
logging.getLogger('fontTools').setLevel(logging.ERROR)
logging.getLogger('fontTools.subset').setLevel(logging.ERROR)
logging.getLogger('cffi').setLevel(logging.ERROR)


def silence_weasyprint_logs():
    """完全静默WeasyPrint的所有日志输出"""
    
    # 临时重定向stderr来捕获WeasyPrint的输出
    old_stderr = sys.stderr
    sys.stderr = StringIO()
    
    try:
        # 设置所有相关日志级别为CRITICAL（最高级别，几乎不输出）
        weasyprint_loggers = [
            'weasyprint', 'weasyprint.document', 'weasyprint.css', 
            'weasyprint.html', 'weasyprint.text', 'weasyprint.layout', 
            'weasyprint.draw', 'weasyprint.fonts', 'weasyprint.progress', 
            'weasyprint.utils', 'fontTools', 'fontTools.subset', 'cffi'
        ]
        
        for logger_name in weasyprint_loggers:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
            
    finally:
        # 恢复stderr
        sys.stderr = old_stderr


def get_html_template(html_body: str, title: str = "顾问分析报告") -> str:
    """获取完整的HTML模板，包含CSS样式"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: "Microsoft YaHei", "SimSun", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #fff;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                font-weight: 600;
            }}
            
            h1 {{ 
                font-size: 2.2em; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 0.3em;
                text-align: center;
                margin-bottom: 1em;
            }}
            
            h2 {{ 
                font-size: 1.8em; 
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 0.2em;
            }}
            
            h3 {{ font-size: 1.4em; }}
            h4 {{ font-size: 1.2em; }}
            h5 {{ font-size: 1.1em; }}
            h6 {{ font-size: 1em; }}
            
            p {{ 
                margin-bottom: 1em; 
                text-align: justify;
            }}
            
            ul, ol {{
                margin-bottom: 1em;
                padding-left: 2em;
            }}
            
            li {{
                margin-bottom: 0.3em;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
                color: #2c3e50;
            }}
            
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            pre {{
                background-color: #f6f8fa;
                padding: 1em;
                border-radius: 6px;
                font-family: 'Courier New', 'Consolas', monospace;
                font-size: 0.9em;
                margin: 1em 0;
                overflow-x: auto;
                border-left: 4px solid #3498db;
            }}
            
            code {{
                font-family: 'Courier New', 'Consolas', monospace;
                background-color: #f0f0f0;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-size: 0.9em;
                color: #e74c3c;
            }}
            
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 1em;
                margin: 1em 0;
                color: #555;
                font-style: italic;
                background-color: #f8f9fa;
                padding: 1em;
                border-radius: 0 4px 4px 0;
            }}
            
            hr {{
                border: none;
                height: 2px;
                background: linear-gradient(to right, #3498db, #2ecc71);
                margin: 2em 0;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """


def markdown_to_pdf_weasyprint(markdown_file: str, output_file: str, title: Optional[str] = None) -> bool:
    """
    使用WeasyPrint将Markdown转换为PDF
    
    Args:
        markdown_file: Markdown文件路径
        output_file: 输出PDF文件路径
        title: 文档标题，默认为文件名
        
    Returns:
        bool: 转换是否成功
    """
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        logger.error("缺少必要的库 (weasyprint 或 markdown)")
        return False
    
    try:
        logger.info("开始转换Markdown到PDF: %s -> %s", markdown_file, output_file)
        
        # 读取Markdown文件
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 转换为HTML
        html_body = markdown.markdown(markdown_content, extensions=['extra', 'codehilite', 'tables'])
        
        # 获取文件名作为标题
        if title is None:
            title = Path(markdown_file).stem
        full_html = get_html_template(html_body, title)
        
        # 使用WeasyPrint转换
        html_doc = weasyprint.HTML(string=full_html)
        
        # 添加额外的CSS样式
        css = weasyprint.CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: "Microsoft YaHei", "SimSun", sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                page-break-after: avoid;
            }
            h2, h3 {
                page-break-after: avoid;
            }
            table {
                page-break-inside: avoid;
            }
            pre {
                page-break-inside: avoid;
            }
        ''')
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 生成PDF（使用静默模式）
        silence_weasyprint_logs()
        html_doc.write_pdf(output_file, stylesheets=[css])
        logger.info("WeasyPrint转换成功: %s", output_file)
        return True
        
    except OSError as e:
        if "libgobject" in str(e) or "cannot load library" in str(e):
            logger.error("WeasyPrint遇到GTK依赖问题: %s", e)
            logger.error("请确保已正确安装GTK3和相关依赖")
            return False
        else:
            logger.error("WeasyPrint系统依赖错误: %s", e)
            return False
    except Exception as e:
        logger.error("WeasyPrint转换失败: %s", e)
        return False


def markdown_content_to_pdf(markdown_content: str, output_file: str, title: str = "文档") -> bool:
    """
    将Markdown内容直接转换为PDF
    
    Args:
        markdown_content: Markdown内容字符串
        output_file: 输出PDF文件路径
        title: 文档标题
        
    Returns:
        bool: 转换是否成功
    """
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        logger.error("缺少必要的库 (weasyprint 或 markdown)")
        return False
    
    try:
        logger.info("开始转换Markdown内容到PDF: %s", output_file)
        
        # 转换为HTML
        html_body = markdown.markdown(markdown_content, extensions=['extra', 'codehilite', 'tables'])
        full_html = get_html_template(html_body, title)
        
        # 使用WeasyPrint转换
        html_doc = weasyprint.HTML(string=full_html)
        
        # 添加额外的CSS样式
        css = weasyprint.CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: "Microsoft YaHei", "SimSun", sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                page-break-after: avoid;
            }
            h2, h3 {
                page-break-after: avoid;
            }
            table {
                page-break-inside: avoid;
            }
            pre {
                page-break-inside: avoid;
            }
        ''')
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 生成PDF（使用静默模式）
        silence_weasyprint_logs()
        html_doc.write_pdf(output_file, stylesheets=[css])
        logger.info("WeasyPrint转换成功: %s", output_file)
        return True
        
    except OSError as e:
        if "libgobject" in str(e) or "cannot load library" in str(e):
            logger.error("WeasyPrint遇到GTK依赖问题: %s", e)
            logger.error("请确保已正确安装GTK3和相关依赖")
            return False
        else:
            logger.error("WeasyPrint系统依赖错误: %s", e)
            return False
    except Exception as e:
        logger.error("WeasyPrint转换失败: %s", e)
        return False


def check_weasyprint_availability() -> bool:
    """
    检查WeasyPrint是否可用
    
    Returns:
        bool: WeasyPrint是否可用
    """
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        logger.warning("WeasyPrint或markdown库不可用")
        return False
    
    try:
        # 尝试创建一个简单的HTML文档
        html_doc = weasyprint.HTML(string='<html><body><h1>测试</h1></body></html>')
        # 尝试生成PDF（不保存到文件）
        pdf_bytes = html_doc.write_pdf()
        logger.info("WeasyPrint可用，测试PDF大小: %d 字节", len(pdf_bytes))
        return True
        
    except OSError as e:
        if "libgobject" in str(e) or "cannot load library" in str(e):
            logger.error("WeasyPrint遇到GTK依赖问题: %s", e)
            return False
        else:
            logger.error("WeasyPrint系统依赖错误: %s", e)
            return False
    except Exception as e:
        logger.error("WeasyPrint测试失败: %s", e)
        return False
