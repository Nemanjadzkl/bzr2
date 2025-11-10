from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
from django.utils import timezone
from simple_history.models import HistoricalRecords

def klijent_logo_upload_path(instance, filename):
    return f'klijenti/{instance.id}/logo/{filename}'

class Klijent(models.Model):
    # ... (postojeci Klijent model) ...
    STATUS_CHOICES = (
        ('Aktivan', 'Aktivan'),
        ('Neaktivan', 'Neaktivan'),
        ('Arhiviran', 'Arhiviran'),
    )
    # Osnovni podaci
    naziv = models.CharField(max_length=255, verbose_name="Naziv firme")
    pib = models.CharField(max_length=20, unique=True, verbose_name="PIB")
    maticni_broj = models.CharField(max_length=20, unique=True, verbose_name="Matični broj")
    adresa = models.CharField(max_length=255, verbose_name="Adresa")
    telefon = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Email")
    web_sajt = models.URLField(blank=True, verbose_name="Web sajt")
    logo = models.ImageField(upload_to=klijent_logo_upload_path, blank=True, null=True, verbose_name="Logo firme")

    # Dodatni podaci
    sifra_delatnosti = models.CharField(max_length=20, blank=True, verbose_name="Šifra delatnosti")
    broj_zaposlenih = models.PositiveIntegerField(default=0, verbose_name="Ukupan broj zaposlenih")
    broj_zaposlenih_povecan_rizik = models.PositiveIntegerField(default=0, verbose_name="Broj zaposlenih sa povećanim rizikom")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktivan', verbose_name="Status klijenta")
    datum_pocetka_saradnje = models.DateField(null=True, blank=True, verbose_name="Datum početka saradnje")
    odgovorna_osoba_bzr = models.CharField(max_length=255, blank=True, verbose_name="Odgovorna osoba za BZR")
    napomene = models.TextField(blank=True, verbose_name="Napomene")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = "Klijent"
        verbose_name_plural = "Klijenti"
        ordering = ['naziv']

class OrganizacionaJedinica(models.Model):
    # ... (postojeci OrganizacionaJedinica model) ...
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='organizacione_jedinice')
    naziv = models.CharField(max_length=255, verbose_name="Naziv poslovne jedinice")
    adresa = models.CharField(max_length=255, verbose_name="Adresa")
    broj_zaposlenih = models.PositiveIntegerField(default=0, verbose_name="Broj zaposlenih u jedinici")
    rukovodilac = models.CharField(max_length=255, blank=True, verbose_name="Rukovodilac jedinice")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.naziv} ({self.klijent.naziv})"

    class Meta:
        verbose_name = "Organizaciona Jedinica"
        verbose_name_plural = "Organizacione Jedinice"

class Kontakt(models.Model):
    # ... (postojeci Kontakt model) ...
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='kontakti', verbose_name="Klijent")
    ime_i_prezime = models.CharField(max_length=255, verbose_name="Ime i prezime")
    pozicija = models.CharField(max_length=255, blank=True, verbose_name="Pozicija u firmi")
    email = models.EmailField(verbose_name="Email adresa")
    telefon = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    mobilni = models.CharField(max_length=50, blank=True, verbose_name="Mobilni telefon")
    is_primary = models.BooleanField(default=False, verbose_name="Primarni kontakt")
    napomene = models.TextField(blank=True, verbose_name="Napomene")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.ime_i_prezime} ({self.klijent.naziv})"

    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakti"

class KategorijaDokumenta(models.Model):
    # ... (postojeci KategorijaDokumenta model) ...
    naziv = models.CharField(max_length=100, unique=True, verbose_name="Naziv kategorije")
    history = HistoricalRecords()

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = "Kategorija Dokumenta"
        verbose_name_plural = "Kategorije Dokumenata"

def master_template_upload_path(instance, filename):
    return f'master_templates/{instance.kategorija.naziv}/{filename}'

