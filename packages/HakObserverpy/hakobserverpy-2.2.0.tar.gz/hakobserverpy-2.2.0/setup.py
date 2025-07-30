import platform
from setuptools import setup, find_packages

setup(
    name='HakObserverpy', 
    version='2.2.0',  
    description='A package connect endpoints to the Hakware Application', 
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',
    author='Jacob O\'Brien',  
    packages=find_packages(),  
    install_requires=[  
    'requests',
    'psutil',
    'lxml[html_clean]',
    'requests_html' ,
    'pywin32'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
)
