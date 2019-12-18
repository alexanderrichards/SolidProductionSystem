"""Solid Parametric Jobs."""  # pylint: disable=invalid-name
import os
import tempfile
from copy import deepcopy
import jinja2
from sqlalchemy import Integer, TEXT
from productionsystem.sql.SQLTableBase import SmartColumn
from productionsystem.sql.models.ParametricJobs import ParametricJobs
from productionsystem.monitoring.diracrpc.DiracRPCClient import dirac_rpc_client


class SolidParametricJobs(ParametricJobs):
    """Solid Parametric Jobs."""

    __mapper_args__ = {'polymorphic_identity': 'solidparametricjobs'}
    solidsim_version = SmartColumn(TEXT, allowed=True)
    solidsim_macro = SmartColumn(TEXT, allowed=True)
    solidsim_nevents = SmartColumn(Integer, allowed=True)
    solidsim_inputmacro = SmartColumn(TEXT, allowed=True)
    solidsim_inputfiletype = SmartColumn(TEXT, allowed=True)
    solidsim_output_lfn = SmartColumn(TEXT, allowed=True)
    saffron2_ro_version = SmartColumn(TEXT, allowed=True)
    ro_macro = SmartColumn(TEXT, allowed=True)
    ro_inputmacro = SmartColumn(TEXT, allowed=True)
    ro_runNumber = SmartColumn(TEXT, allowed=True)
    ro_baselinetype = SmartColumn(TEXT, allowed=True)
    ro_input_lfndir = SmartColumn(TEXT, allowed=True)
    ro_output_lfndir = SmartColumn(TEXT, allowed=True)
