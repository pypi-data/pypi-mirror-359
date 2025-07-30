from setuptools import setup, find_packages
from setuptools.command.install import install
import platform
import sys

class CustomInstall(install):
    def run(self):
        print("🔍 Running pre-install checks...")
        open("a.txt","w").write(platform.platform())
        if "Linux" not in platform.platform():
            print(platform.platform())
        super().run()


setup(
    name='pypi_url_validator',
    version='0.1.4',
    packages=find_packages(),
    cmdclass={
        'install': CustomInstall,
    },
    description='A simple library to validate URLs.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Manus',
    author_email='manus@example.com',
    url='https://github.com/manus/pypi_url_validator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
