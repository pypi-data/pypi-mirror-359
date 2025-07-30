from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.apps import apps
from django.http import Http404
from django.urls import reverse

class CRUDListView(ListView):
    template_name = 'easyboard/crud_list.html'
    paginate_by = 25

    def get_queryset(self):
        app_label = self.kwargs.get('app_label')
        model_name = self.kwargs.get('model_name')
        try:
            model = apps.get_model(app_label, model_name)
        except Exception:
            raise Http404('Модель не найдена')
        return model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.kwargs.get('model_name')
        context['app_label'] = self.kwargs.get('app_label')
        if self.object_list:
            context['fields'] = [f.name for f in self.object_list.model._meta.fields]
        else:
            context['fields'] = []
        return context

class CRUDCreateView(CreateView):
    template_name = 'easyboard/crud_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])
        self.fields = [f.name for f in self.model._meta.fields if f.editable and f.name != 'id']
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        from django.forms import modelform_factory
        return modelform_factory(self.model, fields=self.fields)

    def get_success_url(self):
        return reverse('easyboard:crud_list', kwargs={
            'app_label': self.kwargs['app_label'],
            'model_name': self.kwargs['model_name']
        })

class CRUDUpdateView(UpdateView):
    template_name = 'easyboard/crud_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])
        self.fields = [f.name for f in self.model._meta.fields if f.editable and f.name != 'id']
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        from django.forms import modelform_factory
        return modelform_factory(self.model, fields=self.fields)

    def get_success_url(self):
        return reverse('easyboard:crud_list', kwargs={
            'app_label': self.kwargs['app_label'],
            'model_name': self.kwargs['model_name']
        })

class CRUDDeleteView(DeleteView):
    template_name = 'easyboard/crud_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.model = apps.get_model(self.kwargs['app_label'], self.kwargs['model_name'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('easyboard:crud_list', kwargs={
            'app_label': self.kwargs['app_label'],
            'model_name': self.kwargs['model_name']
        }) 