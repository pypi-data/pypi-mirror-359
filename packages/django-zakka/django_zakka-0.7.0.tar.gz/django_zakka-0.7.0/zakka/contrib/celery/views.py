from celery import current_app
from celery.execute import send_task
from django import forms
from django.contrib import messages
from django.urls import path
from django.views.generic import FormView

from zakka import permissions


class TaskForm(forms.Form):
    task = forms.CharField(label="Your name", max_length=100)


class CeleryJobs(permissions.SuperuserRequiredMixin, FormView):
    template_name = "zakka/celery/tasks.html"
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        current_app.loader.import_default_modules()
        # For each task in our current app, either get the version with schedule information or a
        # placeholder with the same key
        data["tasks"] = [
            current_app.conf.beat_schedule.get(task, {"task": task}) for task in current_app.tasks
        ]
        return data

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, f"Running {form.data['task']}")
        send_task(form.data["task"])
        return self.get(self.request)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, f"Invalid {form.errors}")
        return self.get(self.request)


urlpatterns = [path("", CeleryJobs.as_view())]
