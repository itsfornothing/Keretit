import os
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, get_backends
from .form import UserForm
from .models import Uploads, FileTypes, Folders
from DataHub.settings import MEDIA_ROOT
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.utils.encoding import smart_str
import mimetypes
from django.http import JsonResponse
import shutil 
from django.utils.text import get_valid_filename
from django.db.models import Sum


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please provide both email and password!")
            return render(request, 'login.html')
        
        try:
            user_instance = User.objects.get(email=email)

        except User.DoesNotExist:
            messages.error(request, "Please register! You don't have an account.")
            return render(request, 'login.html')

        user = authenticate(request, username=user_instance.username, password=password)
        if user:
            login(request, user)
            return redirect('home_page')
        
        messages.error(request, 'Invalid Credential!')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username is already taken, please enter another.")

            elif User.objects.filter(email__iexact=email).exists():
                messages.error(request, "You already have an account, please login instead!")

            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                backend = get_backends()[0]
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                login(request, user)
                return redirect('home_page')
    else:
        form = UserForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    all_files_size = Uploads.objects.filter(owner=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0
    all_files_size_mb = round(all_files_size / 1024, 3)
    recent_upload = Uploads.objects.filter(owner=request.user).first()

    return render(request, 'profile.html' , {"all_files_size": all_files_size_mb, "recent_upload": recent_upload})

@login_required
def home_view(request):
    return render(request, 'home.html')

@login_required
def upload_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_name = get_valid_filename(uploaded_file.name)

        file_type = file_identifier(file_extension)
        category, created = FileTypes.objects.get_or_create(name=file_type, user=request.user)
        owner_name = request.user.username
        DESTINATION = os.path.join(MEDIA_ROOT, f'{file_type}/{owner_name}')
        
        if not os.path.isdir(DESTINATION):
            os.makedirs(DESTINATION)

        dst_path = os.path.join(DESTINATION, file_name)

        counter = 1
        while os.path.exists(dst_path):
            file_name = f"{file_name.rsplit('.', 1)[0]}_{counter}.{file_extension}"
            dst_path = os.path.join(DESTINATION, file_name)
            counter += 1

        with open(dst_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        new_upload = Uploads(
            name = file_name,
            owner = request.user,
            file_path = dst_path,
            category = category,
            size = uploaded_file.size
        )
        new_upload.save()
        messages.success(request, "The file uploaded successfully!")
            
    return render(request, 'upload.html')


@login_required
def download_view(request, file_id):
    upload = get_object_or_404(Uploads, id=file_id, owner=request.user)
    try:
        file_path = upload.file_path 

        if not file_path.startswith(MEDIA_ROOT):
            return HttpResponse("Access denied.", status=403)

        response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
        return response

    except FileNotFoundError:
        return HttpResponse("File not found.", status=404)

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


@login_required
def delete_view(request, file_id):   
    try:
        file_to_delete = Uploads.objects.get(id=file_id, owner=request.user)
        file_path = file_to_delete.file_path
        file_to_delete.delete()

        if os.path.exists(file_path):
            os.remove(file_path)
        
        parent_directory_path = os.path.dirname(file_path)
        check_empty = os.listdir(parent_directory_path)
        if len(check_empty) == 0: 
            shutil.rmtree(parent_directory_path)

        messages.success(request, "File deleted successfully.")

    except Uploads.DoesNotExist:
        messages.error(request, "File not found.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
    return redirect('filesview', file_type='all')
    

@login_required
def files_view(request, file_type):
    all_files = {}
    files = []
    folder_name = ''
    if file_type == 'all':
        categories = FileTypes.objects.filter(user=request.user).prefetch_related('uploads')
        for category in categories:
            uploads = category.uploads.all()
            for upload in uploads:
                upload.size_mb = round(upload.size / 1024, 3)

            all_files[category] = category.uploads.all()

    else:
        # for folders
        directory = os.path.join(MEDIA_ROOT, f'folders/{request.user.username}/{file_type}')
        files = os.listdir(directory)
        folder_name = file_type

    return render(request, 'view_files.html', {'all_files': all_files, 'files':files, 'folder_name':folder_name})


@login_required
def search_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name', '')
        all_files = {}
        categories = FileTypes.objects.filter(user=request.user).prefetch_related('uploads')

        for category in categories:
            uploads = category.uploads.all()
            for upload in uploads:
                upload.size_mb = round(upload.size / 1024, 3)

            all_files[category] = category.uploads.all()

        if file_name:
            search_result = Uploads.objects.filter(owner=request.user, name__icontains=file_name).first()
        else:
            search_result = None

        return render(request, 'view_files.html', {'all_files': all_files, 'search_result': search_result})
    
    else:
        return HttpResponseNotFound("Invalid request method.")
        

@login_required
def preview_file(request, upload_id):
    upload = get_object_or_404(Uploads, id=upload_id, owner=request.user) 

    try:
        file_path = upload.file_path 
        content_type, encoding = mimetypes.guess_type(file_path)

        if content_type is None:
            content_type = 'application/octet-stream' 

        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = 'inline; filename=%s' % smart_str(upload.name)
        return response

    except FileNotFoundError:
        return HttpResponse("File not found.", status=404)

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder_check = Folders.objects.filter(name=folder_name, owner=request.user).exists()
        
        if folder_check:
            messages.error(request, "Folder name taken.")
            return

        else:
            DESTINATION = os.path.join(MEDIA_ROOT, f'folders/{request.user.username}/{folder_name}')
            if not os.path.isdir(DESTINATION):
                os.makedirs(DESTINATION)
            new_folder = Folders(
                name=folder_name, owner=request.user
            )
            new_folder.save()

            return redirect('folders_view')
        
@login_required        
def delete_folder(request, folder_id):
    try:
        folder_to_delete = Folders.objects.get(id=folder_id, owner=request.user)
        folder_name = folder_to_delete.name
        folder_to_delete.delete()
        DESTINATION = os.path.join(MEDIA_ROOT, f'folders/{request.user.username}/{folder_name}')

        if os.path.exists(DESTINATION):
            shutil.rmtree(DESTINATION)

    except Uploads.DoesNotExist:
        messages.error(request, "File not found.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")

    return redirect('folders_view')

    
@login_required
def folders_view(request):
    all_folders = Folders.objects.filter(owner=request.user)
    return render(request, 'folders.html', {'all_folders': all_folders})

@login_required
def move_view(request, file_id):
    if request.method == "POST":
        file = Uploads.objects.filter(id=file_id, owner=request.user).first()
        if file:
            folder_name = request.POST.get('folder_name')
            folder_path = os.path.join(MEDIA_ROOT, f'folders/{request.user.username}/{folder_name}')

            if os.path.exists(folder_path):
                shutil.copy(file.file_path, folder_path) 
                messages.success(request, f"File successfilly moved! ")

            else:
                messages.error(request, f"Folder doesn't exist! ")
        else:
            messages.error(request, f"File doesn't exist! ")
    else:
        messages.error(request, f"Invalid request!")

    return redirect('filesview', file_type='all')

    
def file_identifier(file_extension):
    file_types = {
        'Documents': ['txt', 'doc', 'docx', 'pdf', 'rtf', 'odt', 'xls', 'xlsx', 'ods', 'ppt', 'pptx', 'odp', 'srt'],
        'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'svg', 'ai', 'eps'],
        'Videos': ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv'],
        'Archives': ['zip', 'rar', '7z', 'tar'],
        'Audios': ['mp3', 'flac', 'aac', 'wav', 'ogg', 'm4a'],
        'Executables': ['exe', 'app', 'apk', 'dmg', 'bin'],
        'Codes': ['py', 'js', 'html', 'htm', 'css', 'php', 'xls', 'c', 'cpp', 'h', 'java', 'sh'],
        'Databases': ['sql', 'db', 'sqlite'],
        'Configurations': ['ini', 'json', 'xml', 'yaml', 'yml'],
        'Fonts': ['ttf', 'otf']
    }
    for category, extensions in file_types.items():
            if file_extension in extensions:
                return category
            
    return "Uknown"