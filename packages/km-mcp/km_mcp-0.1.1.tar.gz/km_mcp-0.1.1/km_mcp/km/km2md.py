#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
学城JSON格式转Markdown工具

此脚本用于将学城文档的JSON格式转换为Markdown格式。
学城文档的JSON格式是一个树形嵌套结构，主要包含type, content, attrs, marks四个属性。
"""

import json
import argparse
import os
import re
from typing import Dict, List, Any, Optional, Union
from utils.logger import get_logger
from sso.meituan_requests import MeituanRequests
from km.minder_parser import convert_minder_to_plantuml 
from km.drawio_to_mermaid import convert_drawio_to_mermaid
logger = get_logger()

class KM2MD:
    """学城JSON格式转Markdown的转换器"""

    def __init__(self):
        # 缩进级别，用于列表等需要缩进的元素
        self.indent_level = 0
        # 是否在代码块内
        self.in_code_block = False
        # 表格状态
        self.in_table = False
        self.table_headers = []
        self.table_rows = []
        # 当前列表类型栈
        self.list_stack = []

    def convert(self, json_content: Union[str, Dict]) -> str:
        """
        将学城JSON格式转换为Markdown
        
        Args:
            json_content: JSON字符串或已解析的JSON对象
            
        Returns:
            转换后的Markdown文本
        """
        if isinstance(json_content, str):
            try:
                data = json.loads(json_content)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format"
        else:
            data = json_content
            
        # 重置状态
        self.indent_level = 0
        self.in_code_block = False
        self.in_table = False
        self.table_headers = []
        self.table_rows = []
        self.list_stack = []
        
        # 开始转换
        return self._process_node(data)
    
    def _process_node(self, node: Dict) -> str:
        """处理节点，根据节点类型调用相应的处理函数"""
        node_type = node.get("type", "")
        
        # 根据节点类型调用相应的处理函数
        handler = getattr(self, f"_handle_{node_type}", self._handle_unknown)
        return handler(node)
    
    def _process_content(self, content: List[Dict]) -> str:
        """处理节点的内容（子节点）"""
        if not content:
            return ""
            
        result = []
        for item in content:
            result.append(self._process_node(item))
            
        return "".join(result)
    
    def _process_marks(self, text: str, marks: List[Dict]) -> str:
        """处理文本的标记（加粗、斜体等）"""
        if not marks:
            return text
            
        for mark in marks:
            mark_type = mark.get("type", "")
            
            if mark_type == "strong":
                text = f"**{text}**"
            elif mark_type == "em":
                text = f"*{text}*"
            elif mark_type == "underline":
                text = f"<u>{text}</u>"
            elif mark_type == "strikethrough":
                text = f"~~{text}~~"
            elif mark_type == "code":
                text = f"`{text}`"
            elif mark_type == "sub":
                text = f"<sub>{text}</sub>"
            elif mark_type == "sup":
                text = f"<sup>{text}</sup>"
        return text
    
    # 处理各种节点类型的函数
    def _handle_doc(self, node: Dict) -> str:
        """处理文档节点"""
        content = node.get("content", [])
        return self._process_content(content)
    
    def _handle_title(self, node: Dict) -> str:
        """处理标题节点"""
        content = node.get("content", [])
        title_text = self._process_content(content)
        return f"# {title_text}\n\n"
    
    def _handle_text(self, node: Dict) -> str:
        """处理文本节点"""
        text = node.get("text", "")
        marks = node.get("marks", [])
        
        if marks:
            text = self._process_marks(text, marks)
            
        return text
    
    def _handle_paragraph(self, node: Dict) -> str:
        """处理段落节点"""
        content = node.get("content", [])
        attrs = node.get("attrs", {})
        indent = attrs.get("indent", 0)
        align = attrs.get("align", "")
        
        text = self._process_content(content)
        
        # 如果在表格中，不添加额外的换行
        if self.in_table:
            return text
            
        # 处理缩进和对齐
        indent_str = "    " * indent
        
        # 如果段落为空且不在代码块内，返回一个换行
        if not text.strip() and not self.in_code_block:
            return "\n"
            
        return f"{indent_str}{text}\n\n"
    
    def _handle_heading(self, node: Dict) -> str:
        """处理标题节点"""
        content = node.get("content", [])
        attrs = node.get("attrs", {})
        level = attrs.get("level", 1)
        
        # 确保级别在1-6之间
        level = max(1, min(level, 6))
        
        heading_text = self._process_content(content)
        return f"{'#' * level} {heading_text}\n\n"
    
    def _handle_bullet_list(self, node: Dict) -> str:
        """处理无序列表节点"""
        content = node.get("content", [])
        
        # 保存当前列表状态
        self.list_stack.append("bullet")
        self.indent_level += 1
        
        result = "\n"
        for item in content:
            result += self._process_node(item)
            
        # 恢复列表状态
        self.list_stack.pop()
        self.indent_level -= 1
        
        return result + "\n" if self.indent_level == 0 else result
    
    def _handle_ordered_list(self, node: Dict) -> str:
        """处理有序列表节点"""
        content = node.get("content", [])
        
        # 保存当前列表状态
        self.list_stack.append("ordered")
        self.indent_level += 1
        
        result = "\n"
        for i, item in enumerate(content):
            # 在处理列表项之前设置序号
            item["_list_index"] = i + 1
            result += self._process_node(item)
            
        # 恢复列表状态
        self.list_stack.pop()
        self.indent_level -= 1
        
        return result + "\n" if self.indent_level == 0 else result
    
    def _handle_list_item(self, node: Dict) -> str:
        """处理列表项节点"""
        content = node.get("content", [])
        
        # 确定列表标记
        if self.list_stack and self.list_stack[-1] == "ordered":
            list_index = node.get("_list_index", 1)
            marker = f"{list_index}."
        else:
            marker = "-"
            
        # 处理缩进
        indent = "  " * (self.indent_level - 1)
        
        # 处理列表项内容
        result = f"{indent}{marker} "
        
        # 处理第一个子节点（通常是段落）
        if content:
            first_item = content[0]
            # 如果是段落，特殊处理以避免额外的换行
            if first_item.get("type") == "paragraph":
                para_content = first_item.get("content", [])
                result += self._process_content(para_content)
                # 处理剩余的子节点
                for item in content[1:]:
                    result += self._process_node(item)
            else:
                # 如果不是段落，正常处理
                for item in content:
                    result += self._process_node(item)
                    
        return result + "\n"
    
    def _handle_task_list(self, node: Dict) -> str:
        """处理任务列表节点"""
        # 与无序列表类似，但使用任务列表标记
        content = node.get("content", [])
        
        # 保存当前列表状态
        self.list_stack.append("task")
        self.indent_level += 1
        
        result = "\n"
        for item in content:
            result += self._process_node(item)
            
        # 恢复列表状态
        self.list_stack.pop()
        self.indent_level -= 1
        
        return result + "\n" if self.indent_level == 0 else result
    
    def _handle_task_item(self, node: Dict) -> str:
        """处理任务列表项节点"""
        content = node.get("content", [])
        attrs = node.get("attrs", {})
        checked = attrs.get("checked", False)
        
        # 确定任务标记
        marker = "[x]" if checked else "[ ]"
        
        # 处理缩进
        indent = "  " * (self.indent_level - 1)
        
        # 处理列表项内容
        result = f"{indent}- {marker} "
        
        # 处理第一个子节点（通常是段落）
        if content:
            first_item = content[0]
            # 如果是段落，特殊处理以避免额外的换行
            if first_item.get("type") == "paragraph":
                para_content = first_item.get("content", [])
                result += self._process_content(para_content)
                # 处理剩余的子节点
                for item in content[1:]:
                    result += self._process_node(item)
            else:
                # 如果不是段落，正常处理
                for item in content:
                    result += self._process_node(item)
                    
        return result + "\n"
    
    def _handle_code_block(self, node: Dict) -> str:
        """处理代码块节点"""
        content = node.get("content", [])
        attrs = node.get("attrs", {})
        language = attrs.get("language", "")
        title = attrs.get("title", "")
        
        # 设置代码块状态
        self.in_code_block = True
        
        # 处理代码内容
        code_content = self._process_content(content)
        
        # 恢复代码块状态
        self.in_code_block = False
        
        # 添加标题注释（如果有）
        title_comment = f"// {title}\n" if title else ""
        
        return f"```{language}\n{title_comment}{code_content}\n```\n\n"
    
    def _handle_link(self, node: Dict) -> str:
        """处理链接节点"""
        content = node.get("content", [])
        attrs = node.get("attrs", {})
        href = attrs.get("href", "")
        title = attrs.get("title", "")
        
        link_text = self._process_content(content)
        
        if title:
            return f"[{link_text}]({href} \"{title}\")"
        else:
            return f"[{link_text}]({href})"
    
    def _handle_open_iframe(self, node: Dict) -> str:
        """处理iframe节点"""
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        type = attrs.get("type", "")
        if type == "511H2i0612540259":
            attachment_id = attrs.get("attachmentId", "")
            return self._handle_mermaid_content(attachment_id)
        return f"![{type}]({src})\n\n"
    
    def _handle_mermaid_content(self, attachment_id: str) -> str:
        """处理Mermaid内容"""
        content = self._get_remote_content(f"https://km.sankuai.com/block/mermaid/api/fileinfo?thirdPartyId={attachment_id}", "mermaid")
        if content:
            return f"```mermaid\n{content}\n```\n\n"
        return f"[无法获取Mermaid内容: {attachment_id}]"
    
    def _handle_open_link(self, node: Dict) -> str:
        """处理iframe节点"""
        attrs = node.get("attrs", {})
        src = attrs.get("href", "")
        type = attrs.get("type", "")
        return f"[{type}]({src})"
        
    def _get_remote_content(self, url:str , type:str) -> str:
        """获取远程内容"""
        meituan_requests = MeituanRequests()
        response = meituan_requests.get(url, allow_redirects=True)
        try:
            response.raise_for_status()
            if response.status_code == 200:
                if type == "mermaid":
                    data = response.json()
                    return data.get("data",{}).get("content","")
                elif type == "minder":
                    return response.text
                else:
                    return response.text
            else:
                logger.error(f"获取远程内容失败: {response.status_code},{url}")
                return ""
        except Exception as e:
            logger.error(f"获取远程内容失败: {response.status_code},{url} ,{e}")
            return ""
    
    def _handle_image(self, node: Dict) -> str:
        """处理图片节点"""
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        name = attrs.get("name", "")
        
        # 构建图片标记
        alt_text = name or "image"
        return f"![{alt_text}]({src})\n\n"
    
    def _handle_table(self, node: Dict) -> str:
        """处理表格节点"""
        content = node.get("content", [])
        
        # 设置表格状态
        self.in_table = True
        self.table_headers = []
        self.table_rows = []
        
        # 处理表格内容
        table_content = self._process_content(content)
        
        # 恢复表格状态
        self.in_table = False
        
        # 如果没有表头，使用空表头
        if not self.table_headers:
            # 假设所有行的列数相同，使用第一行的列数
            if self.table_rows and self.table_rows[0]:
                col_count = len(self.table_rows[0])
                self.table_headers = [""] * col_count
        
        # 构建Markdown表格
        result = []
        
        # 表头
        result.append("| " + " | ".join(self.table_headers) + " |")
        
        # 分隔线
        result.append("| " + " | ".join(["---"] * len(self.table_headers)) + " |")
        
        # 表格内容
        for row in self.table_rows:
            # 确保行的列数与表头一致
            while len(row) < len(self.table_headers):
                row.append("")
            result.append("| " + " | ".join(row) + " |")
        
        return "\n" + "\n".join(result) + "\n\n"
    
    def _handle_table_row(self, node: Dict) -> str:
        """处理表格行节点"""
        content = node.get("content", [])
        
        # 处理行内容
        row_cells = []
        for cell in content:
            cell_content = self._process_node(cell)
            row_cells.append(cell_content.strip())
        
        # 添加到表格行
        self.table_rows.append(row_cells)
        
        return ""
    
    def _handle_table_header(self, node: Dict) -> str:
        """处理表格表头节点"""
        content = node.get("content", [])
        
        # 处理表头内容
        header_content = self._process_content(content)
        
        # 添加到表头
        self.table_headers.append(header_content.strip())
        
        return ""
    
    def _handle_table_cell(self, node: Dict) -> str:
        """处理表格单元格节点"""
        content = node.get("content", [])
        
        # 处理单元格内容
        return self._process_content(content)
    
    def _handle_blockquote(self, node: Dict) -> str:
        """处理引用节点"""
        content = node.get("content", [])
        
        # 处理引用内容
        quote_content = self._process_content(content)
        
        # 在每行前添加引用标记
        lines = quote_content.split("\n")
        quoted_lines = [f"> {line}" if line.strip() else ">" for line in lines]
        
        return "\n" + "\n".join(quoted_lines) + "\n\n"
    
    def _handle_horizontal_rule(self, node: Dict) -> str:
        """处理水平线节点"""
        return "\n---\n\n"
    
    def _handle_hard_break(self, node: Dict) -> str:
        """处理换行节点"""
        return "<br>\n"
    
    def _handle_latex_inline(self, node: Dict) -> str:
        """处理行内LaTeX公式节点"""
        attrs = node.get("attrs", {})
        content = attrs.get("content", "")
        
        return f"$${content}$$"
    
    def _handle_latex_block(self, node: Dict) -> str:
        """处理块级LaTeX公式节点"""
        attrs = node.get("attrs", {})
        content = attrs.get("content", "")
        
        return f"\n$$\n{content}\n$$\n\n"
    
    def _handle_mention(self, node: Dict) -> str:
        """处理@提及节点"""
        attrs = node.get("attrs", {})
        name = attrs.get("name", "")
        
        return f"@{name}"
    
    def _handle_status(self, node: Dict) -> str:
        """处理状态节点"""
        content = node.get("content", [])
        
        # 处理状态内容
        status_content = self._process_content(content)
        
        return f"[{status_content}]"
    
    def _handle_collapse(self, node: Dict) -> str:
        """处理折叠节点"""
        content = node.get("content", [])
        
        # 处理折叠内容
        collapse_content = self._process_content(content)
        
        return collapse_content
    
    def _handle_collapse_title(self, node: Dict) -> str:
        """处理折叠标题节点"""
        content = node.get("content", [])
        
        # 处理折叠标题内容
        title_content = self._process_content(content)
        
        return f"**{title_content}**\n"
    
    def _handle_collapse_content(self, node: Dict) -> str:
        """处理折叠内容节点"""
        content = node.get("content", [])
        
        # 处理折叠内容
        collapse_content = self._process_content(content)
        
        return f"{collapse_content}\n"
    
    def _handle_note(self, node: Dict) -> str:
        """处理注释节点"""
        content = node.get("content", [])
        # attrs = node.get("attrs", {})
        # 忽略type
        # note_type = attrs.get("type", "info")
        
        # 处理注释内容
        return self._process_content(content)
    
    def _handle_note_title(self, node: Dict) -> str:
        """处理注释标题节点"""
        content = node.get("content", [])
        
        # 处理注释标题内容
        title_content = self._process_content(content)
        
        return f"**{title_content}**\n"
    
    def _handle_note_content(self, node: Dict) -> str:
        """处理注释内容节点"""
        content = node.get("content", [])
        
        # 处理注释内容
        note_content = self._process_content(content)
        
        return note_content
    
    def _handle_markdown(self, node: Dict) -> str:
        """处理Markdown节点"""
        attrs = node.get("attrs", {})
        content = attrs.get("content", "")
        
        # 直接返回Markdown内容
        return f"\n{content}\n\n"
    
    def _handle_html(self, node: Dict) -> str:
        """处理HTML节点"""
        attrs = node.get("attrs", {})
        content = attrs.get("content", "")
        
        # 将HTML包装在代码块中
        return f"\n```html\n{content}\n```\n\n"
    
    def _handle_attachment(self, node: Dict) -> str:
        """处理附件节点"""
        attrs = node.get("attrs", {})
        name = attrs.get("name", "")
        src = attrs.get("src", "")
        
        return f"[📎 {name}]({src})\n\n"
    
    def _handle_audio(self, node: Dict) -> str:
        """处理音频节点"""
        attrs = node.get("attrs", {})
        name = attrs.get("name", "")
        url = attrs.get("url", "")
        
        return f"[🔊 {name}]({url})\n\n"
    
    def _handle_video(self, node: Dict) -> str:
        """处理视频节点"""
        attrs = node.get("attrs", {})
        name = attrs.get("name", "")
        url = attrs.get("url", "")
        
        return f"[🎬 {name}]({url})\n\n"
    
    def _handle_plantuml(self, node: Dict) -> str:
        """处理PlantUML节点"""
        attrs = node.get("attrs", {})
        content = attrs.get("content", "")
        
        return f"\n```plantuml\n{content}\n```\n\n"
    
    def _handle_drawio(self, node: Dict) -> str:
        """处理DrawIO图表节点"""
        attrs = node.get("attrs", {})
        src = attrs.get("src", "")
        draw_svg = self._get_remote_content(src, "drawio")
        if draw_svg:
            mermaid_content =  convert_drawio_to_mermaid(draw_svg)
            return f"```mermaid\n %% convert from drawio: {src} \n{mermaid_content}\n```\n\n"
        else:
            return f"[DrawIO Diagram: {src}]\\n\\n" if src else "[DrawIO Diagram]\\n\\n"
    
    def _handle_minder(self, node: Dict) -> str:
        """处理嵌入式SVG思维导图 (Minder) 节点，转换为Mermaid格式"""
        attrs = node.get("attrs", {})
        svg_src = attrs.get("src") 
        svg_content = self._get_remote_content(svg_src, "minder") 

        if svg_content:
            logger.info("Processing embedded SVG minder content.")
            return convert_minder_to_plantuml(svg_content) 
        else:
            logger.warning("Minder node found, but no SVG content or source attribute.")
            return "[Minder Diagram - No SVG data found]"
    
    def _handle_unknown(self, node: Dict) -> str:
        """处理未知类型的节点"""
        node_type = node.get("type", "unknown")
        content = node.get("content", [])
        
        # 尝试处理内容
        if content:
            return self._process_content(content)
            
        return ""


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Convert KM JSON to Markdown")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("output", help="Output Markdown file path")
    
    args = parser.parse_args()
    
    # 读取输入文件
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            json_content = json.load(f)
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return
    
    # 转换为Markdown
    converter = KM2MD()
    markdown_content = converter.convert(json_content)
    
    # 输出结果
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"Markdown saved to {args.output}")
    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return
    
    logger.debug(markdown_content)


if __name__ == "__main__":
    main()