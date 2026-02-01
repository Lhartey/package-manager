import os
import shutil
import logging
import clamd
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
UPLOAD_DIR = "packages"
SECRET_TOKEN = os.getenv("AUTH_TOKEN", "default-insecure-key")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "500000000"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGINS", "*").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to ClamAV scanner
def get_scanner():
    try:
        # Tries to connect via Unix socket (standard on Linux)
        return clamd.ClamdUnixSocket()
    except Exception as e:
        logger.error(f"ClamAV connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Antivirus engine not reachable")

@app.post("/upload")
async def upload_apk(file: UploadFile = File(...), x_token: str = Header(None)):
    # 1. Auth Check
    if x_token != SECRET_TOKEN:
        logger.warning(f"Unauthorized upload attempt")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 2. Basic Extension Check
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="Only .apk files allowed")
    
    # 3. File Size Check
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File size exceeded: {file_size} bytes")
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    # 4. Save to a temporary location for scanning
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. Malware Scan
    cd = get_scanner()
    try:
        scan_result = cd.scan(os.path.abspath(temp_path))
    except Exception as e:
        os.remove(temp_path)
        logger.error(f"Scan failed for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Malware scan failed")
    
    # Result format: {'/path/to/file': ('FOUND', 'VirusName')} or None
    if scan_result and os.path.abspath(temp_path) in scan_result:
        status_tuple = scan_result[os.path.abspath(temp_path)]
        if isinstance(status_tuple, tuple) and status_tuple[0] == 'FOUND':
            virus_name = status_tuple[1]
            os.remove(temp_path)  # Delete the infected file immediately
            logger.warning(f"Malware detected in {file.filename}: {virus_name}")
            raise HTTPException(status_code=400, detail=f"Malware detected: {virus_name}")

    # 6. Move to final destination if clean
    final_path = os.path.join(UPLOAD_DIR, file.filename)
    os.rename(temp_path, final_path)
    logger.info(f"File {file.filename} uploaded and scanned successfully")
    
    return {"status": "Clean", "file": file.filename}

@app.get("/download/{filename}")
async def download_apk(filename: str):
    # Security: Prevent path traversal attacks
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        logger.warning(f"Path traversal attempt detected: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Validate filename is just the basename (no directory components)
    if os.path.basename(filename) != filename:
        logger.warning(f"Path traversal attempt detected: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        logger.info(f"Download request for non-existent file: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"File {filename} downloaded")
    return FileResponse(path, media_type='application/vnd.android.package-archive')