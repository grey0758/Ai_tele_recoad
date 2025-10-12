"""使用WeasyPrint将Markdown转换为PDF - 专门针对已安装GTK3的环境"""

import logging
import os
from pathlib import Path
import traceback

# 导入必要的库
try:
    import markdown  # type: ignore
    MARKDOWN_AVAILABLE = True
    print("✅ markdown库导入成功")
except ImportError as e:
    MARKDOWN_AVAILABLE = False
    print(f"❌ markdown库导入失败: {e}")

try:
    import weasyprint  # type: ignore
    WEASYPRINT_AVAILABLE = True
    print("✅ weasyprint库导入成功")
    
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
    
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    print(f"❌ weasyprint库导入失败: {e}")


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


def markdown_to_pdf_weasyprint(markdown_file: str, output_file: str) -> bool:
    """使用WeasyPrint将Markdown转换为PDF"""
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        print("❌ 缺少必要的库 (weasyprint 或 markdown)")
        return False
    
    try:
        print(f"🔄 开始转换: {markdown_file} -> {output_file}")
        
        # 读取Markdown文件
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 转换为HTML
        html_body = markdown.markdown(markdown_content, extensions=['extra', 'codehilite', 'tables'])
        
        # 获取文件名作为标题
        file_title = Path(markdown_file).stem
        full_html = get_html_template(html_body, file_title)
        
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
        
        # 生成PDF
        html_doc.write_pdf(output_file, stylesheets=[css])
        print(f"✅ WeasyPrint转换成功: {output_file}")
        return True
        
    except OSError as e:
        if "libgobject" in str(e) or "cannot load library" in str(e):
            print(f"❌ WeasyPrint遇到GTK依赖问题: {e}")
            print("💡 请确保已正确安装GTK3和相关依赖")
            print("💡 Windows用户可能需要安装: GTK3, Cairo, Pango, GdkPixbuf")
            return False
        else:
            print(f"❌ WeasyPrint系统依赖错误: {e}")
            return False
    except Exception as e:
        print(f"❌ WeasyPrint转换失败: {e}")
        traceback.print_exc()
        return False


def test_weasyprint_conversion():
    """测试WeasyPrint转换功能"""
    
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        print("❌ 缺少必要的库，无法进行转换测试")
        return
    
    # 测试文件列表
    test_files = [
        "consultant_analysis_output/2025-10-10/智浩_顾问分析报告_2025-10-10_20251010_184425.md",
        "consultant_analysis_output/2025-10-10/思怡_顾问分析报告_2025-10-10_20251010_184529.md", 
        "consultant_analysis_output/2025-10-10/佳慧_顾问分析报告_2025-10-10_20251010_184633.md"
    ]
    
    print("=== 开始测试WeasyPrint转换功能 ===")
    
    # 创建输出目录
    output_dir = Path("weasyprint_output")
    output_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_count = 0
    
    for md_file in test_files:
        if not os.path.exists(md_file):
            print(f"❌ 文件不存在: {md_file}")
            continue
            
        print(f"\n📄 正在转换: {md_file}")
        total_count += 1
        
        # 获取文件名（不含扩展名）
        file_name = Path(md_file).stem
        
        # 转换到PDF
        pdf_file = output_dir / f"{file_name}.pdf"
        if markdown_to_pdf_weasyprint(md_file, str(pdf_file)):
            success_count += 1
    
    print("\n=== WeasyPrint转换测试完成 ===")
    print(f"成功转换: {success_count}/{total_count} 个文件")
    
    if success_count > 0:
        print(f"✅ 输出目录: {output_dir.absolute()}")
    else:
        print("❌ 没有文件转换成功")


def test_single_file_conversion():
    """测试单个文件的转换"""
    
    if not WEASYPRINT_AVAILABLE or not MARKDOWN_AVAILABLE:
        print("❌ 缺少必要的库，无法进行转换测试")
        return
    
    # 选择一个测试文件
    test_file = "consultant_analysis_output/2025-10-10/智浩_顾问分析报告_2025-10-10_20251010_184425.md"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print("=== 测试单个文件转换 ===")
    print(f"📄 源文件: {test_file}")
    
    # 创建输出目录
    output_dir = Path("weasyprint_single_output")
    output_dir.mkdir(exist_ok=True)
    
    file_name = Path(test_file).stem
    
    # 转换到PDF
    pdf_file = output_dir / f"{file_name}.pdf"
    print(f"\n🔄 转换为PDF: {pdf_file}")
    
    if markdown_to_pdf_weasyprint(test_file, str(pdf_file)):
        print(f"✅ 转换成功，输出文件: {pdf_file.absolute()}")
    else:
        print("❌ 转换失败")
    
    print("\n=== 单个文件转换测试完成 ===")


def check_weasyprint_status():
    """检查WeasyPrint状态"""
    print("=== WeasyPrint状态检查 ===")
    
    if not WEASYPRINT_AVAILABLE:
        print("❌ WeasyPrint库未安装")
        print("💡 安装命令: pip install weasyprint")
        return False
    
    print("✅ WeasyPrint库已安装")
    
    try:
        # 尝试创建一个简单的HTML文档
        html_doc = weasyprint.HTML(string='<html><body><h1>测试</h1></body></html>')
        print("✅ WeasyPrint可以正常创建HTML文档")
        
        # 尝试生成PDF（不保存到文件）
        pdf_bytes = html_doc.write_pdf()
        print("✅ WeasyPrint可以正常生成PDF")
        print(f"✅ 生成的PDF大小: {len(pdf_bytes)} 字节")
        
        return True
        
    except OSError as e:
        if "libgobject" in str(e) or "cannot load library" in str(e):
            print(f"❌ WeasyPrint遇到GTK依赖问题: {e}")
            print("💡 请确保已正确安装GTK3和相关依赖")
            return False
        else:
            print(f"❌ WeasyPrint系统依赖错误: {e}")
            return False
    except Exception as e:
        print(f"❌ WeasyPrint测试失败: {e}")
        return False


if __name__ == "__main__":
    print("=== WeasyPrint Markdown转换工具 ===")
    print("选择操作:")
    print("1. 检查WeasyPrint状态")
    print("2. 测试所有文件转换")
    print("3. 测试单个文件转换")
    
    try:
        choice = input("请输入选择 (1, 2 或 3): ").strip()
        
        if choice == "1":
            check_weasyprint_status()
        elif choice == "2":
            test_weasyprint_conversion()
        elif choice == "3":
            test_single_file_conversion()
        else:
            print("无效选择，默认检查WeasyPrint状态")
            check_weasyprint_status()
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
