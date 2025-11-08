from geomeppy import IDF  # Not from eppy!
import matplotlib.pyplot as plt

IDF.setiddname("/Applications/EnergyPlus-25-1-0/Energy+.idd")
idf = IDF("idf_files/Case600_EnergyPlus-25-1-0.idf")

idf.view_model()  # Works now!
plt.show()