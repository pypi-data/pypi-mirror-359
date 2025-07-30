from django.conf import settings

EASYBOARD = getattr(settings, 'EASYBOARD', {
    'SITE_TITLE': 'EasyBoard Admin',
    'BRAND_LOGO': '',
    'SHOW_STATS': True,
    'ENABLE_IMPORT_EXPORT': False,
    'ENABLE_MPTT': False,
    'CUSTOM_DASHBOARD_CARDS': [],
})

EASYBOARD_CUSTOM_METRICS = getattr(settings, 'EASYBOARD_CUSTOM_METRICS', []) 