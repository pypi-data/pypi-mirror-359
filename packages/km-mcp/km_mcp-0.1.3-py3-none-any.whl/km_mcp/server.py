from dataclasses import dataclass
import os
from bs4 import BeautifulSoup
import html2text
from mcp.server.fastmcp import FastMCP, Image
from .km import KM2MD
from .sso import MeituanRequests
from .utils.logger import get_logger

# 配置日志
logger = get_logger()

meituan_requests = MeituanRequests()
mcp = FastMCP("km-doc-server")


@dataclass
class KmSearchResult:
    title:str
    content_summmary:str
    km_doc_id:str
    doc_link:str

def get_km_doc_by_id(doc_id: str) -> str:
    api_url = f"https://km.sankuai.com/api/pages/new/{doc_id}?queryType=0"
    response = meituan_requests.get(api_url)
    doc_json = response.json()  
    return doc_json

def get_max_secret_level_threshold() -> int:
    threshold = os.getenv("MAX_SECRET_LEVEL_THRESHOLD", "2")
    return int(threshold) if threshold.isdigit() else 2

def is_filter_secret_level_in_search_result() -> bool:
    filter_secret_level = os.getenv("FILTER_SECRET_LEVEL_IN_SEARCH_RESULT", "1")
    return filter_secret_level == "1"

@mcp.tool()
async def get_km_doc(doc_id: str, doc_title: str = "", doc_link: str = "", convert_to_md: bool = True) -> str:
    """
    Get the content of a Meituan internal document (WIKI or 学城) by its ID.
    
    The document can be accessed through URLs in these formats:
    - https://km.sankuai.com/collabpage/<doc_id>
    - https://km.sankuai.com/page/<doc_id>
    
    Args:
        doc_id: Document ID, a unique identifier for the document
        doc_title: Optional. Title of the document, used for display purposes
        doc_link: Optional. HTTP link to the document, used for reference display in format: [doc_title](doc_link)
        convert_to_md: Optional. Whether to convert the content to Markdown format, defaults to True
    
    Returns:
        str: Document content in markdown format if convert_to_md is True, otherwise in original json format.
            If an error occurs, returns an error message string.
    
    Error Handling:
        - Returns error message if document's secret level exceeds threshold
        - Returns error message if document retrieval fails
        - Returns error message if document format conversion fails
    """
    try:
        logger.info(f"获取文档: {doc_id}")
        doc_json = get_km_doc_by_id(doc_id)
        threshold = get_max_secret_level_threshold()
        secret_level = doc_json.get("data", {}).get("secretLevel", 0)
        if secret_level > threshold:
            return f"文档{doc_id}的密级为C{secret_level}，超过阈值{threshold}，无法访问"
        body = doc_json.get('data', {}).get('body', {})
        # 检查body是否为字符串
        if isinstance(body, str):
            is_json = body.startswith('{')
            if is_json:
                if convert_to_md:
                    # 转换为Markdown格式
                    content = KM2MD().convert(body)
                else:
                    content = body
            else:
                soup = BeautifulSoup(body, 'html.parser')
                content = html2text.html2text(str(soup))
        else:
            # 如果body是字典，直接转换为JSON字符串
            if convert_to_md:
                content = KM2MD().convert(str(body))
            else:
                content = str(body)
        return content
        
    except Exception as e:
        logger.error(f"获取文档失败: {doc_id}，错误信息：{str(e)}")
        return f"获取文档失败，错误信息：{str(e)}"
    
    
