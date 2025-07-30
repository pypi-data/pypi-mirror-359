# 配置日志
import os
from utils.logger import get_logger


logger = get_logger()

def get_appkey_match_threshold() -> float:
    threshold = os.getenv("APPKEY_MATCH_THRESHOLD", "0.6")
    try:
        value = float(threshold)
        if value < 0 or value > 1:
            return 0.6
        return value
    except Exception as e:
        logger.error(f"APPKEY_MATCH_THRESHOLD 配置错误: {e}")
        return 0.6

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    计算两个字符串的编辑距离
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def is_acceptable_typo(pattern: str, target: str) -> bool:
    """
    判断是否为可接受的拼写错误
    1. 允许单个字母的替换、增加或删除（位置不限）
    2. 允许相邻字母的交换
    3. 不允许数字或特殊字符的替换
    4. 不允许多个字符的变化

    Args:
        pattern: 模式串
        target: 目标串

    Returns:
        bool: 是否为可接受的拼写错误
    """
    if pattern == target:
        return True
        
    # 长度差距过大
    if abs(len(pattern) - len(target)) > 1:
        return False
    
    # 检查是否包含数字
    if any(c.isdigit() for c in pattern) or any(c.isdigit() for c in target):
        return False
    
    # 长度相等的情况
    if len(pattern) == len(target):
        # 找出所有不同的位置
        diff_positions = [(i, p, t) for i, (p, t) in enumerate(zip(pattern, target)) if p != t]
        
        # 如果只有一个字符不同，检查是否都是字母
        if len(diff_positions) == 1:
            _, c1, c2 = diff_positions[0]
            return c1.isalpha() and c2.isalpha()
            
        # 如果是两个相邻位置的字符交换，检查是否都是字母
        if len(diff_positions) == 2:
            pos1, c1, c2 = diff_positions[0]
            pos2, c3, c4 = diff_positions[1]
            # 检查是否都是字母
            if not all(c.isalpha() for c in [c1, c2, c3, c4]):
                return False
            # 相邻位置
            if abs(pos1 - pos2) == 1:
                # 交叉匹配
                if c1 == c4 and c2 == c3:
                    return True
        
        return False
    
    # 长度差1的情况，允许在任意位置插入或删除一个字母
    if len(pattern) < len(target):
        shorter, longer = pattern, target
    else:
        shorter, longer = target, pattern
        
    # 检查是否可以通过插入一个字母得到longer
    for i in range(len(longer)):
        if longer[:i] + longer[i+1:] == shorter:
            # 检查被插入/删除的字符是否为字母
            extra_char = longer[i]
            if not extra_char.isalpha():
                return False
            return True
            
    return False

def match_appkey(pattern: str, appkey: str) -> bool:
    """
    匹配appkey，采用从后向前的渐进式匹配策略：
    1. 完全匹配
    2. 后缀完全匹配：对pattern按.分割，从后向前匹配
    3. 滑动窗口匹配：对较长pattern(>=3个词)，使用滑动窗口进行匹配
    4. 模糊匹配：对最后N个部分进行相似度匹配，容忍轻微的拼写错误

    Args:
        pattern: 匹配模式
        appkey: 待匹配的appkey

    Returns:
        bool: 是否匹配成功
    """
    if not pattern or not appkey:
        return bool(not pattern)

    # 预处理：统一分隔符为点号
    pattern_lower = pattern.lower().replace('_', '.')
    appkey_lower = appkey.lower().replace('_', '.')
    
    # 1. 完全匹配
    if pattern_lower == appkey_lower:
        return True
    
    # 获取appkey的各个部分
    appkey_parts = appkey_lower.split('.')
    pattern_parts = pattern_lower.split('.')
    
    if not appkey_parts:
        return False

    # 2. 后缀完全匹配
    pattern_len = len(pattern_parts)
    appkey_len = len(appkey_parts)
    
    # 如果pattern比appkey还长，直接返回False
    if pattern_len > appkey_len:
        return False
        
    # 从后向前完全匹配
    if pattern_len <= 3:  # 对于较短的pattern，直接从后向前匹配
        if appkey_lower.endswith(pattern_lower):
            return True
        # 检查最后N个部分是否完全匹配
        if pattern_parts == appkey_parts[-pattern_len:]:
            return True
    
    # 3. 滑动窗口匹配（适用于较长的pattern）
    if pattern_len >= 3:
        window_size = pattern_len
        for i in range(len(appkey_parts) - window_size + 1):
            window = appkey_parts[i:i + window_size]
            if '.'.join(window) == pattern_lower:
                return True
    
    # 4. 模糊匹配
    # 对最后1-2个部分进行相似度匹配
    last_parts_to_check = min(2, pattern_len, appkey_len)
    for i in range(1, last_parts_to_check + 1):
        pattern_suffix = '.'.join(pattern_parts[-i:])
        appkey_suffix = '.'.join(appkey_parts[-i:])
        
        # 对于每个部分单独进行匹配
        pattern_parts_to_check = pattern_suffix.split('.')
        appkey_parts_to_check = appkey_suffix.split('.')
        
        all_parts_match = True
        for p_part, a_part in zip(pattern_parts_to_check, appkey_parts_to_check):
            if not is_acceptable_typo(p_part, a_part):
                all_parts_match = False
                break
        
        if all_parts_match:
            return True
    
    return False