class MasterTemplejt(models.Model):
    # ... (postojeci MasterTemplejt model) ...
    STATUS_CHOICES = (
        ('Aktivan', 'Aktivan'),
        ('Arhiviran', 'Arhiviran'),
        ('U pripremi', 'U pripremi'),
    )
    naziv = models.CharField(max_length=255, verbose_name="Naziv šablona")
    kategorija = models.ForeignKey(KategorijaDokumenta, on_delete=models.PROTECT, verbose_name="Kategorija dokumenta")
    fajl = models.FileField(upload_to=master_template_upload_path, verbose_name="Fajl templejta")
    verzija = models.CharField(max_length=20, default="1.0", verbose_name="Verzija")
    parent_template = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='revisions', verbose_name="Prethodna verzija")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktivan', verbose_name="Status")
    opis = models.TextField(blank=True, verbose_name="Opis i napomene")
    kreator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='kreirani_templejti')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.naziv} (v{self.verzija})"

    class Meta:
        verbose_name = "Master Templejt"
        verbose_name_plural = "Master Templejti"

def klijentski_dokument_upload_path(instance, filename):
    return f'klijenti/{instance.klijent.id}/dokumenta/{filename}'

class KlijentskiDokument(models.Model):
    # ... (postojeci KlijentskiDokument model) ...
    STATUS_CHOICES = (
        ('Aktivan', 'Aktivan'),
        ('Istekao', 'Istekao'),
        ('Arhiviran', 'Arhiviran'),
    )
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='dokumenti', verbose_name="Klijent")
    master_templejt = models.ForeignKey(MasterTemplejt, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Originalni master templejt")
    naziv = models.CharField(max_length=255, verbose_name="Naziv dokumenta")
    fajl = models.FileField(upload_to=klijentski_dokument_upload_path, verbose_name="Finalni fajl")
    datum_izdavanja = models.DateField(verbose_name="Datum izdavanja")
    rok_vazenja = models.DateField(null=True, blank=True, verbose_name="Rok važenja")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktivan', verbose_name="Status")
    verzija = models.CharField(max_length=20, blank=True, verbose_name="Verzija dokumenta")
    kreirao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='kreirani_klijentski_dokumenti')
    odobrio = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='odobreni_klijentski_dokumenti')
    napomene = models.TextField(blank=True, verbose_name="Napomene")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.naziv} ({self.klijent.naziv})"

    class Meta:
        verbose_name = "Klijentski Dokument"
        verbose_name_plural = "Klijentski Dokumenti"

class EmailTemplejt(models.Model):
    # ... (postojeci EmailTemplejt model) ...
    naziv = models.CharField(max_length=255, verbose_name="Naziv templejta")
    naslov = models.CharField(max_length=255, verbose_name="Naslov (Subject)")
    telo = models.TextField(verbose_name="Telo poruke", help_text="Koristite promenljive poput {klijent_naziv}, {datum}, {dokumenti}.")
    kategorija = models.CharField(max_length=100, blank=True, verbose_name="Kategorija")
    history = HistoricalRecords()

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = "Email Templejt"
        verbose_name_plural = "Email Templejti"

class PoslatiMail(models.Model):
    # ... (postojeci PoslatiMail model) ...
    posiljalac = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Posiljalac")
    primaoci = models.TextField(verbose_name="Primaoci (To)")
    naslov = models.CharField(max_length=255, verbose_name="Naslov email-a")
    telo_poruke = models.TextField(verbose_name="Telo poruke")
    prilozeni_dokumenti = models.ManyToManyField(KlijentskiDokument, blank=True, related_name='poslati_mailovi', verbose_name="Priloženi dokumenti")
    datum_slanja = models.DateTimeField(auto_now_add=True, verbose_name="Datum slanja")
    history = HistoricalRecords()

    def __str__(self):
        return f"Mail za {self.primaoci} - {self.naslov}"

    class Meta:
        verbose_name = "Poslati Mail"
        verbose_name_plural = "Poslati Mailovi"

class SmtpSettings(models.Model):
    # ... (postojeci SmtpSettings model) ...
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='smtp_settings')
    email_host = models.CharField(max_length=255)
    email_port = models.IntegerField(default=587)
    email_host_user = models.CharField(max_length=255)
    email_host_password_encrypted = models.BinaryField()
    email_use_tls = models.BooleanField(default=True)
    history = HistoricalRecords()

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

# ========== MODELI ZA FAZU 3 ==========

