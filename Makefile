# 專案名稱與輸出路徑
BINARY_NAME=server
CMD_DIR=cmd/server
BIN_DIR=bin

# 預設目標
.PHONY: all
all: build

# 編譯 Go 程式
.PHONY: build
build:
	@echo "🚀 Building Go server..."
	@mkdir -p $(BIN_DIR)
	go build -o $(BIN_DIR)/$(BINARY_NAME) ./$(CMD_DIR)

# 啟動 Go server
.PHONY: run
run: build
	@echo "🏃 Running Go server..."
	./$(BIN_DIR)/$(BINARY_NAME)

# 執行 Python 測試 (範例: search-code 模組)
.PHONY: test-python
test-python:
	@echo "🐍 Running Python tests..."
	python3 internal/sample/search-code/search_code.py  internal/sample/search-code/mixed_log.txt --window 5 --threshold 3 --maxlen 15 --maxblank 2 --minlines 2 --top 2

# 清理編譯檔與暫存
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(BIN_DIR)
	find . -name '__pycache__' -type d -exec rm -rf {} +

# 幫助訊息
.PHONY: help
help:
	@echo "可用指令:"
	@echo "  make build        - 編譯 Go server"
	@echo "  make run          - 編譯並啟動 Go server"
	@echo "  make test-python  - 執行 Python 測試程式"
	@echo "  make clean        - 清除編譯檔與暫存資料"
