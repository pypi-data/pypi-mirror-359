from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aplicacion_de_ventas",  # nombre sin tildes ni mayúsculas raras
    version="0.1.3",
    author="Marcello Paolo Massucco Bustios",
    author_email="marcello.mass@gmail.com",
    description="Paquete para gestionar ventas, precios, impuestos y descuentos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu_usuario/gestor_ventas",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">3.6",
)