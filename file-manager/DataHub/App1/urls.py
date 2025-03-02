from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('filesview/<str:file_type>', views.files_view, name='filesview'),
    path('delete_file/<int:file_id>', views.delete_view, name='delete_file'),
    path('search_file/', views.search_file, name='search_file'),
    path('preview_file/<int:upload_id>', views.preview_file, name='preview_file'),
    path('download_file/<int:file_id>', views.download_view, name='download_file'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('Folders/', views.folders_view, name='folders_view'),
    path('delete_folder/<int:folder_id>', views.delete_folder, name='delete_folder'),
    path('Move_file/<int:file_id>', views.move_view, name='move_view'),
    path('profile/', views.profile_view, name='profile'),

]
