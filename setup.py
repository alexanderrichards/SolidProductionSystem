"""Setuptools Module."""
from setuptools import setup, find_packages

setup(
    name="solidproductionsystem",
    version="0.1",
    packages=find_packages(),
    install_requires=['productionsystem'],
    entry_points={
        'dbmodels': ['parametricjobs = solidproductionsystem.ParametricJobs:SolidParametricJobs'],
#                     'requests = productionsystem.sql.models.Requests:Requests'],
#        'webapp.services': ['htmlpageserver = productionsystem.webapp.services.HTMLPageServer:HTMLPageServer'],
        'webapp.streams': ['newrequest = solidproductionsystem.resource_utils:newrequest_streams'],
        'monitoring.dirac': ['jobfactory = solidproductionsystem.jobfactory:jobfactory'],
        'daemons': ['webapp = solidproductionsystem.WebApp:SolidWebApp']
    },
    # metadata for upload to PyPI
    author="Alexander Richards",
    author_email="a.richards@imperial.ac.uk",
    description="Solid Production System Plugin",
    license="MIT",
    keywords="production",
    url="https://github.com/alexanderrichards/ProductionSystem"
)
