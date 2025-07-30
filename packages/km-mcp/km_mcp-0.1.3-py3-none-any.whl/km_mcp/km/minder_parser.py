import xml.etree.ElementTree as ET
import json
from urllib.parse import unquote
import base64
from ..utils.logger import get_logger

logger = get_logger()

def _extract_minder_json_from_svg(svg_content: str) -> dict:
    """
    解析 SVG 文件，提取 <svg> 标签 content 属性中的 URL 编码 JSON 数据。

    Args:
        file_path: SVG 文件的路径。

    Returns:
        解析后的 JSON 数据 (dict)，如果解析失败则返回 None。
    """
    try:
        # 解析 SVG 内容
        root = ET.fromstring(svg_content)

        # 检查根元素是否为 svg
        if not root.tag.endswith('svg'):
             # 有时 etree 会包含命名空间，例如 {http://www.w3.org/2000/svg}svg
            logger.error(f"错误：文件的根元素不是 <svg> 标签。找到的标签是: {root.tag}")
            return None

        # 获取 content 属性
        content_encoded = root.get('content')
        if content_encoded is None:
            logger.error("错误：<svg> 标签中未找到 'content' 属性。")
            return None
        content_decoded = base64.b64decode(content_encoded).decode('utf-8')
        # URL 解码
        content_decoded = unquote(content_decoded)

        # 解析 JSON
        json_data = json.loads(content_decoded)
        return json_data

    except ET.ParseError:
        logger.error(f"错误：解析 SVG 文件失败 - {svg_content}")
        return None
    except json.JSONDecodeError:
        logger.error("错误：解码后的 'content' 属性不是有效的 JSON 格式。")
        return None
    except Exception as e:
        logger.error(f"发生未知错误：{e}")
        return None

def _decode_text(encoded_text: str) -> str:
    """解码 Minder JSON 中的 URL 编码文本。"""
    # 替换 %uXXXX 格式为 \\uXXXX 以便 Python 解码
    encoded_text = encoded_text.replace('%u', r'\u')
    # 使用 'unicode_escape' 解码
    return encoded_text.encode('ascii').decode('unicode_escape')

def _generate_plantuml_recursive(node: dict, level: int) -> str:
    """递归生成 PlantUML 思维导图节点字符串。"""
    plantuml_str = ""
    if node and 'data' in node and 'text' in node['data']:
        # 解码文本
        text = _decode_text(node['data']['text'])
        # 生成当前节点的 PlantUML 行
        plantuml_str += f"{'*' * level} {text}\\n"

        # 递归处理子节点
        if 'children' in node and node['children']:
            for child in node['children']:
                plantuml_str += _generate_plantuml_recursive(child, level + 1)
    return plantuml_str

def _convert_minder_json_to_plantuml(minder_json: dict) -> str:
    """
    将 Minder JSON 数据转换为 PlantUML 思维导图格式。

    Args:
        minder_json: 解析后的 Minder JSON 数据 (dict)。

    Returns:
        PlantUML 格式的字符串。
    """
    if not minder_json or 'root' not in minder_json:
        return ""

    root_node = minder_json['root']
    plantuml_body = _generate_plantuml_recursive(root_node, 1)

    # 添加 PlantUML 头尾
    return f"```plantuml\\n@startmindmap\\n{plantuml_body}@endmindmap\\n```"

def convert_minder_to_plantuml(svg_content: str) -> str:
    try:
        minder_json = _extract_minder_json_from_svg(svg_content)
        if not minder_json:
            return ""
        return _convert_minder_json_to_plantuml(minder_json)
    except Exception as e:
        logger.error(f"minder 转换为 plantuml 过程中发生错误: {e}")
        return ""

if __name__ == "__main__":
    encoded_str = "%u5206%u652F%u4E3B%u9898"
    decoded_str = encoded_str.encode('utf-8').decode('unicode_escape')
    logger.info(decoded_str)  # 输出：分支主题
    # --- 示例用法 ---
    svg_file = 'km/minder.svg'
    with open(svg_file, 'r', encoding='utf-8') as file:
        svg_content = file.read()
    minder_data = _extract_minder_json_from_svg(svg_content)

    if minder_data:
        print("原始 Minder JSON 数据:")
        print(json.dumps(minder_data, indent=2, ensure_ascii=False))
        print("\\n" + "="*30 + "\\n")

        print("转换后的 PlantUML 数据:")
        plantuml_output = _convert_minder_json_to_plantuml(minder_data)
        print(plantuml_output)