class Zaposleni(models.Model):
    # ... (postojeci Zaposleni model) ...
    STATUS_CHOICES = (
        ('Aktivan', 'Aktivan'),
        ('Neaktivan', 'Neaktivan'),
    )
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='zaposleni')
    ime = models.CharField(max_length=100, verbose_name="Ime")
    prezime = models.CharField(max_length=100, verbose_name="Prezime")
    jmbg = models.CharField(max_length=13, unique=True, verbose_name="JMBG")
    radno_mesto = models.CharField(max_length=255, verbose_name="Radno mesto")
    organizaciona_jedinica = models.ForeignKey(OrganizacionaJedinica, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Organizaciona jedinica")
    povecan_rizik = models.BooleanField(default=False, verbose_name="Radno mesto sa povećanim rizikom")
    datum_zaposlenja = models.DateField(verbose_name="Datum zaposlenja")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktivan', verbose_name="Status")
    strucna_sprema = models.CharField(max_length=100, blank=True, verbose_name="Stručna sprema")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.ime} {self.prezime}"

    class Meta:
        verbose_name = "Zaposleni"
        verbose_name_plural = "Zaposleni"

class Obuka(models.Model):
    # ... (postojeci Obuka model) ...
    TIP_OBUKE_CHOICES = (
        ('Inicijalna', 'Inicijalna'),
        ('Periodična', 'Periodična'),
        ('Vanredna', 'Vanredna'),
    )
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE, related_name='obuke')
    tip_obuke = models.CharField(max_length=50, choices=TIP_OBUKE_CHOICES, verbose_name="Tip obuke")
    datum_obuke = models.DateField(verbose_name="Datum obuke")
    datum_vazenja = models.DateField(verbose_name="Datum važenja (naredna obuka)")
    sertifikat = models.FileField(upload_to='sertifikati/obuke/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Obuka za {self.zaposleni} - {self.datum_obuke}"

    class Meta:
        verbose_name = "Obuka BZR"
        verbose_name_plural = "Obuke BZR"

class LekarskiPregled(models.Model):
    # ... (postojeci LekarskiPregled model) ...
    TIP_PREGLEDA_CHOICES = (
        ('Prethodni', 'Prethodni'),
        ('Periodični', 'Periodični'),
    )
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE, related_name='lekarski_pregledi')
    tip_pregleda = models.CharField(max_length=50, choices=TIP_PREGLEDA_CHOICES, verbose_name="Tip pregleda")
    datum_pregleda = models.DateField(verbose_name="Datum pregleda")
    naredni_pregled = models.DateField(verbose_name="Datum narednog pregleda")
    sposoban = models.BooleanField(default=True, verbose_name="Zdravstveno sposoban")
    dokument = models.FileField(upload_to='lekarski_pregledi/', blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Lekarski pregled za {self.zaposleni} - {self.datum_pregleda}"

    class Meta:
        verbose_name = "Lekarski Pregled"
        verbose_name_plural = "Lekarski Pregledi"

class LZO(models.Model): # Licna Zastitna Oprema
    # ... (postojeci LZO model) ...
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE, related_name='lzo_zaduzenja')
    tip_opreme = models.CharField(max_length=255, verbose_name="Tip opreme")
    datum_izdavanja = models.DateField(verbose_name="Datum izdavanja")
    kolicina = models.PositiveIntegerField(default=1, verbose_name="Količina")
    rok_trajanja = models.DateField(null=True, blank=True, verbose_name="Rok trajanja opreme")
    razduzeno = models.BooleanField(default=False, verbose_name="Razduženo")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.tip_opreme} za {self.zaposleni}"

    class Meta:
        verbose_name = "Lična Zaštitna Oprema (LZO)"
        verbose_name_plural = "Lična Zaštitna Oprema (LZO)"

# ========== MODELI ZA FAZU 4 ==========

