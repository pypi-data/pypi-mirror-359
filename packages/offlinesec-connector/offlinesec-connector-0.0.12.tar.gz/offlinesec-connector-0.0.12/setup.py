import offlinesec_connector
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='offlinesec-connector',
    version=offlinesec_connector.__version__,
    packages=find_packages(),
    url='https://offlinesec.com',
    author='Offline Security',
    author_email='info@offlinesec.com',
    description='Offline Security Connector',
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={'console_scripts': ['offlinesec_connector = offlinesec_connector.offlinesec_connector:main',
                                      'offlinesec_conn_settings = offlinesec_connector.mng_offlinesec_conn:main',
], },
    install_requires=required,
    include_package_data=True
)
# packages=['offlinesec_client'],