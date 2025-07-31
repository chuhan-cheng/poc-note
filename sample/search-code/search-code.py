import re
import json
import argparse
from collections import deque

# 關鍵字定義
KEYWORDS = {
    'c': {'int', 'char', 'if', 'else', 'for', 'while', 'return', 'printf', '#include'},
    'cpp': {'std', 'cout', 'cin', 'class', 'public', 'private', 'template', '::', '->'},
    'java': {'public', 'class', 'static', 'void', 'String', 'System', 'new', 'return'}
}
ALL_KEYWORDS = set().union(*KEYWORDS.values())
keyword_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in ALL_KEYWORDS) + r')\b')

def find_code_segments_streaming(file_path, window_size=5, keyword_threshold=3,
                                 max_segment_length=20, max_blank_lines=2, min_keyword_lines=2):
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
                # start new segment from current position in buffer
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

                # 清空 buffer，從下一行重新滑動
                buffer.clear()
                keyword_buffer.clear()
            else:
                # 滑動視窗
                buffer.popleft()
                keyword_buffer.popleft()
    finally:
        file.close()

    return segments

def main():
    parser = argparse.ArgumentParser(description="Extract code-like segments from a mixed log file (streaming).")
    parser.add_argument("file", help="Path to the input log file.")
    parser.add_argument("--window", type=int, default=5, help="Window size (number of lines).")
    parser.add_argument("--threshold", type=int, default=3, help="Minimum keyword hits per window.")
    parser.add_argument("--maxlen", type=int, default=20, help="Maximum lines per segment.")
    parser.add_argument("--maxblank", type=int, default=2, help="Max consecutive non-keyword lines in segment.")
    parser.add_argument("--minlines", type=int, default=2, help="Min keyword-containing lines in segment.")
    parser.add_argument("--top", type=int, default=0, help="Return only top N segments sorted by keyword count.")
    args = parser.parse_args()

    segments = find_code_segments_streaming(
        file_path=args.file,
        window_size=args.window,
        keyword_threshold=args.threshold,
        max_segment_length=args.maxlen,
        max_blank_lines=args.maxblank,
        min_keyword_lines=args.minlines
    )

    # 排序與取前 N 筆
    segments.sort(key=lambda seg: seg["keyword_hits"], reverse=True)
    if args.top > 0:
        segments = segments[:args.top]

    # 移除排序欄位再輸出
    for seg in segments:
        del seg["keyword_hits"]

    print(json.dumps(segments, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
