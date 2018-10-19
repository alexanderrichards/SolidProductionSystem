import os
import random
from copy import deepcopy
import jinja2
from sqlalchemy import Integer, TEXT
from productionsystem.sql.SQLTableBase import SmartColumn
from productionsystem.sql.models.ParametricJobs import ParametricJobs
from productionsystem.monitoring.diracrpc.DiracRPCClient import dirac_rpc_client

class SolidParametricJobs(ParametricJobs):
    __mapper_args__ = {'polymorphic_identity': 'solidparametricjobs'}
    solidsim_version = SmartColumn(TEXT, allowed=True)
    solidsim_macro = SmartColumn(TEXT, allowed=True)
    solidsim_nevents = SmartColumn(Integer, allowed=True)
    solidsim_inputmacro = SmartColumn(TEXT, allowed=True)
    solidsim_inputfiletype = SmartColumn(TEXT, allowed=True)
    solidsim_output_lfn = SmartColumn(TEXT, allowed=True)
    saffron2_ro_version = SmartColumn(TEXT, allowed=True)
    saffron2_output_lfn = SmartColumn(TEXT, allowed=True)
    seed = SmartColumn(Integer, allowed=True)
    jobnumber_start = SmartColumn(Integer, allowed=True)
    saffron2_analysis_version = SmartColumn(TEXT, allowed=True)
    analysis_macro = SmartColumn(TEXT, allowed=True)
    analysis_inputmacro = SmartColumn(TEXT, allowed=True)
    day = SmartColumn(TEXT, allowed=True)


    def _setup_dirac_job(self, job, tmp_runscript):
        if self.solidsim_version is not None:
            inputmacro = '/cvmfs/solidexperiment.egi.eu/el6/SolidSim/%s/solid_g4_sim/input_macros/%s' %(self.solidsim_version, self.solidsim_macro)
            if self.solidsim_inputmacro:
                with tempfile.NamedTemporaryFile(delete=False) as tempmacro:
                    tempmacro.write(self.solidsim_inputmacro)
                inputmacro = tempmacro.name

            runscript_template = jinja2.Environment(loader=jinja2.PackageLoader("solid"))\
                                       .get_template("mac.sh")\
                                       .render(macro=os.path.basename(inputmacro),
                                               version=self.solidsim_version,
                                               output_lfn=self.solidsim_output_lfn,
                                               seed=self.seed,
                                               nevents=self.solidsim_nevents)
            tmp_runscript.write(runscript_template)
            tmp_runscript.flush()

            if self.solidsim_macro == "cosmicsSim.mac":
                inputdata_lfns = ['/solidexperiment.org/MC/cosmicGeneratorsFiles/2017/atm-n-1000files/Gordon-Events-%d.txt' % i for i in range(1000)]
                inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
                job.setName("SoLid_{name}%(argjn)s".format(name={'atm-n': 'N_',
                                                                 'muons-reduced': 'mu_'}.get(self.solidsim_inputfiletype, '')))
                job.setPlatform('ANY')
                job.setDestination('ANY')
                job.setInputSandbox([tmp_runscript.name, inputmacro])
                job.setParameterSequence('InputData', inputdata_lfns, addToWorkflow='ParametricInputData')
                job.setParameterSequence('argjn', range(self.jobnumber_start, self.jobnumber_start + len(inputdata_lfns)), addToWorkflow=False)
                job.setParameterSequence('input_filenames', inputdata_filenames, addToWorkflow=False)
                job.setExecutable(os.path.basename(tmp_runscript.name), arguments='%(argjn)s %(input_filenames)s')
            else:
                job.setName("SoLid_Simulation_%s.%s" % (self.request_id, self.id))
                job.setPlatform('ANY')
                job.setDestination('ANY')
                job.setInputSandbox([tmp_runscript.name, inputmacro])
                job.setExecutable(os.path.basename(tmp_runscript.name), arguments='%s.%s' % (self.request_id, self.id))                
        else:
            day = self.day
            inputmacro = '/cvmfs/solidexperiment.egi.eu/el6/saffron2/%s/saffron2/ops/%s' % (self.saffron2_analysis_version, self.analysis_macro)
            if self.analysis_inputmacro:
                with tempfile.NamedTemporaryFile(delete=False) as tempmacro:
                    tempmacro.write(self.analysis_inputmacro)
                inputmacro = tempmacro.name

            runscript_template = jinja2.Environment(loader=jinja2.PackageLoader("solid"))\
                                       .get_template("runscript.sh")\
                                       .render(day=day.replace("-", "_"),
                                               saffron2_version=self.saffron2_analysis_version,
                                               macro=os.path.basename(inputmacro))
            tmp_runscript.write(runscript_template)
            tmp_runscript.flush()

            #DAY = '2017_12_15'
            directory_path = '/solidexperiment.org/Data/phase1_BR2/DAQ/days/%s/RO-data' % self.day.replace("-", "_")

            with dirac_rpc_client("DataManagement/FileCatalog") as rpcclient:
                dir_content = deepcopy(rpcclient.listDirectory(directory_path, False))
            if not dir_content["OK"]:
                self.logger.error("Failed to contact DIRAC server for %s", directory_path)
                self.logger.error(dir_content['Message'])
                raise RuntimeError("Failed to contact DIRAC server for %s", directory_path)

            if directory_path in dir_content['Value']['Failed']:
                self.logger.error("Could not access %s, maybe it doesn't exist?", directory_path)
                raise RuntimeError("Could not access %s, maybe it doesn't exist?", directory_path)

            # doesn't look like a walk is needed.
            # subdirs = dir_content['Value']['Successful'][directory_path]['SubDirs']
            files = dir_content['Value']['Successful'][directory_path]['Files']

            inputdata_lfns = []
            for filename in files.keys():
                if not filename.endswith('.sbf'):
                    continue
    #            inputdata_lfns.append("LFN:%s" % os.path.join(directory_path, filename))
                inputdata_lfns.append(os.path.join(directory_path, filename))

            job_numbers = range(len(inputdata_lfns))
            inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
            self.num_jobs = len(inputdata_filenames)

            job.setName("SoLid_data_%(jobno)s")
            job.setExecutable(os.path.basename(tmp_runscript.name), arguments='%(jobno)s %(inputdata_filename)s')
            job.setPlatform('ANY')
    #        job.setDestination('LCG.UKI-LT2-IC-HEP.uk')
            job.setDestination('ANY')
            job.setInputSandbox([tmp_runscript.name, inputmacro, 'LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
    #        job.setInputData(['LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
            job.setParameterSequence('InputData', inputdata_lfns, addToWorkflow='ParametricInputData')
            job.setParameterSequence('jobno', job_numbers, addToWorkflow=False)
            job.setParameterSequence('inputdata_filename', inputdata_filenames, addToWorkflow=False)
        return job
