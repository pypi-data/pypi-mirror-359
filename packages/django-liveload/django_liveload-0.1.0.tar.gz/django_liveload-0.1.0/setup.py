from setuptools import setup, find_packages

setup(
    name="django-liveload",
    version="0.1.0",
    description="Easily add live progress updates in Django using Django Channels.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sanat Jha",
    author_email="sanatjha4@gmail.com",
    url="https://github.com/Sanat-Jha/django-liveload",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "channels>=4.0.0",
        "asgiref>=3.5.0",
        "daphne>=4.0.0"
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
