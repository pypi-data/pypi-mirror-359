from django.views.generic import TemplateView
from django.conf import settings
import importlib.util
from django.apps import apps
import importlib

class DashboardView(TemplateView):
    template_name = 'easyboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        easyboard_settings = getattr(settings, 'EASYBOARD', {})
        context['site_title'] = easyboard_settings.get('SITE_TITLE', 'EasyBoard Admin')
        context['brand_logo'] = easyboard_settings.get('BRAND_LOGO', '')
        context['show_stats'] = easyboard_settings.get('SHOW_STATS', True)
        context['custom_cards'] = easyboard_settings.get('CUSTOM_DASHBOARD_CARDS', [])
        # Проверка наличия интеграций
        context['has_import_export'] = importlib.util.find_spec('import_export') is not None
        context['has_mptt'] = importlib.util.find_spec('mptt') is not None
        context['has_constance'] = importlib.util.find_spec('constance') is not None
        context['has_dynamic_preferences'] = importlib.util.find_spec('dynamic_preferences') is not None
        context['has_drf'] = (
            importlib.util.find_spec('drf_spectacular') is not None or
            importlib.util.find_spec('drf_yasg') is not None
        )
        # Динамические данные
        # Пользователи
        try:
            User = apps.get_model(settings.AUTH_USER_MODEL)
            context['users_count'] = User.objects.count()
        except Exception:
            context['users_count'] = '—'
        # Заказы
        try:
            Order = apps.get_model('orders', 'Order')
            context['orders_count'] = Order.objects.count()
        except Exception:
            context['orders_count'] = '—'
        # Товары
        try:
            Product = apps.get_model('products', 'Product')
            context['products_count'] = Product.objects.count()
        except Exception:
            context['products_count'] = '—'
        # Кастомные метрики
        custom_metrics = []
        metric_paths = getattr(settings, 'EASYBOARD_CUSTOM_METRICS', [])
        for path in metric_paths:
            try:
                module_path, func_name = path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                func = getattr(module, func_name)
                metric = func()
                # metric должен быть dict с ключами 'title' и 'value'
                if isinstance(metric, dict) and 'title' in metric and 'value' in metric:
                    custom_metrics.append(metric)
                else:
                    custom_metrics.append({'title': path, 'value': metric})
            except Exception as e:
                custom_metrics.append({'title': path, 'value': f'Ошибка: {e}'})
        context['custom_metrics'] = custom_metrics
        return context

class SettingsView(TemplateView):
    template_name = 'easyboard/settings.html'

class APIDocsView(TemplateView):
    template_name = 'easyboard/api_docs.html' 