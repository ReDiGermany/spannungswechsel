# SpannungsWechsel

Dieses Repository behinhaltet diverse KOT dumps vom Team SpannungsWechsel.

SpannungsWechsel ist ein Team, dass sich damit beschäftigt, ein RC Car autonom durch Pylonen fahren zu lassen.

Dabei haben wir die [Formula Student](https://www.formulastudent.de/fsg/) und ihre Driverless Vehicle im Fokus. Umgesetzt wird das ganze für das Team [HofSpannung](https://hofspannung.de/).

___

## Allgemeines:

Zur nutzung der jeweiligen Instanzen im Ordner `pip install -r requirements.txt` nutzen.

Zur erstellung dieser Datei nutzen wir `pipreqs .` (`pip install pipreqs`).

Getestet und entwickelt wird unter Python 3.9.13

Auf dem Auto läuft Python 3.8.10


-------------------------------------------

update Matplotlib plot

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 6*np.pi, 100)
y = np.sin(x)

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

for phase in np.linspace(0, 10*np.pi, 500):
    line1.set_ydata(np.sin(x + phase))
    fig.canvas.draw()
    fig.canvas.flush_events()


## TODO

[ ] Nach Klassen sortieren
[ ] Mit den Klassen einen Kreis plotten