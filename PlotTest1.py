import pandas as pd;
import numpy as np;
import matplotlib.pyplot as plt;
import matplotlib as mpl;
import datetime;


%matplotlib inline
import matplotlib.pyplot as plt;

print "Backend:", plt.matplotlib.rcParams['backend']
print "Interactive:", plt.isinteractive()

plt.figure();
plt.ylabel("Test plot"); 
plt.title("test plot title")

#plt.bar([1,2,3,4,5], [21,33,40,23,7], color='r', bottom=0)

xpoints = [1,2,3,4,5]
r1 = [21,33,40,23,7]
r2 = [17,3,4,44,22] 

p1 = plt.bar(xpoints, r1, color='r', bottom=0)
p2 = plt.bar(xpoints, r2, color='g', bottom=r1)

