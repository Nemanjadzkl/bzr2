from django.contrib import admin
from .models import Klijent, Kontakt, TipDokumenta, Dokument, ArhiviraniDokument, PoslatiMail

@admin.register(Klijent)
class KlijentAdmin(admin.ModelAdmin):
    list_display = ('naziv', 'pib', 'adresa', 'created_at')
    search_fields = ('naziv', 'pib')

@admin.register(Kontakt)
class KontaktAdmin(admin.ModelAdmin):
    list_display = ('ime_i_prezime', 'klijent', 'email', 'telefon')
    list_filter = ('klijent',)
    search_fields = ('ime_i_prezime', 'email', 'klijent__naziv')

@admin.register(TipDokumenta)
class TipDokumentaAdmin(admin.ModelAdmin):
    list_display = ('naziv',)
    search_fields = ('naziv',)

@admin.register(Dokument)
class DokumentAdmin(admin.ModelAdmin):
    list_display = ('naziv_dokumenta', 'tip_dokumenta', 'created_at')
    list_filter = ('tip_dokumenta',)
    search_fields = ('naziv_dokumenta',)

@admin.register(ArhiviraniDokument)
class ArhiviraniDokumentAdmin(admin.ModelAdmin):
    list_display = ('fajl', 'klijent', 'originalni_dokument', 'datum_arhiviranja')
    list_filter = ('klijent', 'datum_arhiviranja')
    search_fields = ('fajl', 'klijent__naziv')

@admin.register(PoslatiMail)
class PoslatiMailAdmin(admin.ModelAdmin):
    list_display = ('naslov', 'primaoci', 'datum_slanja')
    list_filter = ('datum_slanja',)
    search_fields = ('naslov', 'primaoci')
    filter_horizontal = ('prilozeni_dokumenti',)
