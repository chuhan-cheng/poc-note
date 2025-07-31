from search_code import extract_code_segments

segments = extract_code_segments("mixed_log.txt", top_n=5)
for seg in segments:
    print(f"{seg['start_line']}~{seg['end_line']}")
    print("\n".join(seg['lines']))
    print("=" * 40)