@mcp.tool()
async def search_km(keyword: str, limit: int = 30, offset: int = 0) -> str:
    """
    Search for Meituan internal documents (WIKI or 学城) using keywords.
    
    This function searches through the Meituan Knowledge Management system and returns
    a list of relevant documents based on the search keyword. The results can be
    filtered by document security level and paginated using limit and offset. 
    
    Document HTTP link format: https://km.sankuai.com/page/<km_doc_id>, 
    which can be used as a reference shown to the user in the format: [doc_title](http://km.
    sankuai.com/page/<km_doc_id>)
    
    Args:
        keyword: Search keyword to find relevant documents
        limit: Optional. Maximum number of documents to return, defaults to 30
        offset: Optional. Number of documents to skip for pagination, defaults to 0
    
    Returns:
        str: Formatted search results containing:
            - Document title and ID
            - HTTP link to the document in format: https://km.sankuai.com/page/<km_doc_id>
            - Brief summary or highlight of the document content
            - Total number of results found
    
    Error Handling:
        - Returns error message if search fails
        - Filters out documents with security level above threshold
        - Returns empty list if no matching documents found
    
    Note:
        The search is performed in public space by default. This can be configured
        using the KM_SEARCH_SPACE_TYPE environment variable (0 for public, 1 for private).
    """
    try:
        
        # 构建API URL
        # spaceType=1表示个人空间,spaceType=0表示公共空间 ,默认是公共空间
        space_type = os.getenv("KM_SEARCH_SPACE_TYPE", "0")
        api_url = f"https://km.sankuai.com//api/citadelsearch/content?keyword={keyword}&offset={offset}&limit={limit}&refreshFlag=1&spaceType={space_type}"
        
        # 发起请求
        response = meituan_requests.get(api_url)
        doc_json = response.json()
        page_list = doc_json.get('data', {}).get('models', [])
        search_result = []
        if page_list:
            for p in page_list:
                km_doc_id=p.get("contentId")
                title = p.get("title", "")
                #过滤密级大于阈值的文档
                if is_filter_secret_level_in_search_result():
                    doc_json = get_km_doc_by_id(km_doc_id)
                    secret_level = doc_json.get("data", {}).get("secretLevel", 0)
                    if secret_level > get_max_secret_level_threshold():
                        logger.info(f"文档{km_doc_id} [{title}] 的密级为C{secret_level}，超过阈值，已过滤")
                        continue
                search_result.append( KmSearchResult(
                    km_doc_id=km_doc_id,
                    title = title, 
                    content_summmary=p.get("contentBody_hl", ""),
                    doc_link= f"https://km.sankuai.com/page/{km_doc_id}"
                ))
        # 格式化搜索结果为字符串
        if not search_result:
            return f"未找到关键字 '{keyword}' 相关的文档"
        
        result_text = f"找到 {len(search_result)} 个相关文档：\n\n"
        for i, result in enumerate(search_result, 1):
            result_text += f"{i}. **{result.title}**\n"
            result_text += f"   - 文档ID: {result.km_doc_id}\n"
            result_text += f"   - 链接: [{result.title}]({result.doc_link})\n"
            if result.content_summmary:
                # 清理HTML标签
                summary = result.content_summmary.replace('<em>', '**').replace('</em>', '**')
                result_text += f"   - 摘要: {summary}\n"
            result_text += "\n"
        
        return result_text
    except Exception as e:
        logger.error(f"搜索学城文档失败，关键字：{keyword}，错误信息：{str(e)}")
        return f"搜索学城文档失败，关键字：{keyword}，错误信息：{str(e)}"
    

def _process_image_content(response, img_format, compression_level):
    """
    处理图片内容，包括压缩和格式转换。
    """
    try:
        from io import BytesIO
        from PIL import Image as PILImage
        img = PILImage.open(BytesIO(response.content))
        output = BytesIO()
        # 根据压缩级别调整参数
        if compression_level == 1:
            quality = 85
            max_size = (1600, 1600)
        elif compression_level == 2:
            quality = 70
            max_size = (1024, 1024)
        else:  # compression_level >= 3
            quality = 50
            max_size = (640, 640)
        # 缩放图片
        img.thumbnail(max_size, PILImage.LANCZOS)
        # 只对JPEG/WEBP等有损格式设置quality
        if img_format.upper() in ["JPEG", "JPG", "WEBP"]:
            img.save(output, format=img_format, quality=quality, optimize=True)
        else:
            img.save(output, format=img_format)
        output.seek(0)
        return Image(data=output.read(), format=img_format.lower())
    except Exception as e:
        logger.warning(f"图片压缩失败，返回原图，错误: {str(e)}")
        return Image(data=response.content, format=img_format.lower())

