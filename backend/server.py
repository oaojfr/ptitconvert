"""
FastAPI backend for PtitConvert
Provides a simple HTTP API for Electron (or any client) to drive conversions.

Endpoints:
- GET /health -> { status: "ok" }
- GET /formats -> returns supported output formats for a given input file or extension
- POST /convert -> starts a background job and returns { job_id }
- GET /jobs/{job_id} -> progress and status
- GET /history/recent -> recent conversions from SQLite history
"""

from __future__ import annotations

import os
import platform
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure project root is in path for imports
ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from converters.spreadsheet_converter import SpreadsheetConverter
from converters.advanced_document_converter import AdvancedDocumentConverter
from converters.archive_converter import ArchiveConverter
from converters.media_converter import MediaConverter
from utils.history import ConversionHistory


app = FastAPI(title="PtitConvert API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConvertRequest(BaseModel):
    files: List[str]
    output_format: str
    output_dir: str


class JobStatus(BaseModel):
    job_id: str
    total: int
    processed: int
    success: int
    failed: int
    current_file: Optional[str] = None
    message: Optional[str] = None
    done: bool = False


# Simple in-memory job registry
JOBS: Dict[str, JobStatus] = {}
JOBS_LOCK = threading.Lock()


# Converters (singletons for the process)
IMG = ImageConverter()
DOC = DocumentConverter()
SHEET = SpreadsheetConverter()
ADVDOC = AdvancedDocumentConverter()
ARCH = ArchiveConverter()
MEDIA = MediaConverter()
HISTORY = ConversionHistory()


def _supported_formats_for_extension(ext: str) -> List[str]:
    ext = ext.lower()
    # Images
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
        return ['PNG', 'JPG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'PDF']
    # Documents standards
    if ext in ['.pdf', '.docx', '.txt']:
        return ['PDF', 'DOCX', 'TXT']
    # Documents avancés
    if ext in ['.epub', '.odt', '.rtf']:
        return ['PDF', 'DOCX', 'TXT', 'EPUB', 'ODT', 'RTF']
    # Feuilles de calcul
    if ext in ['.xlsx', '.csv', '.ods']:
        return ['XLSX', 'CSV', 'ODS', 'PDF']
    # Archives
    if ext in ['.zip', '.tar', '.rar', '.7z']:
        return ['ZIP', 'TAR', '7Z']
    # Média audio
    if ext in ['.mp3', '.wav', '.flac']:
        return ['MP3', 'WAV', 'FLAC', 'OGG']
    # Média vidéo
    if ext in ['.mp4', '.avi']:
        return ['MP4', 'AVI', 'MKV', 'MOV']
    return []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/formats")
def get_formats(file_path: Optional[str] = None, file_ext: Optional[str] = None):
    ext = None
    if file_ext:
        ext = file_ext if file_ext.startswith('.') else f'.{file_ext}'
    elif file_path:
        ext = Path(file_path).suffix
    else:
        raise HTTPException(status_code=400, detail="Provide file_path or file_ext")
    return {"formats": _supported_formats_for_extension(ext)}


def _convert_one(file_path: str, output_format: str, output_dir: str) -> Tuple[bool, Optional[str]]:
    try:
        ext = Path(file_path).suffix.lower()
        # Images
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']:
            ok = IMG.convert(file_path, output_dir, output_format.lower())
        # Documents standards
        elif ext in ['.pdf', '.docx', '.txt']:
            ok = DOC.convert(file_path, output_dir, output_format.lower())
        # Documents avancés
        elif ext in ['.epub', '.odt', '.rtf']:
            ok = ADVDOC.convert(file_path, output_dir, output_format.lower())
        # Feuilles de calcul
        elif ext in ['.xlsx', '.csv', '.ods']:
            ok = SHEET.convert(file_path, output_dir, output_format.lower())
        # Archives
        elif ext in ['.zip', '.tar', '.rar', '.7z']:
            try:
                ok = ARCH.convert(file_path, output_dir, output_format.lower())
            except AttributeError:
                ok = ARCH.extract_archive(file_path, output_dir)
        # Média
        elif ext in ['.mp3', '.mp4', '.avi', '.wav', '.flac']:
            ok = MEDIA.convert(file_path, output_dir, output_format.lower())
        else:
            return False, f"Format non supporté: {ext}"
        return (True, None) if ok else (False, None)
    except Exception as e:
        return False, str(e)


def _run_job(job_id: str, files: List[str], output_format: str, output_dir: str):
    status = JOBS[job_id]
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(files):
        with JOBS_LOCK:
            status.current_file = os.path.basename(f)
            status.message = f"Conversion de {status.current_file} ({i+1}/{status.total})"
        ok, err = _convert_one(f, output_format, output_dir)
        # Add to history
        try:
            input_name = Path(f).stem
            out_file = os.path.join(output_dir, f"{input_name}.{output_format.lower()}")
            HISTORY.add_conversion(
                input_file=f,
                input_format=Path(f).suffix.lower().lstrip('.'),
                output_file=out_file,
                output_format=output_format.lower(),
                file_size=os.path.getsize(f) if os.path.exists(f) else 0,
                conversion_time=0,
                success=ok,
                error_message=err,
            )
        except Exception:
            pass
        with JOBS_LOCK:
            status.processed += 1
            if ok:
                status.success += 1
            else:
                status.failed += 1
    with JOBS_LOCK:
        status.done = True
        status.message = "Conversion terminée"


@app.post("/convert")
def convert(req: ConvertRequest):
    if not req.files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    job_id = str(uuid.uuid4())
    status = JobStatus(job_id=job_id, total=len(req.files), processed=0, success=0, failed=0)
    with JOBS_LOCK:
        JOBS[job_id] = status
    t = threading.Thread(target=_run_job, args=(job_id, req.files, req.output_format, req.output_dir), daemon=True)
    t.start()
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    st = JOBS.get(job_id)
    if not st:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return st


@app.get("/history/recent")
def history_recent(limit: int = Query(100, ge=1, le=1000)):
    return {"items": HISTORY.get_recent_conversions(limit=limit)}


@app.post("/open_folder")
def open_folder(path: str):
    try:
        if not os.path.isdir(path):
            raise HTTPException(status_code=400, detail="Chemin invalide")
        if platform.system() == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            import subprocess
            subprocess.run(["open", path], check=False)
        else:
            import subprocess
            subprocess.run(["xdg-open", path], check=False)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run():
    import uvicorn
    port = int(os.environ.get("PTITCONVERT_PORT", "8787"))
    uvicorn.run("backend.server:app", host="127.0.0.1", port=port, reload=False, workers=1)


if __name__ == "__main__":
    run()
