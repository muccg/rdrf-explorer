import os
from setuptools import setup
from viewer import __version__

setup(
    name = "django-mongodb-viewer",
    version = __version__,
    author = "Maciej Radochonski (CCG)",
    author_email = "mradochonski@ccg.murdoch.edu.au",
    description = ("MongoDB query tool"),
    url = "https://bitbucket.org/ccgmurdoch/django-mongodb-viewer",
    packages=['viewer'],
    classifiers=[
        "Topic :: Utilities",
    ],
    install_requires=[
        'Django>=1.5',
    ],
    include_package_data=True,
    zip_safe = False,
)