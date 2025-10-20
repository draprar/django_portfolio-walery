from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pathlib import Path
import tempfile
import json

from .extractors.extract_docx import DocxExtractor
from .extractors.extract_xlsx import XlsxExtractor
from .extractors.extract_txt import TxtExtractor
from .diff_engine import compare_blocks
from .report_builder import generate_html_report
from .heuristics_ai import analyze_change


def docdiff_view(request):
    """
    Główny widok narzędzia DocDiff.
    Obsługuje upload dwóch plików, porównanie i wyświetlenie raportu.
    """
    if request.method == "POST":
        file_old = request.FILES.get("file_old")
        file_new = request.FILES.get("file_new")

        if not file_old or not file_new:
            return JsonResponse({"error": "Proszę przesłać dwa pliki do porównania."}, status=400)

        # Zapis tymczasowy
        temp_dir = Path(tempfile.mkdtemp())
        old_path = temp_dir / file_old.name
        new_path = temp_dir / file_new.name

        with open(old_path, "wb") as f:
            for chunk in file_old.chunks():
                f.write(chunk)
        with open(new_path, "wb") as f:
            for chunk in file_new.chunks():
                f.write(chunk)

        # Wybór ekstraktora po rozszerzeniu
        def get_extractor(path: Path):
            ext = path.suffix.lower()
            if ext == ".docx":
                return DocxExtractor()
            elif ext == ".xlsx":
                return XlsxExtractor()
            elif ext == ".txt":
                return TxtExtractor()
            else:
                raise ValueError(f"Nieobsługiwane rozszerzenie: {ext}")

        old_extractor = get_extractor(old_path)
        new_extractor = get_extractor(new_path)

        # Ekstrakcja i porównanie bloków
        old_blocks = old_extractor.extract_blocks(old_path)
        new_blocks = new_extractor.extract_blocks(new_path)
        diff_result = compare_blocks(old_blocks, new_blocks)

        # AI analiza semantyczna
        for block in diff_result:
            ai_info = analyze_change(block)
            block.update(ai_info)

        # Generowanie raportu HTML
        output_html = temp_dir / "raport.html"
        generate_html_report(diff_result, output_html)

        # Wczytanie gotowego raportu i render w przeglądarce
        with open(output_html, "r", encoding="utf-8") as f:
            html_content = f.read()

        return HttpResponse(html_content)

    # GET → pokazuje formularz uploadu
    return render(request, "docdiff/upload.html")
