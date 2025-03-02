Keretit - File Manager Web Application

Keretit is a modern, user-friendly file manager built with Django, designed to help users securely upload, organize, preview, and manage files and folders. With a clean interface powered by Bootstrap and robust backend logic, Keretit offers an efficient solution for personal file management.

Features
User Authentication: Secure login, registration, and logout using Django's built-in authentication system.
File Management:
Upload files with automatic categorization (e.g., Documents, Images, Videos) based on extensions.
Preview files inline (e.g., images, PDFs) using MIME type detection.
Download and delete files with real-time filesystem synchronization.
Folder Management: Create custom folders and move files into them dynamically.
Search: Quickly find files by name across all categories.
Profile Dashboard: View total storage usage and recent uploads for the logged-in user.
Security: Restricts file access to the authenticated owner with path validation.
Responsive UI: Built with Bootstrap 5 for a mobile-friendly experience, featuring modals for folder creation.

Tech Stack
Backend: Python 3.9+, Django 4.2
Frontend: HTML, CSS (Bootstrap 5.3), JavaScript
Storage: Local filesystem via Django's MEDIA_ROOT
Key Libraries:
os and shutil for file operations
mimetypes for content type detection
django.contrib.auth for authentication
django.contrib.messages for user feedback

Prerequisites
Python 3.9 or higher
Django 4.2 (install via pip install django)

Usage
Register/Login: Create an account or log in to access the file manager.
Upload Files: Go to the Upload page to add files, which are automatically categorized.
Manage Files:
View all files under /filesview/all.
Preview files with the "Preview" option.
Download or delete files as needed.
Create Folders: Use the "New Folder" dropdown option to organize files.
Move Files: Select a file and move it to a folder via the Move option.
Search: Use the search bar to find specific files by name.
Profile: Check your storage stats and recent uploads on the Profile page.