class Oprema(models.Model):
    # ... (postojeci Oprema model) ...
    STATUS_CHOICES = (
        ('U funkciji', 'U funkciji'),
        ('Na servisu', 'Na servisu'),
        ('Van upotrebe', 'Van upotrebe'),
    )
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='oprema')
    naziv = models.CharField(max_length=255, verbose_name="Naziv opreme")
    inventarski_broj = models.CharField(max_length=100, blank=True, verbose_name="Inventarski broj")
    serijski_broj = models.CharField(max_length=100, blank=True, verbose_name="Serijski broj")
    proizvodjac = models.CharField(max_length=100, blank=True, verbose_name="Proizvođač")
    datum_nabavke = models.DateField(null=True, blank=True, verbose_name="Datum nabavke")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='U funkciji', verbose_name="Status")
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.naziv} ({self.klijent.naziv})"

    class Meta:
        verbose_name = "Oprema za Rad"
        verbose_name_plural = "Oprema za Rad"

class PregledIspitivanje(models.Model):
    # ... (postojeci PregledIspitivanje model) ...
    NALAZ_CHOICES = (
        ('Ispravan', 'Ispravan'),
        ('Neispravan', 'Neispravan'),
    )
    oprema = models.ForeignKey(Oprema, on_delete=models.CASCADE, related_name='pregledi')
    tip_pregleda = models.CharField(max_length=255, verbose_name="Tip pregleda/ispitivanja")
    datum_pregleda = models.DateField(verbose_name="Datum pregleda")
    naredni_pregled = models.DateField(verbose_name="Datum narednog pregleda")
    ovlascena_kuca = models.CharField(max_length=255, blank=True, verbose_name="Ovlašćena kuća")
    nalaz = models.CharField(max_length=20, choices=NALAZ_CHOICES, verbose_name="Nalaz")
    strucni_nalaz_fajl = models.FileField(upload_to='strucni_nalazi/', blank=True, null=True, verbose_name="Stručni nalaz (fajl)")
    history = HistoricalRecords()

    def __str__(self):
        return f"Pregled za {self.oprema.naziv} - {self.datum_pregleda}"

    class Meta:
        verbose_name = "Pregled i Ispitivanje"
        verbose_name_plural = "Pregledi i Ispitivanja"

# ========== NOVI MODELI ZA FAZU 5 ==========

class PovredaNaRadu(models.Model):
    TEZINA_CHOICES = (
        ('Laka', 'Laka'),
        ('Teška', 'Teška'),
        ('Smrtna', 'Smrtna'),
        ('Kolektivna', 'Kolektivna'),
    )
    zaposleni = models.ForeignKey(Zaposleni, on_delete=models.CASCADE, related_name='povrede')
    datum_povrede = models.DateTimeField(verbose_name="Datum i vreme povrede")
    mesto = models.CharField(max_length=255, verbose_name="Mesto incidenta")
    opis = models.TextField(verbose_name="Opis povrede i okolnosti")
    svedoci = models.TextField(blank=True, verbose_name="Svedoci")
    tezina_povrede = models.CharField(max_length=20, choices=TEZINA_CHOICES, verbose_name="Težina povrede")
    izvestaj = models.FileField(upload_to='povrede_izvestaji/', blank=True, null=True, verbose_name="Izveštaj o povredi (fajl)")
    status = models.CharField(max_length=50, default="U obradi", verbose_name="Status")
    history = HistoricalRecords()

    def __str__(self):
        return f"Povreda na radu za {self.zaposleni} - {self.datum_povrede.date()}"

    class Meta:
        verbose_name = "Povreda na Radu"
        verbose_name_plural = "Povrede na Radu"

class Inspekcija(models.Model):
    STATUS_CHOICES = (
        ('U toku', 'U toku'),
        ('Završeno', 'Završeno'),
    )
    klijent = models.ForeignKey(Klijent, on_delete=models.CASCADE, related_name='inspekcije')
    datum_inspekcije = models.DateField(verbose_name="Datum inspekcije")
    inspektor = models.CharField(max_length=255, verbose_name="Inspektor (ime, institucija)")
    nalaz = models.TextField(verbose_name="Nalazi i nedostaci")
    zapisnik = models.FileField(upload_to='inspekcije_zapisnici/', blank=True, null=True, verbose_name="Zapisnik (fajl)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='U toku', verbose_name="Status")
    history = HistoricalRecords()

    def __str__(self):
        return f"Inspekcija za {self.klijent.naziv} - {self.datum_inspekcije}"

    class Meta:
        verbose_name = "Inspekcija"
        verbose_name_plural = "Inspekcije"
