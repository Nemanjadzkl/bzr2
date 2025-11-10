from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, TemplateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMessage
from .models import Klijent, MasterTemplejt, KlijentskiDokument, PoslatiMail, SmtpSettings, Kontakt, EmailTemplejt
from .forms import SmtpSettingsForm, SendDocumentForm
from django.db.models import Q
from datetime import date, timedelta

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ukupan_broj_klijenata'] = Klijent.objects.filter(status='Aktivan').count()
        context['poslati_mailovi_mesec'] = PoslatiMail.objects.filter(datum_slanja__month=date.today().month).count()
        nadolazeci_rokovi_datum = date.today() + timedelta(days=30)
        context['nadolazeci_rokovi_dokumenti'] = KlijentskiDokument.objects.filter(
            rok_vazenja__lte=nadolazeci_rokovi_datum,
            rok_vazenja__gte=date.today(),
            status='Aktivan'
        ).order_by('rok_vazenja')
        return context

class FileManagerView(LoginRequiredMixin, ListView):
    model = MasterTemplejt
    template_name = 'core/file_manager.html'
    context_object_name = 'templejti'

class AddTemplateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MasterTemplejt
    fields = ['naziv', 'kategorija', 'fajl', 'verzija', 'status', 'opis']
    template_name = 'core/add_template.html'
    success_url = reverse_lazy('core:file_manager')
    success_message = "Novi master templejt je uspešno dodat."

    def form_valid(self, form):
        form.instance.kreator = self.request.user
        return super().form_valid(form)

class KlijentListView(LoginRequiredMixin, ListView):
    model = Klijent
    template_name = 'core/klijent_list.html'
    context_object_name = 'klijenti'

class KlijentDetailView(LoginRequiredMixin, DetailView):
    model = Klijent
    template_name = 'core/klijent_detail.html'
    context_object_name = 'klijent'

class PoslatiMailListView(LoginRequiredMixin, ListView):
    model = PoslatiMail
    template_name = 'core/poslati_mail_list.html'
    context_object_name = 'mailovi'
    paginate_by = 10

class SmtpSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SmtpSettings
    form_class = SmtpSettingsForm
    template_name = 'core/smtp_settings.html'
    success_url = reverse_lazy('core:smtp_settings')
    success_message = "SMTP podešavanja su uspešno sačuvana."

    def get_object(self, queryset=None):
        obj, created = SmtpSettings.objects.get_or_create(user=self.request.user)
        return obj

class SendDocumentView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'core/send_document_modal.html'
    form_class = SendDocumentForm
    success_message = "Email je uspešno poslat i dokument arhiviran."

    def get_success_url(self):
        return reverse('core:file_manager')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['master_templejt'] = get_object_or_404(MasterTemplejt, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        klijent = form.cleaned_data['klijent']
        primaoci_qs = form.cleaned_data['primaoci']
        primaoci_emails = [kontakt.email for kontakt in primaoci_qs]

        dodatni_primaoci = form.cleaned_data['dodatni_primaoci']
        if dodatni_primaoci:
            primaoci_emails.extend([email.strip() for email in dodatni_primaoci.split(',')])

        naslov = form.cleaned_data['naslov']
        poruka = form.cleaned_data['poruka']
        fajl = self.request.FILES['fajl']
        master_templejt = get_object_or_404(MasterTemplejt, pk=self.kwargs['pk'])

        klijentski_dokument = None
        if form.cleaned_data['arhiviraj_dokument']:
            klijentski_dokument = KlijentskiDokument.objects.create(
                klijent=klijent,
                master_templejt=master_templejt,
                naziv=fajl.name,
                fajl=fajl,
                datum_izdavanja=date.today(),
                kreirao=self.request.user
            )

        email = EmailMessage(
            naslov,
            poruka,
            self.request.user.email,
            primaoci_emails,
        )
        email.attach(fajl.name, fajl.read(), fajl.content_type)
        email.send()

        poslati_mail = PoslatiMail.objects.create(
            posiljalac=self.request.user,
            primaoci=", ".join(primaoci_emails),
            naslov=naslov,
            telo_poruke=poruka
        )
        if klijentski_dokument:
            poslati_mail.prilozeni_dokumenti.add(klijentski_dokument)

        return super().form_valid(form)

def get_klijent_kontakti(request):
    klijent_id = request.GET.get('klijent_id')
    kontakti = Kontakt.objects.filter(klijent_id=klijent_id).values('id', 'ime_i_prezime')
    return JsonResponse(list(kontakti), safe=False)

def get_email_templejt(request):
    templejt_id = request.GET.get('templejt_id')
    templejt = get_object_or_404(EmailTemplejt, id=templejt_id)
    return JsonResponse({'naslov': templejt.naslov, 'telo': templejt.telo})

class EmailTemplejtListView(LoginRequiredMixin, ListView):
    model = EmailTemplejt
    template_name = 'core/email_templejt_list.html'
    context_object_name = 'templejti'
