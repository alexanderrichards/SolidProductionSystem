from sqlalchemy import Integer, TEXT
from productionsystem.sql.SQLTableBase import SmartColumn
from productionsystem.sql.models.ParametricJobs import ParametricJobs

class SolidParametricJobs(ParametricJobs):
    __mapper_args__ = {'polymorphic_identity': 'solidparametricjobs'}
    solidsim_version = SmartColumn(TEXT, allowed=True)
    solidsim_macro = SmartColumn(TEXT, allowed=True)
    solidsim_nevents = SmartColumn(Integer, allowed=True)
    solidsim_inputfiletype = SmartColumn(TEXT, allowed=True)
    solidsim_output_lfn = SmartColumn(TEXT, allowed=True)
    saffron2_ro_version = SmartColumn(TEXT, allowed=True)
    saffron2_output_lfn = SmartColumn(TEXT, allowed=True)
    seed = SmartColumn(Integer, allowed=True)
    jobnumber_start = SmartColumn(Integer, allowed=True)
    day = SmartColumn(TEXT, allowed=True)


    def _setup_dirac_job(self, job, tmp_runscript):
        pass
