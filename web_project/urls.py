from django.urls import path
from trashApp import views as tmpl_views

urlpatterns = [
    path('tr/login', tmpl_views.login_html, name='login'),
    path('tr/registrieren', tmpl_views.registrieren_html, name='registrieren'),
    path('tr/profil', tmpl_views.profil_html, name='profil'),
    path('tr/profil/bearbeiten', tmpl_views.profil_bearbeiten, name='profilBearbeitung'),
    path('tr/dashboard', tmpl_views.dashboard_html, name='dashboard'),
    path('tr/admin', tmpl_views.admin_html, name='admin'),
    path('tr/logout', tmpl_views.logout, name='logout'),
    path('tr/kontakt/', tmpl_views.kontakt_email, name='kontakt'),
    path('api/upload/', tmpl_views.api_upload, name='api_upload'),
    #path('tr/klassifizierte-bilder/', tmpl_views.klassifizierte_bilder_html, name='klassifizierte_bilder'),
    path('tr/logbuch-eintrag/', tmpl_views.logbuchEintragHtml, name='logbuch_eintrag'),
    path('tr/logbuch/loeschen/', tmpl_views.eintragLoeschen, name='eintragLoeschen'),
    path('tr/logbuch/aendern/', tmpl_views.eintragArtAendern, name='eintrag_art_aendern'),
    #path('test/', tmpl_views.test_view, name='test'),
    #path('test/aendern/', tmpl_views.aendere_art, name='aendere_art'),
    path('tr/admin/benutzer/sperren/<uuid:benutzer_id>/', tmpl_views.sperren_benutzer, name='sperren_benutzer'),
    path('tr/admin/benutzer/entsperren/<uuid:benutzer_id>/', tmpl_views.entsperren_benutzer, name='entsperren_benutzer'),
    path('tr/system', tmpl_views.system_html, name='system'),
    path('tr/admin/benutzer/hochsetzen/<uuid:benutzer_id>/', tmpl_views.rolle_hochsetzen, name='rolle_hochsetzen'),
    path('tr/admin/benutzer/runtersetzen/<uuid:benutzer_id>/', tmpl_views.rolle_runtersetzen, name='rolle_runtersetzen'),
    path('tr/flyer', tmpl_views.flyer_html, name='flyer'),
    path("tr/dashboard/reset_fuellstand/", tmpl_views.reset_fuellstand, name="reset_fuellstand"),
    path('api/fuellstand/', tmpl_views.api_fuellstand, name='api_fuellstand'),


]

 

"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""
