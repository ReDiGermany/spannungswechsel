from __future__ import division
from matplotlib import pyplot as plt
import numpy as np  
import sys

from scipy import interpolate

def plotCircle(nodes):
    x = nodes[:,0]
    y = nodes[:,1]

    tck,u     = interpolate.splprep( [x,y] ,s = 0,per=True )
    xnew,ynew = interpolate.splev( np.linspace( 0, 1, 100 ), tck,der = 0)

    return [x,y,xnew,ynew]
    # plt.plot( x,y,'o' , xnew ,ynew )

def plotSplines():
    nodes = np.array([
        [0,4],
        [0,6],
        [2,8],
        [4,6],
        [4,5],
        [3,4],
        [4,3],
        [4,2],
        [2,0],
        [0,2],
        [0,4],
    ])
    x,y,xnew,ynew = plotCircle(nodes)
    plt.plot( x,y,'o' , xnew ,ynew )

    nodes = np.array([
        [1,4],
        [1,6],
        [2,7],
        [3,6],
        [3,5.5],
        [2,4.5],
        [2,3.5],
        [3,2.5],
        [3,2],
        [2,1],
        [1,2],
        [1,4],
    ])
    x,y,xnew,ynew = plotCircle(nodes)
    plt.plot( x,y,'o' , xnew ,ynew )
    plt.show()



def plotCourse(x,y):


    plt.rcParams["figure.figsize"] = [np.max(x)+1, np.max(y)+1]
    plt.rcParams["figure.autolayout"] = True
    plt.xlim(0, np.max(x)+1)
    plt.ylim(0, np.max(y)+1)
    plt.grid()
        
    for i in range (0,4):
        plt.plot(x[i], y[i], marker="o", markersize=10, markeredgecolor="red", markerfacecolor="green")
    plt.show()


    

x = np.array([0.241,2.324,5.2423,4.235])
y = np.array([0.234,3.424,3.455,7.234])

plotSplines()
