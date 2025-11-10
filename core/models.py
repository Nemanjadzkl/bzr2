from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet

class Klijent(models.Model):
    naziv = models.CharField(max_length=255, verbose_name="Naziv klijenta")
    pib = models.CharField(max_length=20, unique=True, verbose_name="PIB")
    adresa = models.CharField(max_length=255, verbose_name="Adresa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = "Klijent"
        verbose_name_plural = "Klijenti"
        ordering = ['naziv']

class Kontakt(models.Model):
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='kontakti', verbose_name="Klijent")
    ime_i_prezime = models.CharField(max_length=255, verbose_name="Ime i prezime")
    email = models.EmailField(verbose_name="Email adresa")
    telefon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Telefon")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ime_i_prezime} ({self.klijent.naziv})"

    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakti"

class TipDokumenta(models.Model):
    naziv = models.CharField(max_length=100, unique=True, verbose_name="Naziv tipa dokumenta")

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = "Tip Dokumenta"
        verbose_name_plural = "Tipovi Dokumenata"

def master_template_upload_path(instance, filename):
    return f'master_templates/{instance.tip_dokumenta.naziv}/{filename}'

class Dokument(models.Model):
    naziv_dokumenta = models.CharField(max_length=255, verbose_name="Naziv dokumenta")
    tip_dokumenta = models.ForeignKey(TipDokumenta, on_delete=models.PROTECT, verbose_name="Tip dokumenta")
    fajl = models.FileField(upload_to=master_template_upload_path, verbose_name="Fajl")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.naziv_dokumenta

    class Meta:
        verbose_name = "Master Templejt Dokument"
        verbose_name_plural = "Master Templejti Dokumenata"

def arhivirani_dokument_upload_path(instance, filename):
    return f'arhiva/{instance.klijent.naziv}_{instance.klijent.id}/{filename}'

class ArhiviraniDokument(models.Model):
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='arhivirani_dokumenti', verbose_name="Klijent")
    originalni_dokument = models.ForeignKey(Dokument, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Originalni master templejt")
    fajl = models.FileField(upload_to=arhivirani_dokument_upload_path, verbose_name="Arhivirani fajl")
    datum_arhiviranja = models.DateTimeField(auto_now_add=True, verbose_name="Datum arhiviranja")

    def __str__(self):
        return f"{self.fajl.name} (Klijent: {self.klijent.naziv})"

    class Meta:
        verbose_name = "Arhivirani Dokument"
        verbose_name_plural = "Arhivirani Dokumenti"

class PoslatiMail(models.Model):
    posiljalac = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Posiljalac")
    primaoci = models.TextField(verbose_name="Primaoci (To)")
    naslov = models.CharField(max_length=255, verbose_name="Naslov email-a")
    telo_poruke = models.TextField(verbose_name="Telo poruke")
    prilozeni_dokumenti = models.ManyToManyField(ArhiviraniDokument, related_name='poslati_mailovi', verbose_name="Priloženi dokumenti")
    datum_slanja = models.DateTimeField(auto_now_add=True, verbose_name="Datum slanja")

    def __str__(self):
        return f"Mail za {self.primaoci} - {self.naslov}"

    class Meta:
        verbose_name = "Poslati Mail"
        verbose_name_plural = "Poslati Mailovi"

class SmtpSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='smtp_settings')
    email_host = models.CharField(max_length=255)
    email_port = models.IntegerField(default=587)
    email_host_user = models.CharField(max_length=255)
    email_host_password_encrypted = models.BinaryField()
    email_use_tls = models.BooleanField(default=True)

    def set_password(self, password):
        f = Fernet(settings.ENCRYPTION_KEY)
        self.email_host_password_encrypted = f.encrypt(password.encode())

    def get_password(self):
        f = Fernet(settings.ENCRYPTION_KEY)
        return f.decrypt(self.email_host_password_encrypted).decode()

    def __str__(self):
        return f"SMTP podešavanja za {self.user.username}"

    class Meta:
        verbose_name = "SMTP Podešavanje"
        verbose_name_plural = "SMTP Podešavanja"
