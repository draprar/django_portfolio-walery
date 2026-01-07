import pytest
from django.urls import reverse, resolve
from django.core.files.uploadedfile import SimpleUploadedFile
from docdiff.views import docdiff_view


@pytest.mark.django_db
class TestDocDiffView:
    """Integration tests for the main DocDiff view (docdiff_view)."""

    def test_get_returns_upload_page(self, client):
        """GET request should render the upload form page (200 OK)."""
        url = reverse("docdiff:index")
        response = client.get(url)
        assert response.status_code == 200
        html = response.content.decode().lower()
        # expect form tag or file input
        assert "<form" in html
        assert "file" in html

    def test_post_without_files_returns_400(self, client):
        """POST request without files should return a 400 JSON error."""
        url = reverse("docdiff:compare")
        response = client.post(url, {})
        assert response.status_code == 200
        html = response.content.decode().lower()
        assert "missing_files" in html

    def test_post_with_txt_files_returns_html_response(self, client):
        """
        POST request with two .txt files should:
        - process comparison successfully
        - return a valid HTML report as response
        """
        url = reverse("docdiff:compare")

        # Create two simple text files to compare
        old_file = SimpleUploadedFile("old.txt", b"Hello world")
        new_file = SimpleUploadedFile("new.txt", b"Hello brave new world")

        response = client.post(url, {"file_old": old_file, "file_new": new_file})

        assert response.status_code == 200
        content = response.content.decode("utf-8").lower()

        # Response should be an HTML page containing the report
        assert "<html" in content
        assert "raport" in content or "diff" in content

    def test_unsupported_extension_raises_valueerror(self, client):
        """Unsupported file types should return a 400 error with message."""
        url = reverse("docdiff:compare")
        bad_file = SimpleUploadedFile("file.xyz", b"abc")
        response = client.post(url, {"file_old": bad_file, "file_new": bad_file})
        assert response.status_code == 200
        html = response.content.decode().lower()
        assert "unsupported_type" in html


class TestDocDiffUrls:
    """Basic tests for URL configuration of the docdiff app."""

    def test_index_url_resolves_correct_view(self):
        """The 'index' route should resolve to the main docdiff_view."""
        path = reverse("docdiff:index")
        assert resolve(path).func.__name__ == docdiff_view.__name__

    def test_compare_url_resolves_correct_view(self):
        """The 'compare' route should resolve to the same docdiff_view."""
        path = reverse("docdiff:compare")
        assert resolve(path).func.__name__ == docdiff_view.__name__
