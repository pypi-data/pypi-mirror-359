# django-easyboard

Современная, легко кастомизируемая альтернатива стандартной Django Admin с красивым UI, расширенной интеграцией и гибкой настройкой.

## Публикация на PyPI

1. Установите twine и build:
   ```bash
   pip install build twine
   ```
2. Соберите пакет:
   ```bash
   python -m build
   ```
3. Загрузите на PyPI:
   ```bash
   twine upload dist/*
   ```

## Установка из PyPI

```bash
pip install django-easyboard
```

Добавьте в `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'easyboard',
]
```

## Особенности
- Dashboard с графиками и сводками
- Кастомизация через settings.py
- Интеграция с популярными Django-библиотеками
- Light/Dark тема
- Адаптивный дизайн

Документация в разработке. 