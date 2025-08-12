from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import jwt, os

app = FastAPI()

SECRET_KEY = "super-secret-download-key"
FILE_BASE_PATH = "/mnt/nfs_storage/files"

@app.get("/download")
def download(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    file_id = payload["file_id"]
    user_id = payload["user_id"]

    file_path = os.path.join(FILE_BASE_PATH, f"{file_id}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/octet-stream", filename=f"{file_id}.pdf")
