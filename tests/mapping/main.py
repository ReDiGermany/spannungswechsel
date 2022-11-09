import numpy as np
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
 
a = np.array([
    [1,20],
    [2,30],
    [3,40],
    [4,40],
    [5,39],
    [6,48],
    [7,50],
    [8,3]
])

x = np.array(a[:,0])
y = np.array(a[:,1])

print(x)
print(y)

# Dataset
# x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
# y = np.array([20, 30, 40, 40, 39, 48, 50, 3])
 
# print(x)
# print(y)
X_Y_Spline = make_interp_spline(x, y)
 
# Returns evenly spaced numbers
# over a specified interval.
X_ = np.linspace(x.min(), x.max(), 500)
Y_ = X_Y_Spline(X_)
 
# Plotting the Graph
plt.plot(x,y,'o')
plt.plot(X_, Y_)
plt.show()

#######################################################################################

# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.interpolate import interp1d

# # x = np.linspace(0, 10, num=11, endpoint=True)
# # y = np.cos(-x**2/9.0)

# # f1 = interp1d(x, y, kind='nearest')
# # f2 = interp1d(x, y, kind='zero')
# x = np.array([0, 6,3])
# y = np.array([0, 100,250])
# f3 = interp1d(x, y, kind='quadratic')

# # xnew = np.linspace(0, 10, num=1001, endpoint=True)
# plt.plot(x, y, 'o')
# plt.plot(x, f3(x), ':')
# # plt.legend(['data', 'nearest', 'zero', 'quadratic'], loc='best')
# plt.show()

#######################################################################################

# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.interpolate import interp1d

# xpoints = np.array([0, 6,3])
# ypoints = np.array([0, 100,250])

# xpoints1 = np.array([10, 5,2])
# ypoints1 = np.array([10, 110,260])

# plt.plot(xpoints, ypoints, marker = 'o', mfc = 'blue', mec = 'blue', c = 'blue')
# plt.plot(xpoints1, ypoints1, marker = 'o', mfc = 'yellow', mec = 'yellow', c = 'yellow')
# plt.show()