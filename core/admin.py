from django.contrib import admin
from .models import (
    Klijent, OrganizacionaJedinica, Kontakt, KategorijaDokumenta,
    MasterTemplejt, KlijentskiDokument, PoslatiMail, SmtpSettings,
    EmailTemplejt, Zaposleni, Obuka, LekarskiPregled, LZO,
    Oprema, PregledIspitivanje, PovredaNaRadu, Inspekcija
)

@admin.register(Klijent)
class KlijentAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'pib', 'maticni_broj', 'status', 'broj_zaposlenih')
    search_fields = ('naziv', 'pib', 'maticni_broj')
    list_filter = ('status',)

@admin.register(OrganizacionaJedinica)
class OrganizacionaJedinicaAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'klijent', 'adresa', 'broj_zaposlenih')
    list_filter = ('klijent',)
    search_fields = ('naziv', 'klijent__naziv')

@admin.register(Kontakt)
class KontaktAdmin(admin.ModelAdmin):
    list_display = ('ime_i_prezime', 'klijent', 'email', 'pozicija', 'is_primary')
    list_filter = ('klijent', 'is_primary')
    search_fields = ('ime_i_prezime', 'email', 'klijent__naziv')

@admin.register(KategorijaDokumenta)
class KategorijaDokumentaAdmin(admin.ModelAdmin):
    list_display = ('naziv',)
    search_fields = ('naziv',)

@admin.register(MasterTemplejt)
class MasterTemplejtAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'kategorija', 'verzija', 'status', 'created_at')
    list_filter = ('kategorija', 'status')
    search_fields = ('naziv',)

@admin.register(KlijentskiDokument)
class KlijentskiDokumentAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'klijent', 'master_templejt', 'status', 'datum_izdavanja', 'rok_vazenja')
    list_filter = ('klijent', 'status', 'datum_izdavanja', 'rok_vazenja')
    search_fields = ('naziv', 'klijent__naziv')

@admin.register(EmailTemplejt)
class EmailTemplejtAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'naslov', 'kategorija')
    search_fields = ('naziv', 'naslov', 'kategorija')
    list_filter = ('kategorija',)

@admin.register(PoslatiMail)
class PoslatiMailAdmin(admin.ModelAdmin):
    list_display = ('naslov', 'primaoci', 'datum_slanja')
    list_filter = ('datum_slanja',)
    search_fields = ('naslov', 'primaoci')
    filter_horizontal = ('prilozeni_dokumenti',)

@admin.register(SmtpSettings)
class SmtpSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_host', 'email_host_user')

@admin.register(Zaposleni)
class ZaposleniAdmin(admin.ModelAdmin):
    list_display = ('ime', 'prezime', 'klijent', 'radno_mesto', 'status')
    list_filter = ('klijent', 'status', 'povecan_rizik')
    search_fields = ('ime', 'prezime', 'jmbg', 'klijent__naziv')

@admin.register(Obuka)
class ObukaAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'tip_obuke', 'datum_obuke', 'datum_vazenja')
    list_filter = ('tip_obuke', 'datum_obuke')
    search_fields = ('zaposleni__ime', 'zaposleni__prezime')

@admin.register(LekarskiPregled)
class LekarskiPregledAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'tip_pregleda', 'datum_pregleda', 'naredni_pregled', 'sposoban')
    list_filter = ('tip_pregleda', 'sposoban')
    search_fields = ('zaposleni__ime', 'zaposleni__prezime')

@admin.register(LZO)
class LZOAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'tip_opreme', 'datum_izdavanja', 'razduzeno')
    list_filter = ('razduzeno',)
    search_fields = ('zaposleni__ime', 'zaposleni__prezime', 'tip_opreme')

@admin.register(Oprema)
class OpremaAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'klijent', 'inventarski_broj', 'status')
    list_filter = ('klijent', 'status')
    search_fields = ('naziv', 'inventarski_broj', 'serijski_broj', 'klijent__naziv')

@admin.register(PregledIspitivanje)
class PregledIspitivanjeAdmin(admin.ModelAdmin):
    list_display = ('oprema', 'tip_pregleda', 'datum_pregleda', 'naredni_pregled', 'nalaz')
    list_filter = ('nalaz', 'datum_pregleda')
    search_fields = ('oprema__naziv',)

@admin.register(PovredaNaRadu)
class PovredaNaRaduAdmin(admin.ModelAdmin):
    list_display = ('zaposleni', 'datum_povrede', 'tezina_povrede', 'status')
    list_filter = ('tezina_povrede', 'status')
    search_fields = ('zaposleni__ime', 'zaposleni__prezime')

@admin.register(Inspekcija)
class InspekcijaAdmin(admin.ModelAdmin):
    list_display = ('klijent', 'datum_inspekcije', 'inspektor', 'status')
    list_filter = ('status', 'datum_inspekcije')
    search_fields = ('klijent__naziv', 'inspektor')
