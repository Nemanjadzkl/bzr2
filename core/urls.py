from django.urls import path
from .views import (
    FileManagerView,
    AddTemplateView,
    SendDocumentView,
    KlijentListView,
    KlijentDetailView,
    PoslatiMailListView,
    SmtpSettingsView
)

app_name = 'core'

urlpatterns = [
    path('', FileManagerView.as_view(), name='file_manager'),
    path('add-template/', AddTemplateView.as_view(), name='add_template'),
    path('send-document/<int:pk>/', SendDocumentView.as_view(), name='send_document'),
    path('klijenti/', KlijentListView.as_view(), name='klijent_list'),
    path('klijent/<int:pk>/', KlijentDetailView.as_view(), name='klijent_detail'),
    path('poslati-mailovi/', PoslatiMailListView.as_view(), name='poslati_mail_list'),
    path('smtp-settings/', SmtpSettingsView.as_view(), name='smtp_settings'),
]
