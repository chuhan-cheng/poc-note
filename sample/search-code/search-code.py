import re

# 模擬關鍵字清單（你可以從檔案或資料庫讀取）
KEYWORDS = {
    'c': {'int', 'char', 'if', 'else', 'for', 'while', 'return', 'printf', '#include'},
    'cpp': {'std', 'cout', 'cin', 'class', 'public', 'private', 'template', '::', '->'},
    'java': {'public', 'class', 'static', 'void', 'String', 'System', 'new', 'return'}
}

# 合併所有語言的關鍵字（視情況也可以分開處理）
ALL_KEYWORDS = set().union(*KEYWORDS.values())

# 預編譯正則表達式，提高效能
keyword_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in ALL_KEYWORDS) + r')\b')

def find_code_segments(file_path, window_size=5, keyword_threshold=3):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    keyword_counts = [len(keyword_pattern.findall(line)) for line in lines]

    # 找出滑動視窗中總和超過閾值的區段
    segments = []
    i = 0
    while i < len(lines) - window_size + 1:
        window_sum = sum(keyword_counts[i:i+window_size])
        if window_sum >= keyword_threshold:
            # 擷取整個視窗
            segment = lines[i:i+window_size]
            segments.append(('Start line ' + str(i+1), segment))
            i += window_size  # 跳過已擷取的區段，避免重複
        else:
            i += 1

    return segments

# 範例使用
if __name__ == '__main__':
    log_file = 'mixed_log.txt'  # 你的 log 檔
    segments = find_code_segments(log_file)

    for label, segment in segments:
        print(label)
        print(''.join(segment))
        print('-' * 40)
