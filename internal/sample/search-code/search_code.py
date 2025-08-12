import re
import json
from collections import deque

# 關鍵字定義
KEYWORDS = {
    'c': {'int', 'char', 'if', 'else', 'for', 'while', 'return', 'printf', '#include'},
    'cpp': {'std', 'cout', 'cin', 'class', 'public', 'private', 'template', '::', '->'},
    'java': {'public', 'class', 'static', 'void', 'String', 'System', 'new', 'return'}
}
ALL_KEYWORDS = set().union(*KEYWORDS.values())
keyword_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in ALL_KEYWORDS) + r')\b')

def extract_code_segments(file_path,
                          window_size=5,
                          keyword_threshold=3,
                          max_segment_length=20,
                          max_blank_lines=2,
                          min_keyword_lines=2,
                          top_n=0):
    """
    從混合 log 檔中擷取出疑似程式碼區塊，依關鍵字密度排序。

    Args:
        file_path (str): 檔案路徑
        window_size (int): 關鍵字視窗大小（行數）
        keyword_threshold (int): 視窗內最小關鍵字數量
        max_segment_length (int): 擷取區塊最大長度
        max_blank_lines (int): 區塊中允許最多空白行（無關鍵字）
        min_keyword_lines (int): 區塊內需有幾行含關鍵字
        top_n (int): 回傳前 N 個區段（依關鍵字數排序），0 為全部

    Returns:
        List[Dict]: 每段區塊資訊，包含 start_line, end_line, lines
    """
    segments = []
    buffer = deque()
    keyword_buffer = deque()
    line_num = 0
    file = open(file_path, 'r', encoding='utf-8')

    def flush_segment(start_line, segment_lines, keyword_counts):
        keyword_line_count = sum(1 for k in keyword_counts if k > 0)
        keyword_total = sum(keyword_counts)
        if keyword_line_count >= min_keyword_lines:
            segments.append({
                "start_line": start_line,
                "end_line": start_line + len(segment_lines) - 1,
                "lines": [line.rstrip('\n') for line in segment_lines],
                "keyword_hits": keyword_total
            })

    try:
        while True:
            line = file.readline()
            if not line:
                break
            line_num += 1

            buffer.append(line)
            count = len(keyword_pattern.findall(line))
            keyword_buffer.append(count)

            if len(buffer) < window_size:
                continue

            window_sum = sum(list(keyword_buffer)[-window_size:])
            if window_sum >= keyword_threshold:
                segment_lines = list(buffer)
                segment_keywords = list(keyword_buffer)
                blank_count = 0
                segment_start = line_num - len(buffer) + 1

                while len(segment_lines) < max_segment_length:
                    next_line = file.readline()
                    if not next_line:
                        break
                    line_num += 1
                    kcount = len(keyword_pattern.findall(next_line))

                    segment_lines.append(next_line)
                    segment_keywords.append(kcount)

                    if kcount > 0:
                        blank_count = 0
                    else:
                        blank_count += 1
                        if blank_count >= max_blank_lines:
                            break

                flush_segment(segment_start, segment_lines, segment_keywords)

                buffer.clear()
                keyword_buffer.clear()
            else:
                buffer.popleft()
                keyword_buffer.popleft()
    finally:
        file.close()

    # 排序與擷取前 N 段
    segments.sort(key=lambda seg: seg["keyword_hits"], reverse=True)
    if top_n > 0:
        segments = segments[:top_n]

    for seg in segments:
        del seg["keyword_hits"]

    return segments

# =============================
# CLI 模式
# =============================
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract code-like segments from a mixed log file (streaming).")
    parser.add_argument("file", help="Path to the input log file.")
    parser.add_argument("--window", type=int, default=5, help="Window size (number of lines).")
    parser.add_argument("--threshold", type=int, default=3, help="Minimum keyword hits per window.")
    parser.add_argument("--maxlen", type=int, default=20, help="Maximum lines per segment.")
    parser.add_argument("--maxblank", type=int, default=2, help="Max consecutive non-keyword lines in segment.")
    parser.add_argument("--minlines", type=int, default=2, help="Min keyword-containing lines in segment.")
    parser.add_argument("--top", type=int, default=0, help="Return only top N segments sorted by keyword count.")
    args = parser.parse_args()

    result = extract_code_segments(
        file_path=args.file,
        window_size=args.window,
        keyword_threshold=args.threshold,
        max_segment_length=args.maxlen,
        max_blank_lines=args.maxblank,
        min_keyword_lines=args.minlines,
        top_n=args.top
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
