#!/usr/bin/python
#########################################################
# currentStackedHist.py
# 2/25/2015 created
#
########################################################

'''
   read in an RT dump file, and generate stacked histograms,
   one bar for each queue, with stacking to indicate ticket status.

   INPUTS: output of RT search (BH: "manual queues, non-antique
        w/Org") downloaded by the RT Feed/Spreadsheet feature. Takes a
        long time to download.

   OUTPUT: One stacked histogram plot

   TO RUN: currently, you need to edit the source dump file name.
        Should taken as command line argument.

   EXAMPLES OF OUTPUT: http://www.slac.stanford.edu/~bhecker/RT_metrics/

'''
################################################################
# FIXME AND IMPROVEMENTS
#
# * output the date of the extract / date of last data point - 
#     analysis won't always run in the same time frame as the extract
################################################################


def generate_index_page(starttime):
    pageCode='<html><head><title>RT current histograms, generated %s</title> </head>\n' % starttime
    pageCode += '<body><h1>RT current histogram</h1>\n' 
    pageCode += '<body><h3>generated %s </h3>\n' % starttime
    pageCode += '<ol>'
    pageCode += '<li><a href="'+'currentHistogram'+'.png">Current stacked histogram</a></li>\n'
    pageCode += '</ol></body></html>'
    return(pageCode)

import pandas as pd;
import numpy as np;
#import matplotlib as mpl;
## next line must occur before any mpl etc commands or imports
## sometimes needed for hardcopy output
#mpl.use("Qt4Agg")

#TO RUN INTERACTIVE, THIS COMMAND MUST RUN perhaps in its own cell before this program
# %matplotlib inline
# symptom is kernel hang

import matplotlib.pyplot as plt;
import datetime, os; 

STATUSES = ['new','open','stalled','resolved','rejected','deleted']
STARTTIME = datetime.datetime.today().isoformat()[0:-7]

print "Started", STARTTIME
print "Backend:", plt.matplotlib.rcParams['backend']
print "Interactive:", plt.isinteractive()

STATUSES = ['new','open','stalled','resolved','rejected','deleted']
STARTTIME = datetime.datetime.today().isoformat()[0:-7]

##queues of interest
AllQueue = [ 'Authors','AUTHORS_claim_manual','AUTHORS_general',\
            'CONF_add+cor', 'CONF_add_user', 'Feedback',\
            'HEP', 'HEP_add_user', 'HEP_cor_user','HEP_ref', 'HEP_ref_user', \
            'HEP_curation','HEPNAMES', 'Inspire-References', 'INST_add+cor', 'JOBS']

## dirx is the root directory for input and output
dirx = 'c:\\Users\\bhecker\\My Documents\\INSPIRE\\RT metrics\\2015-02-13_analyses\\'
inx = dirx+'2015-02-18_vm2_dump.tsv'

EntireSheet=pd.read_csv(inx, delimiter='\t', index_col=None, na_values=['NA'] )
#entireSheetQI = EntireSheet.set_index('Status')

### create output directory for graphs
pathx = dirx + 'currentHisto-'+STARTTIME.replace(':','')

## odd structure, but avoids race condition and avoids file/dir confusion
try: 
    os.makedirs(pathx)
except OSError:
    if not os.path.isdir(pathx):
        raise

########################################################
# setup the accumulating structure
qBin = { }
for q in AllQueue:
    qBin[q] =  { 'new':0,'open':0,'stalled':0,'resolved':0,'rejected':0,'deleted':0 }

########################################################
## do the counting

for i in range(0, len(EntireSheet)):
    #if row['Status'] != 'Resolved' and row['Status'] != 'Deleted':
    # only record entries and build bins for queues listed in AllQueues array
    if EntireSheet.iloc[i]['QueueName'] in qBin:
        qBin[EntireSheet.iloc[i]['QueueName']][EntireSheet.iloc[i]['Status']] += 1
    # well, that was easy.

## Create the dataframe, then transpose it
qf = pd.DataFrame(qBin).T

## values needed for plotting
indx = np.arange(len(qBin))

## plot ################################################
## #get_ipython().magic(u'matplotlib inline')
print plt.matplotlib.rcParams['backend']

# http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.bar
plt.figure(figsize=[14,7]);

wx = .5; #5; # bar width
#barh(bottom, width, height=0.8, left=None, hold=None, **kwargs)
pNew = plt.barh(indx, qf['new'], height=wx, color='r', linewidth=0 )
pOpen = plt.barh(indx, qf['open'], height=wx, color='g', left=qf['new'], linewidth=0)
pStalled = plt.barh(indx, qf['stalled'], height=wx, color='b', left=qf['new']+qf['open'], linewidth=0)  



plt.ylabel("number of tickets"); 
ti = "Current Queue Status, last entry: %s" % EntireSheet.at[len(EntireSheet)-1,'Created']
plt.title(ti)
plt.yticks(indx+wx/2., qf.index)
plt.legend((pNew, pOpen, pStalled), ('new', 'open', 'stalled') )
## if interactive, uncomment
#plt.show()

## if hardcopy, uncomment following 5 lines
plt.savefig(pathx+'\\currentHistogram.png', dpi=140, facecolor='w', format='png')
plt.close()

OUTX = open(pathx+'\\index.html','w')
OUTX.write(generate_index_page(STARTTIME ) )
OUTX.close()

print "End time:", datetime.datetime.today().isoformat()


