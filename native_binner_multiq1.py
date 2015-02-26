#!/usr/bin/python
#########################################################
# native_binner_multiq1.py
# 2/13/2015 created
#
######################################################

'''
   read in an RT dump file, and generate "binner" plots
   comparable to the onces generated by running the older
   "aggregator/binner" python scripts, and generating graphs
   by hand in excel. 

   INPUTS: output of RT search (BH: "manual queues, non-antique
        w/Org") downloaded by the RT Feed/Spreadsheet feature. Takes a
        long time to download.

   OUTPUT: a binner plot of imputing queue size over time, plus a
        index.html page in the same directory, for ease of browsing.

   TO RUN: currently, you need to edit the source dump file name.
        Should taken as command line argument. 

'''
################
# TO-DO
#
# * output the date of the extract / date of last data point - 
#     analysis won't always run in the same time frame as the extract
# * would be better to do histos, especially stacked histos where the stack
#     was "ticket status". 
#


def generate_index_page(starttime, queuelist):
    pageCode='<html><head><title>RT bin graphs, generated %s</title> </head>\n' % starttime
    pageCode += '<body><h1>RT bin graphs</h1>\n'
    pageCode += '<body><h3>generated %s </h3>\n' % starttime
    pageCode += '<ol>'
    for q in queuelist:
        pageCode += '<li><a href="'+q+'.png">'+q+'</a></li>\n'
    pageCode += '</ol></body></html>'
    return(pageCode)

import pandas as pd;
import numpy as np;
import matplotlib as mpl;
## next line must occur before any mpl etc commands or imports
#mpl.use("Qt4Agg")

import matplotlib.pyplot as plt;
import datetime, os; 

STARTTIME = datetime.datetime.today().isoformat()[0:-7]
print "Start time:", STARTTIME
print "Display mode:", plt.matplotlib.rcParams['backend']

##queues of interest
QueueList = [ 'Authors','AUTHORS_claim_manual','AUTHORS_general',\
            'CONF_add+cor', 'CONF_add_user', 'Feedback',\
            'HEP', 'HEP_add_user', 'HEP_cor_user','HEP_ref', 'HEP_ref_user', \
            'HEP_curation', 'Inspire-References', 'INST_add+cor', 'JOBS']

## for testing
QueueList = [ 'INST_add+cor' ]

## dirx is the root directory for input and output
dirx = 'c:\\Users\\bhecker\\My Documents\\INSPIRE\\RT metrics\\2015-02-13_analyses\\'
inx = dirx+'2015-02-18_vm2_dump.tsv'

EntireSheet=pd.read_csv(inx, delimiter='\t', index_col=None, na_values=['NA'] )
entireSheetQI = EntireSheet.set_index('QueueName')

BIN_START_EPOCH = pd.datetime(2013, 5, 1)  ## modern epoch, i.e., point at which analysis starts being meaningful

#define weekly range to be used in defining binning dataframes.
rng = pd.date_range(start=BIN_START_EPOCH, end=datetime.date.today(), freq='w')

### create output directory for graphs
pathx = dirx + 'graph-'+STARTTIME.replace(':','')

## odd structure, but avoids race condition and avoids file/dir confusion
try: 
    os.makedirs(pathx)
except OSError:
    if not os.path.isdir(pathx):
        raise

####################################
## do the counting

for thisQueueName in QueueList:
    # extract only rows that belong to the selected queue
    ThisQueueFrame = entireSheetQI.loc[thisQueueName]
    print "===> ",thisQueueName,"<========="
    ## I didn't see a way to extract the ID column if it was the index
    qFrame = ThisQueueFrame.reset_index()
    idKeys = qFrame['id']
    # set up fresh bin (Pandas dataframe)
    tsbin = pd.Series(0, index=rng)
    qFrame = qFrame.set_index('id')

    for k in idKeys:
        c = qFrame.loc[k]['Created']
        y, m, d = c[:10].split('-')
        c = pd.datetime(int(y),int(m),int(d) ) 
        r = qFrame.loc[k]['Resolved'] 
        if r == "Not set": 
            r = pd.datetime(2020, 12, 31)
        else:
            y, m, d = r[:10].split('-')
            r = pd.datetime(int(y), int(m), int(d) )

        for beginBin in tsbin.index:
            ## bin is an entire week -- careful comparison
            ## ticket starts before or equal to "endBin" date, 
            ## and ends on or after the beginBin date. 

            if c <= beginBin+datetime.timedelta(days=6) and r >= beginBin:
                tsbin.loc[beginBin] += 1

    ##print "tsbin tail/head", tsbin.head(), tsbin.tail()

    ## plot ##############

    #get_ipython().magic(u'matplotlib inline')
    #print plt.matplotlib.rcParams['backend']
    plt.figure();

    plt.ylabel("number of unresolved tickets"); 
    plt.title(thisQueueName + " Queue Size")
    tsbin.plot(kind='line')
    #next line forces the y axis to originate at zero
    plt.ylim(0,)

    # how to make the directory stick for saving the image??

    plt.savefig(pathx+'\\'+thisQueueName+'.png', dpi=140, facecolor='w', format='png')
    plt.close()

OUTX = open(pathx+'\\index.html','w')
OUTX.write(generate_index_page(STARTTIME, QueueList ) )
OUTX.close()

print "End time:", datetime.datetime.today().isoformat()
