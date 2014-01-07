from setuptools import setup, find_packages

version = "2.0.0"

setup(
    name="CMStats",
    version=version,
    packages=find_packages(),
    install_requires=['tornado==2.2', 'sqlalchemy', 'mako', 'pygeoip'],
    entry_points={
        'console_scripts': [
            'cmstats.server=cmstats.app:run_server',
        ],
    },
    include_package_data=True,
)
