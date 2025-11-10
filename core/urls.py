from django.urls import path
from .views import (
    DashboardView,
    FileManagerView,
    AddTemplateView,
    KlijentListView,
    KlijentDetailView,
    PoslatiMailListView,
    SmtpSettingsView,
    SendDocumentView,
    EmailTemplejtListView,
    get_klijent_kontakti,
    get_email_templejt
)

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('dokumentacija/templejti/', FileManagerView.as_view(), name='file_manager'),
    path('dokumentacija/templejti/dodaj/', AddTemplateView.as_view(), name='add_template'),

    path('klijenti/', KlijentListView.as_view(), name='klijent_list'),
    path('klijent/<int:pk>/', KlijentDetailView.as_view(), name='klijent_detail'),

    path('email/poslati/', PoslatiMailListView.as_view(), name='poslati_mail_list'),
    path('email/templejti/', EmailTemplejtListView.as_view(), name='email_templejt_list'),
    path('email/send/<int:pk>/', SendDocumentView.as_view(), name='send_document'),

    path('podesavanja/smtp/', SmtpSettingsView.as_view(), name='smtp_settings'),

    # AJAX
    path('ajax/get-klijent-kontakti/', get_klijent_kontakti, name='get_klijent_kontakti'),
    path('ajax/get-email-templejt/', get_email_templejt, name='get_email_templejt'),
]
