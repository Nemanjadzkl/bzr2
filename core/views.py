from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from .models import Dokument, ArhiviraniDokument, PoslatiMail, Klijent, TipDokumenta, SmtpSettings
from .forms import SendEmailForm, SmtpSettingsForm
from django.db.models import Q

class FileManagerView(LoginRequiredMixin, ListView):
    model = Dokument
    template_name = 'core/file_manager.html'
    context_object_name = 'dokumenti'

class AddTemplateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Dokument
    fields = ['naziv_dokumenta', 'tip_dokumenta', 'fajl']
    template_name = 'core/add_template.html'
    success_url = reverse_lazy('core:file_manager')
    success_message = "Novi master templejt je uspešno dodat."

class SendDocumentView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'core/send_document.html'
    form_class = SendEmailForm
    success_url = reverse_lazy('core:file_manager')
    success_message = "Email je uspešno poslat i dokument arhiviran."

    def form_valid(self, form):
        klijent = form.cleaned_data['klijent']
        primaoci = form.cleaned_data['primaoci']
        naslov = form.cleaned_data['naslov']
        poruka = form.cleaned_data['poruka']
        fajl = self.request.FILES['fajl']

        originalni_dokument_id = self.kwargs['pk']
        originalni_dokument = Dokument.objects.get(id=originalni_dokument_id)

        arhivirani_dokument = ArhiviraniDokument.objects.create(
            klijent=klijent,
            originalni_dokument=originalni_dokument,
            fajl=fajl
        )

        email = EmailMessage(
            naslov,
            poruka,
            'test@example.com', # Privremeno za testiranje
            primaoci.split(','),
        )
        email.attach(fajl.name, fajl.read(), fajl.content_type)
        email.send()

        poslati_mail = PoslatiMail.objects.create(
            posiljalac=self.request.user,
            primaoci=primaoci,
            naslov=naslov,
            telo_poruke=poruka
        )
        poslati_mail.prilozeni_dokumenti.add(arhivirani_dokument)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dokument'] = Dokument.objects.get(id=self.kwargs['pk'])
        return context

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

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(primaoci__icontains=query) | Q(naslov__icontains=query)
            )
        return queryset

class SmtpSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SmtpSettings
    form_class = SmtpSettingsForm
    template_name = 'core/smtp_settings.html'
    success_url = reverse_lazy('core:smtp_settings')
    success_message = "SMTP podešavanja su uspešno sačuvana."

    def get_object(self, queryset=None):
        obj, created = SmtpSettings.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        if password:
            self.object.set_password(password)
        return super().form_valid(form)
