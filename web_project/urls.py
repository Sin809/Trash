"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from trashApp import views as tmpl_views

urlpatterns = [
    path('tr/login', tmpl_views.login_html, name='login'),
    path('tr/registrieren', tmpl_views.registrieren_html, name='registrieren'),
    path('tr/profil', tmpl_views.profil_html, name='profil'),
    path('tr/profil/bearbeiten', tmpl_views.profil_bearbeiten, name='profilBearbeitung'),
    path('tr/dashboard', tmpl_views.dashboard_html, name='dashboard'),
    path('tr/logout', tmpl_views.logout, name='logout'),
    path('tr/kontakt/', tmpl_views.kontakt_email, name='kontakt'),
]



"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""
