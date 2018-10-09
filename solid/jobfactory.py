import os
from copy import deepcopy
import logging

import jinja2

from productionsystem.monitoring.diracrpc.DiracRPCClient import dirac_rpc_client


def jobfactory(parametricjob, dirac_jobcls, tmp_runscript):
    logger = logging.getLogger(__name__)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), 'resources')))
    tmp_runscript.write(template_env.get_template('run_scripts/runscript.sh').render())
    tmp_runscript.flush()

    #DAY = '2017_12_15'
    directory_path = '/solidexperiment.org/Data/phase1_BR2/DAQ/days/%s/RO-data' % parametricjob.day.replace("-", "_")

    with dirac_rpc_client("DataManagement/FileCatalog") as rpcclient:
#        rpcclient = RPCClient( "DataManagement/FileCatalog" )
#        print rpcclient.listDirectory
#        help(rpcclient.listDirectory)
        dir_content = deepcopy(rpcclient.listDirectory(directory_path, False))
    if not dir_content["OK"]:
        logger.error("Failed to contact DIRAC server for %s", directory_path)
        logger.error(dir_content['Message'])
        return []

    if directory_path in dir_content['Value']['Failed']:
        logger.error("Could not access %s, maybe it doesn't exist?", directory_path)
        return []

    # doesn't look like a walk is needed.
    # subdirs = dir_content['Value']['Successful'][directory_path]['SubDirs']
    files = dir_content['Value']['Successful'][directory_path]['Files']

    inputdata_lfns = []
    for filename in files.keys():
        inputdata_lfns.append("LFN:%s" % os.path.join(directory_path, filename))

    job_numbers = range(len(inputdata_lfns))
    inputdata_filenames = [os.path.basename(lfn) for lfn in inputdata_lfns]
    days = [parametricjob.day.replace("-", "_")] * len(inputdata_lfns)
    j = dirac_jobcls()
    j.setName("SoLid_data_%(jobno)s")
    j.setExecutable(os.path.basename(tmp_runscript.name), arguments='%(jobno)s %(inputdata_filename)s %(day)s')
    j.setPlatform('ANY')
    j.setDestination('LCG.UKI-LT2-IC-HEP.uk')
    j.setInputSandbox([tmp_runscript.name, '/cvmfs/solidexperiment.egi.eu/el6/saffron2/v1.21/saffron2/ops/onlineMonitoringBR2.txt'])
    j.setInputData(['LFN:/solidexperiment.org/Data/phase1_BR2/baselines.root'])
    j.setParameterSequence('InputData', inputdata_lfns, addToWorkflow='ParametricInputData')
    j.setParameterSequence('jobno', job_numbers, addToWorkflow=False)
    j.setParameterSequence('inputdata_filename', inputdata_filenames, addToWorkflow=False)
    j.setParameterSequence('day', days, addToWorkflow=False)
    return [j]
