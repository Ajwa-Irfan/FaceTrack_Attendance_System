import os
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.conf import settings

@staff_member_required
def serve_protected_face(request, filename):
    secure_dir = os.path.join(settings.BASE_DIR, 'secure_faces')  # same as FileSystemStorage location
    file_path = os.path.join(secure_dir, filename)

    if not os.path.exists(file_path):
        raise Http404("File not found")

    return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')