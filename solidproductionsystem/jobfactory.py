import os
import jinja2
from tempfile import NamedTemporaryFile

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(__file__), 'resources')))
def jobfactory(parametricjob, dirac_jobcls):
    sublist, sublist1, sublist2, sublist3 = [], [], [], []
    nput = 0
    jn = parametricjob.jobnumber_start
    with NamedTemporaryFile(delete=False) as file_:
        filename = file_.name
        file_.write(template_env.get_template('macN.sh').render({'job': parametricjob}))
    lfn_base = 'LFN:/solidexperiment.org/MC/cosmicGeneratorsFiles/2017'
    if parametricjob.solidsim_inputfiletype == 'atm-n':
        lfn_base = os.path.join(lfn_base, 'atm-n', 'Gordon-Events.out.')
    elif parametricjob.solidsim_inputfiletype == 'muons-reduced':
        lfn_base = os.path.join(lfn_base, 'muons-reduced', 'Guan-Events-reduced.out.')        
    for ii in range(parametricjob.num_jobs):
        nput+=1
        jn+=1
        sublist+=[lfn_base + "%d" % nput]
        sublist1+=[jn]
        sublist2+=[nput]
        sublist3+=[parametricjob.seed]
    j=dirac_jobcls()
    j.setName("SoLid_nu_%(argjn)s")
    j.setPlatform('ANY')
    j.setDestination('LCG.UKI-LT2-IC-HEP.uk') 
    j.setInputSandbox([filename])
    j.setParameterSequence('InputData', sublist, addToWorkflow='ParametricInputData')
    j.setParameterSequence('argjn', sublist1, addToWorkflow=False)
    j.setParameterSequence('argnput', sublist2, addToWorkflow=False)
    j.setParameterSequence('argsd', sublist3, addToWorkflow=False)
    j.setExecutable('macN.sh', arguments='%(argjn)s %(argnput)s %(argsd)s')
    return [j]
