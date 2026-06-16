from django.apps import AppConfig
from django.core.files.storage import FileSystemStorage

class BypassNginxStorage(FileSystemStorage):
    def url(self, name):
        # Appending /serve removes the .png/.jpg file extension from the end of the URL.
        # This completely bypasses Nginx's aggressive static file regex, forcing it to
        # fall back to the Django proxy, resolving the 404 issue without any server config changes.
        return super().url(name) + "/serve"

class BlogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blogs'
