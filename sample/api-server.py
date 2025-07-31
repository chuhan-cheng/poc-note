from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt, time, random

app = FastAPI()

SECRET_KEY = "super-secret-download-key"

EDGE_SERVERS = [
    "https://edge1.myserver.com",
    "https://edge2.myserver.com",
    "https://edge3.myserver.com"
]

# GET /api/request-download?file_id=abc123&user_id=456
@app.get("/api/request-download")
def request_download(file_id: str, user_id: str):
    # ✅ 驗證 user 是否有權限下載該 file_id（略，假設有權限）

    # 隨機挑一個 download node，或根據 user_id 做 consistent hash
    selected_edge = random.choice(EDGE_SERVERS)

    # 產生下載 token（15 分鐘過期）
    payload = {
        "file_id": file_id,
        "user_id": user_id,
        "exp": int(time.time()) + 900,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # 回傳下載連結
    download_url = f"{selected_edge}/download?token={token}"

    '''
    {
    "download_url": "https://edge2.myserver.com/download?token=eyJhbGciOiJIUzI1..."
    }
    '''
    return JSONResponse({"download_url": download_url})
