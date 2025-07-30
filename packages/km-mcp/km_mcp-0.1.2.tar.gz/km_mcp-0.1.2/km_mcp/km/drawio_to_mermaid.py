from typing import List, Optional, Dict, Any
import re
from utils.logger import get_logger
logger = get_logger()

class DrawioToMermaid:
    """DrawIO SVG格式转换为Mermaid格式的转换器"""
    
    @staticmethod
    def _parse_dimension(value: str) -> float:
        """
        解析维度值，处理百分比和其他单位
        
        Args:
            value: 维度值字符串，可能包含单位如%
            
        Returns:
            float: 解析后的浮点数值
        """
        if not value:
            return 0.0
        
        # 去除百分比符号
        if value.endswith('%'):
            # 对于百分比，暂时返回数值部分/100
            return float(value[:-1]) / 100
        
        # 移除其他可能的单位（px等）
        value = re.sub(r'[a-zA-Z]+$', '', value)
        
        return float(value)
    
    @staticmethod
    def _extract_shapes_text_pairs(svg_content: str) -> list:
        """
        从DrawIO SVG中提取各种形状（矩形、菱形、椭圆形）及其对应的文本
        
        Args:
            svg_content: SVG格式的内容
            
        Returns:
            list: 包含各种形状和文本的对象列表
        """
        results = []
        shape_idx = 0
        
        # 查找所有的矩形元素
        rect_pattern = r'<g>.*?<rect\s+x="([^"]*)".*?y="([^"]*)".*?width="([^"]*)".*?height="([^"]*)".*?></g>'
        rect_matches = re.finditer(rect_pattern, svg_content, re.DOTALL)
        
        for rect_match in rect_matches:
            rect_x = DrawioToMermaid._parse_dimension(rect_match.group(1))
            rect_y = DrawioToMermaid._parse_dimension(rect_match.group(2))
            rect_width = DrawioToMermaid._parse_dimension(rect_match.group(3))
            rect_height = DrawioToMermaid._parse_dimension(rect_match.group(4))
            
            # 计算矩形的中心点
            center_x = rect_x + rect_width / 2
            center_y = rect_y + rect_height / 2
            
            text_content = DrawioToMermaid._find_associated_text(svg_content, rect_match.end(), center_x, center_y)
            
            # 创建节点对象
            node = {
                'id': f'node_{shape_idx}',
                'type': 'rect',
                'x': center_x,
                'y': center_y,
                'width': rect_width,
                'height': rect_height,
                'text': text_content or f"节点{shape_idx}"
            }
            results.append(node)
            shape_idx += 1

        # 查找所有的菱形元素
        diamond_pattern = r'<g>.*?<path\s+d="M\s*([\d.]+)\s*([\d.]+)\s*L\s*([\d.]+)\s*([\d.]+)\s*L\s*([\d.]+)\s*([\d.]+)\s*L\s*([\d.]+)\s*([\d.]+)\s*Z".*?></g>'
        diamond_matches = re.finditer(diamond_pattern, svg_content, re.DOTALL)
        
        for diamond_match in diamond_matches:
            # 提取菱形的四个顶点
            x1, y1 = float(diamond_match.group(1)), float(diamond_match.group(2))
            x2, y2 = float(diamond_match.group(3)), float(diamond_match.group(4))
            x3, y3 = float(diamond_match.group(5)), float(diamond_match.group(6))
            x4, y4 = float(diamond_match.group(7)), float(diamond_match.group(8))
            
            # 计算菱形的中心点和尺寸
            center_x = (x1 + x3) / 2
            center_y = (y2 + y4) / 2
            width = abs(x2 - x4)
            height = abs(y1 - y3)
            
            text_content = DrawioToMermaid._find_associated_text(svg_content, diamond_match.end(), center_x, center_y)
            
            node = {
                'id': f'node_{shape_idx}',
                'type': 'diamond',
                'x': center_x,
                'y': center_y,
                'width': width,
                'height': height,
                'text': text_content or f"节点{shape_idx}"
            }
            results.append(node)
            shape_idx += 1
            
        # 查找所有的椭圆形元素
        ellipse_pattern = r'<g>.*?<ellipse\s+cx="([^"]*)".*?cy="([^"]*)".*?rx="([^"]*)".*?ry="([^"]*)".*?></g>'
        ellipse_matches = re.finditer(ellipse_pattern, svg_content, re.DOTALL)
        
        for ellipse_match in ellipse_matches:
            center_x = DrawioToMermaid._parse_dimension(ellipse_match.group(1))
            center_y = DrawioToMermaid._parse_dimension(ellipse_match.group(2))
            rx = DrawioToMermaid._parse_dimension(ellipse_match.group(3))
            ry = DrawioToMermaid._parse_dimension(ellipse_match.group(4))
            
            text_content = DrawioToMermaid._find_associated_text(svg_content, ellipse_match.end(), center_x, center_y)
            
            node = {
                'id': f'node_{shape_idx}',
                'type': 'ellipse',
                'x': center_x,
                'y': center_y,
                'width': rx * 2,
                'height': ry * 2,
                'text': text_content or f"节点{shape_idx}"
            }
            results.append(node)
            shape_idx += 1
            
        return results

    @staticmethod
    def _find_associated_text(svg_content: str, shape_end: int, center_x: float, center_y: float) -> str:
        """
        查找与形状关联的文本
        
        Args:
            svg_content: SVG内容
            shape_end: 形状元素在SVG中的结束位置
            center_x: 形状的中心点x坐标
            center_y: 形状的中心点y坐标
            
        Returns:
            str: 找到的文本内容
        """
        # 在形状后面的一定范围内查找文本
        text_pattern = r'<g>.*?<g\s+transform="translate[^>]*>.*?<switch>.*?<foreignObject[^>]*>.*?<div[^>]*>.*?<div[^>]*>.*?<div[^>]*>(.*?)</div>.*?</foreignObject>.*?</switch>.*?</g>.*?</g>'
        text_matches = re.finditer(text_pattern, svg_content[shape_end:shape_end+500], re.DOTALL)
        
        text_content = ""
        for text_match in text_matches:
            text_content = text_match.group(1)
            # 清理HTML标签
            text_content = re.sub(r'<[^>]+>', '', text_content).strip()
            break  # 只取第一个匹配的文本
        
        # 如果没有找到文本，尝试用不同的方式查找
        if not text_content:
            # 直接在形状后面的一定范围内查找文本
            next_section = svg_content[shape_end:shape_end+1000]
            text_div_pattern = r'<div[^>]*>.*?<div[^>]*>.*?<div[^>]*>(.*?)</div>'
            text_div_match = re.search(text_div_pattern, next_section, re.DOTALL)
            if text_div_match:
                text_content = text_div_match.group(1)
                text_content = re.sub(r'<[^>]+>', '', text_content).strip()
        
        # 仍然没有文本，可能是使用了更复杂的结构
        if not text_content:
            # 查找整个SVG中与当前形状坐标最接近的文本元素
            all_text_pattern = r'<g transform="translate\(([^,]+),([^)]+)\)"[^>]*>.*?<switch>.*?<foreignObject[^>]*>.*?<div[^>]*>.*?<div[^>]*>.*?<div[^>]*>(.*?)</div>'
            all_text_matches = re.finditer(all_text_pattern, svg_content, re.DOTALL)
            
            min_distance = float('inf')
            for text_match in all_text_matches:
                try:
                    tx = DrawioToMermaid._parse_dimension(text_match.group(1))
                    ty = DrawioToMermaid._parse_dimension(text_match.group(2))
                    # 计算距离
                    dist = ((tx - center_x)**2 + (ty - center_y)**2)
                    if dist < min_distance:
                        min_distance = dist
                        match_text = text_match.group(3)
                        text_content = re.sub(r'<[^>]+>', '', match_text).strip()
                except Exception:
                    continue
                    
        return text_content
    
    @staticmethod
    def _extract_text_labels(svg_content: str) -> dict:
        """
        提取SVG中的文本标签
        
        Args:
            svg_content: SVG格式的内容
            
        Returns:
            dict: 文本标签映射，键为近似位置，值为文本内容
        """
        text_labels = {}
        
        # 查找所有foreignObject文本标签
        label_pattern = r'<g[^>]*>\s*<switch[^>]*>\s*<foreignObject[^>]*>\s*<div[^>]*>\s*<div[^>]*>\s*<div[^>]*>(.*?)</div>'
        label_matches = re.finditer(label_pattern, svg_content, re.DOTALL)
        
        for label_match in label_matches:
            # 尝试从其父元素获取位置信息
            label_pos = label_match.start()
            pre_section = svg_content[max(0, label_pos-300):label_pos]
            
            # 查找translate属性以获取位置
            translate_pattern = r'translate\(\s*([\d.-]+)\s*,\s*([\d.-]+)\s*\)'
            translate_match = re.search(translate_pattern, pre_section)
            
            if translate_match:
                x = DrawioToMermaid._parse_dimension(translate_match.group(1))
                y = DrawioToMermaid._parse_dimension(translate_match.group(2))
                
                # 提取文本内容并清理HTML标签
                text_content = label_match.group(1)
                text_content = re.sub(r'<[^>]+>', '', text_content).strip()
                
                if text_content:
                    # 使用坐标作为键存储文本
                    text_labels[(x, y)] = text_content
        
        return text_labels
    
    @staticmethod
    def _extract_nodes_and_connections(svg_content: str) -> tuple[List[Dict], List[Dict]]:
        """
        从SVG内容中提取节点和连接信息
        
        Args:
            svg_content: SVG格式的内容
            
        Returns:
            tuple: (节点列表, 连接列表)
        """
        # 提取各种形状及其文本
        nodes = DrawioToMermaid._extract_shapes_text_pairs(svg_content)
        
        # 提取所有文本标签
        text_labels = DrawioToMermaid._extract_text_labels(svg_content)
        
        connections = []
        
        # 用于检测重复连接
        connection_set = set()
        
        # 提取所有path元素（通常代表连接线）
        # 使用更严格的pattern，仅匹配箭头连接的path
        path_pattern = r'<path\s+d="([^"]*)"[^>]*?pointer-events="stroke"[^>]*?>'
        path_matches = re.finditer(path_pattern, svg_content)
        
        for path in path_matches:
            path_data = path.group(1)
            # 检查是否是一个有效的路径，应该包含M(移动)和L(线)命令
            if 'M' not in path_data or 'L' not in path_data:
                continue
                
            # 提取路径上的点
            points = re.findall(r'[ML]\s*([\d.-]+)\s*([\d.-]+)', path_data)
            if len(points) >= 2:
                start_x, start_y = DrawioToMermaid._parse_dimension(points[0][0]), DrawioToMermaid._parse_dimension(points[0][1])
                end_x, end_y = DrawioToMermaid._parse_dimension(points[-1][0]), DrawioToMermaid._parse_dimension(points[-1][1])
                
                if not nodes:
                    continue
                
                # 找到最近的起点和终点节点
                start_node = min(nodes, key=lambda n: ((n['x'] - start_x) ** 2 + (n['y'] - start_y) ** 2))
                end_node = min(nodes, key=lambda n: ((n['x'] - end_x) ** 2 + (n['y'] - end_y) ** 2))
                
                # 避免自循环和重复连接
                if start_node['id'] == end_node['id']:
                    continue
                
                # 检查是否已经存在这个连接
                connection_key = (start_node['id'], end_node['id'])
                if connection_key in connection_set:
                    continue
                
                # 查找这个连接上的文本标签
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                connection_text = ""
                
                # 查找最接近连接线中点的文本标签
                min_distance = float('inf')
                for (label_x, label_y), label_text in text_labels.items():
                    # 计算标签到连接线中点的距离
                    distance = ((label_x - mid_x) ** 2 + (label_y - mid_y) ** 2) ** 0.5
                    if distance < min_distance and distance < 50:  # 设置一个距离阈值
                        min_distance = distance
                        connection_text = label_text
                
                # 添加连接关系到集合中以防重复
                connection_set.add(connection_key)
                
                # 添加连接
                connections.append({
                    'from': start_node['id'],
                    'to': end_node['id'],
                    'text': connection_text
                })
        
        return nodes, connections
    
    @staticmethod
    def _generate_mermaid_graph(nodes: List[Dict], connections: List[Dict]) -> str:
        """
        生成Mermaid格式的图表代码
        
        Args:
            nodes: 节点列表
            connections: 连接列表
            
        Returns:
            Mermaid格式的图表代码
        """
        mermaid_code = ['graph TD;']
        
        # 添加节点定义
        for node in nodes:
            node_id = node['id']
            node_text = node['text'] or node_id
            shape_type = node.get('type', 'rect')  # 默认为矩形
            
            # 根据形状类型使用不同的Mermaid语法
            if shape_type == 'rect':
                mermaid_code.append(f'    {node_id}["{node_text}"]')
            elif shape_type == 'diamond':
                mermaid_code.append(f'    {node_id}{{{node_text}}}')
            elif shape_type == 'ellipse':
                mermaid_code.append(f'    {node_id}(("{node_text}"))')
        
        # 添加连接定义
        for conn in connections:
            from_node = conn['from']
            to_node = conn['to']
            conn_text = conn['text']
            if conn_text:
                mermaid_code.append(f'    {from_node} -->|{conn_text}| {to_node}')
            else:
                mermaid_code.append(f'    {from_node} --> {to_node}')
        
        return '\n'.join(mermaid_code)
    
    @classmethod
    def convert_from_url(cls, svg_content: str) -> Optional[str]:
        """
        从URL转换DrawIO文件为Mermaid格式
        
        Args:
            svg_content: DrawIO文件的SVG内容
            
        Returns:
            Mermaid格式的图表代码，如果转换失败返回None
        """
        try:
            # 使用DrawIOParser获取SVG内容
            if not svg_content:
                return None
            
            # 提取节点和连接信息
            nodes, connections = cls._extract_nodes_and_connections(svg_content)
            
            # 生成Mermaid代码
            return cls._generate_mermaid_graph(nodes, connections)
            
        except Exception as e:
            logger.error(f"转换失败: {str(e)}")
            return None

def convert_drawio_to_mermaid(svg_content: str) -> Optional[str]:
    """
    将DrawIO文件转换为Mermaid格式的便捷函数
    
    Args:
        svg_content: DrawIO文件的SVG内容
        
    Returns:
        Mermaid格式的图表代码，如果转换失败返回None
    """
    converter = DrawioToMermaid()
    return converter.convert_from_url(svg_content)

# 确保模块级导出
__all__ = ['convert_drawio_to_mermaid'] 