def _process_svg_content(svg_content, trim_svg, compression_level):
    """
    处理SVG内容，包括压缩和优化。
    """
    original_content = svg_content
    if not trim_svg:
        return svg_content
    try:
        from bs4 import BeautifulSoup, Comment
        import re
        # 压缩级别0: 不进行任何压缩
        if compression_level == 0:
            return svg_content
        soup = BeautifulSoup(svg_content, 'lxml-xml')
        # 压缩级别1: 轻度压缩
        if compression_level >= 1:
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            for script in soup.find_all('script'):
                script.extract()
            for style in soup.find_all('style'):
                style.extract()
            svg_root = soup.find('svg')
            if svg_root and svg_root.has_attr('content'):
                content_attr = svg_root['content']
                if '&lt;mxfile' in content_attr:
                    simplified_content = re.sub(r'(&lt;mxfile.*?)&gt;.*?(&lt;/mxfile&gt;)',
                                               r'\1&gt;...&lt;/mxfile&gt;',
                                               content_attr)
                    svg_root['content'] = simplified_content
        # 压缩级别2: 中度压缩
        if compression_level >= 2:
            for tag in soup.find_all():
                attrs_to_remove = ['style', 'pointer-events', 'font-family',
                                  'stroke-dasharray', 'stroke-miterlimit']
                for attr in attrs_to_remove:
                    if tag.has_attr(attr):
                        del tag[attr]
            for foreign_obj in soup.find_all('foreignObject'):
                text_content = foreign_obj.get_text(strip=True)
                if text_content:
                    new_text = soup.new_tag('text')
                    new_text.string = text_content
                    foreign_obj.replace_with(new_text)
                else:
                    foreign_obj.extract()
        # 压缩级别3: 高度压缩
        if compression_level >= 3:
            for tag in soup.find_all():
                attrs_to_remove = ['stroke-width', 'fill-opacity', 'stroke-opacity',
                                  'opacity', 'rx', 'ry']
                for attr in attrs_to_remove:
                    if tag.has_attr(attr):
                        del tag[attr]
            simple_g_tags = []
            for g in soup.find_all('g'):
                if len(list(g.children)) == 1 and not g.get('transform'):
                    simple_g_tags.append(g)
            for g in simple_g_tags:
                child = list(g.children)[0]
                if hasattr(child, 'name'):
                    g.replace_with(child)
        if compression_level >= 2:
            svg_root = soup.find('svg')
            if svg_root:
                required_attrs = ['xmlns', 'width', 'height', 'viewBox']
                for attr in list(svg_root.attrs.keys()):
                    if attr not in required_attrs and attr != 'content':
                        del svg_root[attr]
                if not soup.find('rect', attrs={'width': '100%', 'height': '100%', 'fill': '#ffffff'}):
                    background = soup.new_tag('rect')
                    background['fill'] = '#ffffff'
                    background['width'] = '100%'
                    background['height'] = '100%'
                    background['x'] = '0'
                    background['y'] = '0'
                    children = list(svg_root.children)
                    if children:
                        svg_root.insert(0, background)
                    else:
                        svg_root.append(background)
        svg_content = str(soup)
        logger.info(f"SVG压缩完成，压缩级别: {compression_level}, 原始大小: {len(original_content)}，压缩后大小: {len(svg_content)}")
    except Exception as e:
        logger.warning(f"SVG压缩失败，使用原始内容，错误: {str(e)}")
        svg_content = original_content
    return svg_content

@mcp.tool()
async def read_file_content(url: str, compression_level: int = 3):
    """
    When asks about accessing image details or Draw.io diagrams, you can use this tool to access the image details in Meituan (WIKI or 学城) 
    
    This function retrieves SVG OR image content from a DrawIO diagram OR image embedded in a Meituan internal document and optionally processes it for optimization. The content can be compressed at different levels to reduce size while maintaining visual quality.
    
    Args:
        url: DrawIO SVG file OR image URL in format: https://km.sankuai.com/api/file/cdn/<file_id>
        compression_level: Optional. Level of compression to apply (0-3):
            - 0: No compression, original SVG
            - 1: Light compression (removes comments and scripts)
            - 2: Medium compression (removes style attributes)
            - 3: High compression (aggressive optimization, may affect some visual effects)
    
    Returns:
        str: The SVG content as a string. If compression is applied, returns the
            optimized SVG content. If an error occurs, returns an error message.
        Image: The image content. If compression is applied, returns the compressed image content.
    Error Handling:
        - Returns error message if URL is invalid or inaccessible
        - Returns error message if SVG content cannot be parsed
        - Returns original content if compression fails
        - Logs compression statistics when successful
    
    Note:
        Higher compression levels may affect certain visual effects but achieve better
        size reduction. Choose the compression level based on your needs for visual
        quality vs file size.
    """
    try:
        response = meituan_requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            is_image = content_type.startswith("image/")
            img_format = content_type.split("/")[-1].upper() if is_image else ""
            is_svg_xml = 'svg' in img_format.lower() or 'xml' in img_format.lower()
            if is_image and not is_svg_xml:
                return _process_image_content(response, img_format, compression_level)
            else:
                svg_content = response.text
                return _process_svg_content(svg_content, True, compression_level)
        else:
            return f"读取学城文档内容失败，错误信息：{response.status_code},url:{url}"
    except Exception as e:
        logger.error(f"读取学城文档内容失败，错误信息：{str(e)}")
        return f"读取学城文档内容失败，错误信息：{str(e)}"
    

def main():
    """Main entry point for the MCP server."""
    print("Starting Meituan KM MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
