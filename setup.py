import io
import os
from setuptools import setup


# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='pynot',
    version='1.0.0',
    packages=['pynot', 'pynot.utils', 'pynot.migrations'],
    install_requires=[
        'django',
        'djangorestframework',
        'drf-writable-nested',
        'django-filter',
        'factory-boy',
        'Faker',
        'django-rest-assured',
        'celery',
    ],
    python_requires='>=3.5.0',
    url='https://github.com/intelligenia/pynot',
    license='Apache 2.0',
    author='José Carlos Calvo Tudela',
    author_email='jcctudela@gmail.com',
    description='Django library to manage notifications emitted by an application',
    long_description=long_description,
    keywords=['emails', 'notifications', 'notification manager', 'REST notification config'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
    ],
)
