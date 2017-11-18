from setuptools import setup, find_packages
from forecast import __version__


if __name__ == '__main__':
    setup(
            name='forecast',
            version=__version__,
            description='Python wrapper for R-forecast',
            url='https://github.yandex-team.ru/ferres/forecast/',
            author='Maxim Kochurov',
            author_email='ferres@yandex-team.ru',
            install_requires=['six', 'rpy2>=2.4', 'pandas'],
            packages=find_packages(),
    )