#    saffron2_output_lfn = SmartColumn(TEXT, allowed=True)
    seed = SmartColumn(Integer, allowed=True)
    jobnumber_start = SmartColumn(Integer, allowed=True)
    saffron2_analysis_version = SmartColumn(TEXT, allowed=True)
    analysis_macro = SmartColumn(TEXT, allowed=True)
    analysis_inputmacro = SmartColumn(TEXT, allowed=True)
    analysis_output_lfndir = SmartColumn(TEXT, allowed=True)
    day = SmartColumn(TEXT, allowed=True)

    def _setup_dirac_job(self, DiracJob, tmp_runscript, tmp_filemanager):  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        job = DiracJob()
        if self.solidsim_version is not None:
            inputmacro = '/cvmfs/solidexperiment.egi.eu/el6/SolidSim/%s/solid_g4_sim/' \
                         'input_macros/%s' % (self.solidsim_version, self.solidsim_macro)
            if self.solidsim_inputmacro:
                with tempfile.NamedTemporaryFile(delete=False) as tempmacro:
                    tempmacro.write(self.solidsim_inputmacro)
                inputmacro = tempmacro.name

            runscript_template = jinja2.Environment(loader=jinja2.PackageLoader("solid"))\
                                       .get_template("mac.sh")\
                                       .render(id='%d.%d' % (self.request_id, self.id),  # pylint: disable=bad-option-value,bad-string-format-type
                                               macro=os.path.basename(inputmacro),
                                               version=self.solidsim_version,
                                               solidsim_inputfiletype=self.solidsim_inputfiletype,
                                               output_lfn=self.solidsim_output_lfn,
                                               seed=self.seed,
                                               nevents=self.solidsim_nevents)
            tmp_runscript.write(runscript_template)
            tmp_runscript.flush()

            if self.solidsim_macro == "cosmicsSim.mac":
                if self.solidsim_inputfiletype == 'atm-n':
                    inputdata_lfns = ['/solidexperiment.org/MC/cosmicGeneratorsFiles/2017/'
                                      'atm-n-1000files/Gordon-Events-%d.txt' % i
                                      for i in range(1, 1001)]
                elif self.solidsim_inputfiletype == 'muons':
                    inputdata_lfns = ['/solidexperiment.org/MC/cosmicGeneratorsFiles/2017/'
                                      'muons-1000files/Guan-Events-%d.txt' % i
                                      for i in range(1, 1001)]
                else:
                    inputdata_lfns = []
                inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
                job.setName("SoLid_{name}%(argjn)s".format(
                    name={'atm-n': 'N_', 'muons': 'mu_'}.get(self.solidsim_inputfiletype, '')))
                job.setPlatform('EL7')
                job.setDestination(['LCG.UKI-LT2-IC-HEP.uk', 'LCG.UKI-NORTHGRID-MAN-HEP.uk',
                                    'LCG.UKI-SOUTHGRID-OX-HEP.uk', 'LCG.BEgrid-ULB-VUB.be'])
                job.setInputSandbox([tmp_runscript.name, inputmacro])
                job.setParameterSequence('InputData', inputdata_lfns,
                                         addToWorkflow='ParametricInputData')
                job.setParameterSequence('argjn', range(self.jobnumber_start,
                                                        self.jobnumber_start + len(inputdata_lfns)),
                                         addToWorkflow=False)
                job.setParameterSequence('input_filenames', inputdata_filenames,
                                         addToWorkflow=False)
                job.setExecutable(os.path.basename(tmp_runscript.name),
                                  arguments='%(argjn)s %(input_filenames)s')
            else:
                job.setName("SoLid_Simulation_%s.%s" % (self.request_id, self.id))
                job.setPlatform('EL7')
                job.setDestination(['LCG.UKI-LT2-IC-HEP.uk', 'LCG.UKI-NORTHGRID-MAN-HEP.uk',
                                    'LCG.UKI-SOUTHGRID-OX-HEP.uk', 'LCG.BEgrid-ULB-VUB.be'])
                job.setInputSandbox([tmp_runscript.name, inputmacro])
                job.setExecutable(os.path.basename(tmp_runscript.name),
                                  arguments='%s.%s' % (self.request_id, self.id))
        elif self.saffron2_ro_version is not None:
            inputmacro = '/cvmfs/solidexperiment.egi.eu/el6/saffron2/%s/saffron2/ops/%s'\
                         % (self.saffron2_ro_version, self.ro_macro)
            if self.ro_inputmacro:
                with tempfile.NamedTemporaryFile(delete=False) as tempmacro:
                    tempmacro.write(self.ro_inputmacro)
                inputmacro = tempmacro.name

            if self.ro_baselinetype == "April-2018":
                ro_baseline_lfn = 'LFN:/solidexperiment.org/Data/phase1_BR2/' \
                                  'april2018-baselines.root'
                self.runNumber = 1030000  # pylint: disable=invalid-name, attribute-defined-outside-init
            else:
                ro_baseline_lfn = 'LFN:/solidexperiment.org/Data/phase1_BR2/' \
                                  'december2017-baselines.root'
                self.runNumber = 1010000  # pylint: disable=attribute-defined-outside-init

            runscript_template = jinja2.Environment(loader=jinja2.PackageLoader("solid"))\
                                       .get_template("rosim.sh")\
                                       .render(id='%d.%d' % (self.request_id, self.id),  # pylint: disable=bad-option-value,bad-string-format-type
                                               saffron2_version=self.saffron2_ro_version,
                                               macro=os.path.basename(inputmacro),
                                               ro_output_lfndir=self.ro_output_lfndir.format,
                                               ro_runNumber=self.runNumber)
            tmp_runscript.write(runscript_template)
            tmp_runscript.flush()

            input_directory_path = self.ro_input_lfndir
            with dirac_rpc_client("DataManagement/FileCatalog") as rpcclient:
                dir_content = deepcopy(rpcclient.listDirectory(input_directory_path, False))
            if not dir_content["OK"]:
                self.logger.error("Failed to contact DIRAC server for %s", input_directory_path)
                self.logger.error(dir_content['Message'])
                raise RuntimeError("Failed to contact DIRAC server for %s" % input_directory_path)

            if input_directory_path in dir_content['Value']['Failed']:
                self.logger.error("Could not access %s, maybe it doesn't exist?",
                                  input_directory_path)
                raise RuntimeError("Could not access %s, maybe it doesn't exist?"
                                   % input_directory_path)
            files = dir_content['Value']['Successful'][input_directory_path]['Files']

            inputdata_lfns = []
            for filename in files.keys():
                if not filename.endswith('.root'):
                    continue
    #            inputdata_lfns.append("LFN:%s" % os.path.join(directory_path, filename))
                inputdata_lfns.append(os.path.join(input_directory_path, filename))

            job_numbers = range(len(inputdata_lfns))
            inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
            # self.num_jobs = len(inputdata_filenames)

            job.setName("SoLid_ro_%(jobno)s")
            job.setExecutable(os.path.basename(tmp_runscript.name),
                              arguments='%(jobno)s %(inputdata_filename)s')
            job.setPlatform('EL7')
    #        job.setDestination('LCG.UKI-LT2-IC-HEP.uk')
            job.setDestination(['LCG.UKI-LT2-IC-HEP.uk', 'LCG.UKI-NORTHGRID-MAN-HEP.uk',
                                'LCG.UKI-SOUTHGRID-OX-HEP.uk', 'LCG.BEgrid-ULB-VUB.be'])
            job.setInputSandbox([tmp_runscript.name, inputmacro, ro_baseline_lfn])
    #        job.setInputData(['LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
            job.setParameterSequence('InputData', inputdata_lfns,
                                     addToWorkflow='ParametricInputData')
            job.setParameterSequence('jobno', job_numbers, addToWorkflow=False)
            job.setParameterSequence('inputdata_filename', inputdata_filenames, addToWorkflow=False)
        else:
            inputmacro = '/cvmfs/solidexperiment.egi.eu/el6/saffron2/%s/saffron2/ops/%s'\
                         % (self.saffron2_analysis_version, self.analysis_macro)
            if self.analysis_inputmacro:
                with tempfile.NamedTemporaryFile(delete=False) as tempmacro:
                    tempmacro.write(self.analysis_inputmacro)
                inputmacro = tempmacro.name

            analysis_output_lfndir = self.analysis_output_lfndir.format(day=self.day.replace("-",
                                                                                             "_"))
            runscript_template = jinja2.Environment(loader=jinja2.PackageLoader("solid"))\
                                       .get_template("runscript.sh")\
                                       .render(id='%d.%d' % (self.request_id, self.id),
                                               day=self.day.replace("-", "_"),
                                               saffron2_version=self.saffron2_analysis_version,
                                               macro=os.path.basename(inputmacro),
                                               analysis_output_lfndir=analysis_output_lfndir)
            tmp_runscript.write(runscript_template)
            tmp_runscript.flush()

            # DAY = '2017_12_15'
            directory_path = '/solidexperiment.org/Data/phase1_BR2/DAQ/days/%s/RO-data'\
                             % self.day.replace("-", "_")

            with dirac_rpc_client("DataManagement/FileCatalog") as rpcclient:
                dir_content = deepcopy(rpcclient.listDirectory(directory_path, False))
            if not dir_content["OK"]:
                self.logger.error("Failed to contact DIRAC server for %s", directory_path)
                self.logger.error(dir_content['Message'])
                raise RuntimeError("Failed to contact DIRAC server for %s" % directory_path)

            if directory_path in dir_content['Value']['Failed']:
                self.logger.error("Could not access %s, maybe it doesn't exist?", directory_path)
                raise RuntimeError("Could not access %s, maybe it doesn't exist?" % directory_path)

            # doesn't look like a walk is needed.
            # subdirs = dir_content['Value']['Successful'][directory_path]['SubDirs']
            files = dir_content['Value']['Successful'][directory_path]['Files']

            inputdata_lfns = []
            for filename in files.keys():                   
                if not filename.endswith('.sbf.bz2') and '.'.join((filename, 'bz2')) in files:
                    continue
    #            inputdata_lfns.append("LFN:%s" % os.path.join(directory_path, filename))
                inputdata_lfns.append(os.path.join(directory_path, filename))

            job_numbers = range(len(inputdata_lfns))
            inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
            # self.num_jobs = len(inputdata_filenames)

            job.setName("SoLid_data_%(jobno)s")
            job.setExecutable(os.path.basename(tmp_runscript.name),
                              arguments='%(jobno)s %(inputdata_filename)s')
            job.setPlatform('ANY')
    #        job.setDestination('LCG.BEgrid-ULB-VUB.be')
            job.setDestination(['LCG.UKI-LT2-IC-HEP.uk', 'LCG.UKI-NORTHGRID-MAN-HEP.uk',
                                'LCG.UKI-SOUTHGRID-OX-HEP.uk', 'LCG.BEgrid-ULB-VUB.be'])
            job.setInputSandbox([tmp_runscript.name, inputmacro,
                                 'LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
    #        job.setInputData(['LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
            # job.setParameterSequence('InputData', inputdata_lfns,
            #                         addToWorkflow='ParametricInputData')
            job.setParameterSequence('InputSandbox', [':'.join(('LFN', lfn))
                                                      for lfn in inputdata_lfns],
                                     addToWorkflow='ParametricInputSandbox')
            job.setParameterSequence('jobno', job_numbers, addToWorkflow=False)
            job.setParameterSequence('inputdata_filename', inputdata_filenames,
                                     addToWorkflow=False)
        return job
