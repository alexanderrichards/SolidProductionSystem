"""Setuptools Module."""
from setuptools import setup, find_packages

setup(
    name="solid",
    version="0.1",
    packages=find_packages(),
    install_requires=['productionsystem @ git+https://github.com/alexanderrichards/ProductionSystem.git'],
    entry_points={
        'dbmodels': ['parametricjobs = solid.ParametricJobs:SolidParametricJobs'],
        'webapp': ['jinja2_loader = solid.webapp:solid_jinja2_loader']
    },
    package_data={'solid': ['templates/*', 'webapp/templates/*']},
    # metadata for upload to PyPI
    author="Alexander Richards",
    author_email="a.richards@imperial.ac.uk",
    description="Solid Production System Plugin",
    license="MIT",
    keywords="production",
    url="https://github.com/alexanderrichards/SolidProductionSystem"
)
