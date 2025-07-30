import setuptools
from pathlib import Path

setuptools.setup(
    name='django-easyboard',
    version='0.1.0',
    description='Современная, легко кастомизируемая альтернатива стандартной Django Admin',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='MzMPrO',
    author_email='mirahmadzoxidov@gmail.com',
    url='https://github.com/MzMProger/django-easyboard',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    python_requires='>=3.7',
    license='MIT',
    keywords='django admin dashboard bootstrap tailwind mptt import-export constance drf',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
) 