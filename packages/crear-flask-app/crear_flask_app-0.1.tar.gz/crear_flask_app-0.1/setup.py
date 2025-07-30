from setuptools import setup, find_packages

setup(
    name="crear_flask_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-dotenv",
        "flask-cors"
    ],
    entry_points={
        'console_scripts': [
            'create-appflask-app=crear_flask_app.__main__:crear_estructura',
        ],
    },
    author="Tu Nombre",
    description="Generador de estructura base para proyectos Flask",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
)
