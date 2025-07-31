# Introduction
Search code within the file.

##
| 參數                  | 說明                          |
| ------------------- | --------------------------- |
| `window_size`       | 要評估的行數視窗寬度（例如 5 表示連續5行）     |
| `keyword_threshold` | 若滑動視窗內出現關鍵字總數 >= 此值，則視為異常區段 |
| `ALL_KEYWORDS`      | 根據你要偵測的語言類型進行調整             |

## Usage
```bash
python3 search-code.py mixed_log.txt --window 5 --threshold 3 --maxlen 15 --maxblank 2 --minlines 2 --top 2
```