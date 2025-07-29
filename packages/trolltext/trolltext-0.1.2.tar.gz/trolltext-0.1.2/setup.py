from setuptools import setup, find_packages

setup(
    name='trolltext',          # имя пакета
    version='0.1.2',
    description='Текстовые стили с множеством шрифтов',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='G3tfun',
    author_email='no-reply@example.com',
    url='https://github.com/G3tfun/trolltext',  # если есть
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)