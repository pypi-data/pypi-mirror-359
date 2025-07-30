# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="FlaskKit",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-dotenv",
        "flask-cors"
    ],
    entry_points={
    'console_scripts': [
        'fk=crear_flask_app.__main__:main',
    ],
},
    author="Deiker Castillo",
    description="Generador de estructura base para proyectos Flask",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
