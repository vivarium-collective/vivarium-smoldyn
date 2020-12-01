# A python script for scanning a parameter
import os



simnum=0
for rxnrate in [0.01,0.02,0.05,0.1,0.2,0.5,1]:
	simnum+=1
	string='smoldyn vivarium_smoldyn/examples/paramscan.txt --define RXNRATE=%f --define SIMNUM=%i -tqw' %(rxnrate,simnum)
	print(string)
	os.system(string)



import ipdb; ipdb.set_trace()
# ModuleNotFoundError: No module named 'smoldyn._smoldyn'