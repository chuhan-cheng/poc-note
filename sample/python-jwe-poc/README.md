# How to use JWE in api server
Python JWE 實作範例（使用 jose）


## API SERVER
### Install
```bash
pip install fastapi uvicorn python-jose[cryptography]
```
```python
# config.py
SECRET_KEY = b"this_is_a_32byte_secret_key!!!!"  # 32 bytes for A256GCM
```
```python
# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from jose import jwe
import json, time, random
from config import SECRET_KEY

app = FastAPI()

EDGE_SERVERS = [
    "https://edge1.myserver.com",
    "https://edge2.myserver.com",
    "https://edge3.myserver.com"
]

@app.get("/api/request-download")
def request_download(file_id: str, user_id: str):
    # 🔐 權限驗證略過，這裡假設通過

    payload = {
        "file_id": file_id,
        "user_id": user_id,
        "exp": int(time.time()) + 900  # 15分鐘後過期
    }

    # 使用 JWE 加密 payload
    encrypted_token = jwe.encrypt(
        json.dumps(payload),
        SECRET_KEY,
        algorithm="dir",
        encryption="A256GCM"
    )

    # 分配一個下載節點
    edge_server = random.choice(EDGE_SERVERS)

    download_url = f"{edge_server}/download?token={encrypted_token}"
    return JSONResponse({"download_url": download_url})
```

## Download Server
```python
# download_server.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from jose import jwe
import json, os, time
from config import SECRET_KEY

app = FastAPI()

BASE_PATH = "/mnt/nfs_storage/files"  # 掛載 NFS 的路徑

@app.get("/download")
def download(token: str):
    try:
        decrypted = jwe.decrypt(token, SECRET_KEY)
        payload = json.loads(decrypted)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or malformed token")

    # 驗證過期時間
    if time.time() > payload["exp"]:
        raise HTTPException(status_code=401, detail="Token expired")

    file_id = payload["file_id"]
    user_id = payload["user_id"]  # 若需額外權限驗證，可加入

    file_path = os.path.join(BASE_PATH, f"{file_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=f"{file_id}.pdf"
    )
```

## Testing
### Download
```pgsql
GET http://api-server.local/api/request-download?file_id=abc123&user_id=u456
```
response
```json
{
  "download_url": "https://edge2.myserver.com/download?token=eyJhbGciOiAiZGlyIiwg..."
}
```
