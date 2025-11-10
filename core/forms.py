from django import forms
from .models import Klijent, SmtpSettings, Kontakt, EmailTemplejt

class SendDocumentForm(forms.Form):
    klijent = forms.ModelChoiceField(
        queryset=Klijent.objects.filter(status='Aktivan'),
        label="1. Odaberi Klijenta",
        widget=forms.Select(attrs={'class': 'form-select w-full'})
    )
    primaoci = forms.ModelMultipleChoiceField(
        queryset=Kontakt.objects.none(), # Dinamički se puni u view-u
        label="2. Primaoci",
        widget=forms.CheckboxSelectMultiple
    )
    dodatni_primaoci = forms.CharField(
        required=False,
        label="Dodaj dodatni email",
        widget=forms.TextInput(attrs={'placeholder': 'email@example.com, drugi@email.com'})
    )
    email_templejt = forms.ModelChoiceField(
        queryset=EmailTemplejt.objects.all(),
        required=False,
        label="3. Email Podešavanja - Templejt",
        widget=forms.Select(attrs={'class': 'form-select w-full'})
    )
    naslov = forms.CharField(
        label="Naslov",
        widget=forms.TextInput(attrs={'placeholder': 'Naslov email poruke'})
    )
    poruka = forms.CharField(
        label="Poruka",
        widget=forms.Textarea(attrs={'rows': 10}) # Ovde dolazi Rich Text Editor
    )
    fajl = forms.FileField(
        label="4. Upload Finalni Dokument"
    )
    arhiviraj_dokument = forms.BooleanField(
        required=False,
        initial=True,
        label="Arhiviraj dokument kod klijenta"
    )
    posalji_kopiju_sebi = forms.BooleanField(
        required=False,
        label="Pošalji kopiju sebi"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'klijent' in self.data:
            try:
                klijent_id = int(self.data.get('klijent'))
                self.fields['primaoci'].queryset = Kontakt.objects.filter(klijent_id=klijent_id)
            except (ValueError, TypeError):
                pass
        elif self.instance:
            self.fields['primaoci'].queryset = self.instance.klijent.kontakti.all()


class SmtpSettingsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Lozinka")

    class Meta:
        model = SmtpSettings
        fields = ['email_host', 'email_port', 'email_host_user', 'password', 'email_use_tls']
        labels = {
            'email_host': "SMTP Host",
            'email_port': "SMTP Port",
            'email_host_user': "Korisničko ime",
            'email_use_tls': "Koristi TLS",
        }
