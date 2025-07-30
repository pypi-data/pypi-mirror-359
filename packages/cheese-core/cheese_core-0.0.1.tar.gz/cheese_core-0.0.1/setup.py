from setuptools import setup,find_packages
setup(name='cheese_core',
version='0.0.1',
author='coco',
author_email='3560000009@qq.com',
description=f'A Cheese',
long_description=open('README.md','r',encoding='utf-8').read(),
long_description_content_type='text/markdown',  
url='https://github.com/topcoco',
packages=find_packages(),
license='Apache-2.0',
keywords=['cheese','auto'],
install_requires=[]
)
