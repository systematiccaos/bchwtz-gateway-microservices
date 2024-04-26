#import os
from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
    
setup(name='ble_daemon',
      version='v2.0.0',
      author='Marius Scheffel',
      author_email = 'scheffel.mariusjohannes@fh-swf.de',
      description = "microservices to communicate with BLE Devices",
      long_description = long_description,
      long_description_content_type = "text/markdown",
      url = 'https://github.com/bchwtz/bchwtz-gateway.git',
      packages=find_packages() ,
      include_package_data=True,
      install_requires=required,
      python_requires=">=3.6"
      )