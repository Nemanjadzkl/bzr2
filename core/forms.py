from django import forms
from .models import Klijent, SmtpSettings

class SendEmailForm(forms.Form):
    klijent = forms.ModelChoiceField(queryset=Klijent.objects.all(), label="Klijent")
    primaoci = forms.CharField(widget=forms.Textarea, label="Primaoci")
    naslov = forms.CharField(max_length=255, label="Naslov")
    poruka = forms.CharField(widget=forms.Textarea, label="Poruka")
    fajl = forms.FileField(label="Finalna verzija dokumenta")

class SmtpSettingsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = SmtpSettings
        fields = ['email_host', 'email_port', 'email_host_user', 'password', 'email_use_tls']
