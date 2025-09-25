from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class SupabasePublicStorage(S3Boto3Storage):
    default_acl = "public-read"
    file_overwrite = False

    def url(self, name, parameters=None, expire=None, http_method=None):
        return f"{settings.MEDIA_URL}{name}"
