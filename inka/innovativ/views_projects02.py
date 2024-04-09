from django.contrib import messages
from django.shortcuts import render
from django.template import Template, Context

from .forms_projects import EmailTemplateForm
from .models import Task, EmailTemplate
from django.core.mail import send_mail

from inka.settings import DEFAULT_FROM_EMAIL

def p_02_1_telefonszam_keres(request, task_id):
    # az aktuális ügyfél
    task = Task.objects.get(pk=task_id)

    # a feladathoz tartozó email sablon
    email_template = EmailTemplate.objects.get(title='02.1. Email kérés elérhető telefonszámért')

    # szerkeszthető szöveg a sblon alapján
    template = Template(email_template.content)

    # az aktuális ügyfélnév helyettesítése a sablon változója alapján
    context = Context({'customer_name': task.customer})
    rendered_content = template.render(context)

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=email_template)
        if form.is_valid():
            subject = form['subject'].value()
            message = form['content'].value()
            to_email = [task.customer.email]
            sent = send_mail(subject, message, DEFAULT_FROM_EMAIL, to_email, html_message=message)
            # Az új feladat jelzőből Folyamatban jelző lesz
            task.type = '3:'
            task.type_color = '3:'
            task.save()
            if sent:
                messages.success(request, 'E-mail sikeresen elküldve!')
                Task.objects.create(type='0:',  # Esemény bejegyzésés
                                    type_color='0:',
                                    project=task.project,
                                    customer=task.customer,
                                    comment=f'{task.customer} ügyfélnek - 02.1. Email kérés elérhető telefonszámért - '
                                            f'nevű sablon email kiküldve.',
                                    created_user=request.user)
            else:
                Task.objects.create(type='1:',  # Figyelmeztető bejegyzésés
                                    type_color='1:',
                                    project=task.project,
                                    customer=task.customer,
                                    comment=f'{task.customer} ügyfélnek sikertelen lett az email küldés.',
                                    created_user=request.user)
                messages.success(request,'Hiba történt az e-mail küldése közben!')
            return render(request, 'home.html', {})

    else:
        form = EmailTemplateForm(instance=email_template, initial={'content': rendered_content})

    return render(request, 'p_02_1_telefonszam_keres.html', {'task': task, 'form': form})

