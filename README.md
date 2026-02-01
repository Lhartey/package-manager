# Package Manager

A simple and secure APK upload and download service with built-in malware scanning.

## What It Does

Upload Android packages (APKs) safely with automatic malware detection using ClamAV. Once scanned, files are stored securely and available for download. It's like a gatekeeper that checks everything coming in before letting it through.

## Getting Started

### Prerequisites
- Python 3.8+
- ClamAV antivirus engine (for scanning)

### Install ClamAV on Your Server

Run these commands on your Linux server (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install clamav clamav-daemon

# Update the virus database
sudo freshclam
```

Then start the ClamAV daemon:

```bash
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon  # Auto-start on reboot
```

### Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your settings:**
   Edit the `.env` file with your preferences:
   - `AUTH_TOKEN` - Your secret authentication token
   - `CORS_ORIGINS` - Allowed domains (comma-separated)
   - `MAX_FILE_SIZE` - Upload limit in bytes

4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

Visit `http://localhost:8000/docs` to see the interactive API documentation.

## API Endpoints

- **POST `/upload`** - Upload and scan an APK file
  - Header: `x-token: your-auth-token`
  - Body: multipart form with `file` field

- **GET `/download/{filename}`** - Download a previously scanned APK

## Security Features

✅ Token-based authentication  
✅ Malware scanning with ClamAV  
✅ File size limits  
✅ Path traversal protection  
✅ Comprehensive logging  
✅ CORS support  

## Project Structure

```
.
├── main.py           # FastAPI application
├── .env              # Configuration (don't commit!)
├── packages/         # Uploaded files storage
└── requirements.txt  # Python dependencies
```

## Notes

- Files are temporarily stored during scanning then moved to `/packages` if clean
- Infected files are automatically deleted
- All actions are logged for security auditing
- Make sure `.env` is in your `.gitignore` - never commit secrets!

## License

Yours to use however you like. 🚀
