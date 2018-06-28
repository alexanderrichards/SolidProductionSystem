from sqlalchemy import Integer, TEXT
from productionsystem.sql.SQLTableBase import SmartColumn as Column
from productionsystem.sql.models.ParametricJobs import ParametricJobs

class SolidParametricJobs(ParametricJobs):
    __mapper_args__ = {'polymorphic_identity': 'solidparametricjobs'}
    solidsim_version = Column(TEXT, allowed=True)
    solidsim_macro = Column(TEXT, allowed=True)
    solidsim_nevents = Column(Integer, allowed=True)
    solidsim_inputfiletype = Column(TEXT, allowed=True)
    solidsim_output_lfn = Column(TEXT, allowed=True)
    saffron2_ro_version = Column(TEXT, allowed=True)
    saffron2_output_lfn = Column(TEXT, allowed=True)
    seed = Column(Integer, allowed=True)
    jobnumber_start = Column(Integer, allowed=True)
    day = Column(TEXT, allowed=True)
