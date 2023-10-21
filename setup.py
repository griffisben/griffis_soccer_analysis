from setuptools import setup

setup(
    name='griffis_soccer_analysis',
    version='1.0.2',

    url='https://github.com/griffisben/griffis_soccer_analysis',
    author='Ben Griffis',
    author_email='1.fcgriffisconsulting@gmail.com',
    
    packages=['griffis_soccer_analysis'],
    modules=['similarity','fbref_code'],
    install_requires=['pandas','matplotlib','seaborn','numpy','scikit-learn','scipy','pillow','selenium','clipboard'],
)
