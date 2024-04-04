from django.shortcuts import render
from django.template import Template, Context

from .models import Task, EmailTemplate


def p_02_1_telefonszam_keres(request, task_id):
    task = Task.objects.get(pk=task_id)
    email_template = EmailTemplate.objects.get(title='02.1. Email kérés elérhető telefonszámért')

    template = Template(email_template.content)
    context = Context({'customer_name': task.customer})
    rendered_content = template.render(context)

    return render(request, 'p_02_1_telefonszam_keres.html', {'task': task,
                                                             'email_template': email_template,
                                                             'rendered_content': rendered_content})
