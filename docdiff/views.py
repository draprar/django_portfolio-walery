from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from pathlib import Path
import tempfile
import shutil

from .extractors.normalize import normalize_blocks
from .extractors.extract_docx import DocxExtractor
from .extractors.extract_xlsx import XlsxExtractor
from .extractors.extract_txt import TxtExtractor
from .diff_engine import compare_blocks
from .report_builder import generate_html_report
from .heuristics_ai import analyze_change


# Upload validation parameters
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".docx", ".xlsx", ".txt"}
ALLOWED_MIME = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".txt": "text/plain",
}
FORMAT_GROUP = {
    ".txt": "txt",
    ".docx": "docx",
    ".xlsx": "xlsx",
}

def validate_upload(upload):
    """Validate uploaded file extension, MIME and size."""
    ext = Path(upload.name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    if upload.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large: {upload.size / 1024**2:.1f} MB")
    if hasattr(upload, "content_type"):
        if upload.content_type != ALLOWED_MIME.get(ext, ""):
            raise ValueError(f"Invalid MIME type: {upload.content_type}")

def validate_file_pair(file_old, file_new):
    ext_old = Path(file_old.name).suffix.lower()
    ext_new = Path(file_new.name).suffix.lower()

    if FORMAT_GROUP.get(ext_old) != FORMAT_GROUP.get(ext_new):
        raise ValueError(
            f"File format mismatch: {ext_old} vs {ext_new}. "
            "Both files must be of the same type."
        )

@require_http_methods(["GET", "POST"])
def docdiff_view(request):
    """
    Main DocDiff view:
    Handles upload of two files, performs diff and returns rendered HTML report.
    """
    if request.method == "POST":
        file_old = request.FILES.get("file_old")
        file_new = request.FILES.get("file_new")

        if not file_old or not file_new:
            return render(
                request,
                "docdiff/upload.html",
                {"error": "Please upload both files."}
            )

        # Validate uploads
        try:
            validate_upload(file_old)
            validate_upload(file_new)
            validate_file_pair(file_old, file_new)
        except ValueError as e:
            return render(
                request,
                "docdiff/upload.html",
                {"error": str(e)}
            )

        # Temporary storage
        temp_dir = Path(tempfile.mkdtemp())
        old_path = temp_dir / file_old.name
        new_path = temp_dir / file_new.name

        with open(old_path, "wb") as f:
            for chunk in file_old.chunks():
                f.write(chunk)
        with open(new_path, "wb") as f:
            for chunk in file_new.chunks():
                f.write(chunk)

        # Select extractor by extension
        def get_extractor(path: Path):
            ext = path.suffix.lower()
            if ext == ".docx":
                return DocxExtractor()
            elif ext == ".xlsx":
                return XlsxExtractor()
            elif ext == ".txt":
                return TxtExtractor()
            raise ValueError(f"Unsupported extension: {ext}")

        old_extractor = get_extractor(old_path)
        new_extractor = get_extractor(new_path)

        # Extraction and comparison
        try:
            old_blocks = old_extractor.extract_blocks(old_path)
            new_blocks = new_extractor.extract_blocks(new_path)
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return render(
                request,
                "docdiff/upload.html",
                {"error": "Failed to read document content. Make sure the file is not corrupted."}
            )

        if not old_blocks and not new_blocks:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return render(
                request,
                "docdiff/upload.html",
                {"error": "No readable content found in documents."}
            )

        diff_result = compare_blocks(old_blocks, new_blocks)

        # Prevent excessive AI processing
        changed_blocks = [b for b in diff_result if b.get("change") == "changed"]
        if len(changed_blocks) > 300:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return render(
                request,
                "docdiff/upload.html",
                {"error": "Too many changes to analyze. Try smaller documents."}
            )

        # AI semantic analysis
        for block in diff_result:
            if block.get("change") != "changed":
                continue

            old_type = block.get("old", {}).get("type")
            new_type = block.get("new", {}).get("type")

            # AI text only
            if old_type != "paragraph" or new_type != "paragraph":
                block.update({
                    "labels": [],
                    "semantic_score": None,
                    "change_type": "structural",
                    "confidence": 1.0,
                })
                continue

            try:
                ai_info = analyze_change(block)
                block.update(ai_info)
            except Exception as e:
                # AI failure must not kill the request
                block.update({
                    "labels": [],
                    "semantic_score": None,
                    "change_type": "ai_error",
                    "confidence": 0.0,
                })

        # Generate report
        output_html = temp_dir / "report.html"
        generate_html_report(diff_result, output_html)

        with open(output_html, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

        return HttpResponse(html_content)

    # GET → upload form
    return render(request, "docdiff/upload.html")
