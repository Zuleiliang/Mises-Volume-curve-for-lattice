from abaqus import *
from abaqusConstants import *
import numpy as np
import os
import csv


# amend parameter ===============================================================================================
# Modify the working directory to the folder where the odb file is located
os.chdir(r"C:\temp\45-30")

# Modify “odbName” 
odbName = '45-30-30.odb'
# Modify “instName”
instName = 'PART-1-1'
# List all the frames to be extracted in the frame_index_list table
frame_index_list = [78,67,61,56,52]

# Define the path for saving CSV files
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")   
csv_file_path = os.path.join(desktop_path, "Mises_Volume_Curves_.csv")


# Calculate the volume of the tetrahedral element ==========================================================================================
def get4PointsVolume(p1,p2,p3,p4):
	
	l1 = [p1[0]-p4[0],p1[1]-p4[1],p1[2]-p4[2]]
	l2 = [p2[0]-p4[0],p2[1]-p4[1],p2[2]-p4[2]]
	l3 = [p3[0]-p4[0],p3[1]-p4[1],p3[2]-p4[2]]
	l1xl2 = [l1[1]*l2[2]-l2[1]*l1[2],l1[2]*l2[0]-l2[2]*l1[0],l1[0]*l2[1]-l2[0]*l1[1]]
	l1xl2_l3 = l1xl2[0]*l3[0]+ l1xl2[1]*l3[1]+ l1xl2[2]*l3[2]
	v = abs(l1xl2_l3)/6.
	return v



odb = session.odbs[odbName]
inst = odb.rootAssembly.instances[instName]
instNodes = inst.nodes
elemVolumes = {}
allVolume = 0
node_dict = {}


for node in inst.nodes:
	node_dict[node.label] = node.coordinates


for elem in inst.elements:
	if elem.type == 'C3D10M':
		elemNodeCoords = []
		for nodeId in elem.connectivity[:4]:
			elemNodeCoords.append(node_dict[nodeId])
		elemVolume = get4PointsVolume(*elemNodeCoords)
		elemVolumes[elem.label] = elemVolume
		allVolume += elemVolume


# Display the total volume of the lattice
print('Total Volume : %e'%allVolume)


# Loop through the frame data to be extracted
# Open the CSV file and write the data (Python 2.7 uses the 'wb' mode)  
with open(csv_file_path, 'wb') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    
    csv_writer.writerow(["CheckValue", "FrameVolume"])
    
    
    for frame_index in frame_index_list:
        for step in odb.steps.values():
            frame = step.frames[frame_index]
            
            
            for checkValues in range(1, 51, 1):
				frameVolume = 0
				findValues = frame.fieldOutputs['S'].getSubset(region=inst).values
				
				
				for i in findValues:
					try:
						if i.mises <= checkValues:
							frameVolume += elemVolumes[i.elementLabel] / 4.
					except KeyError:
						continue
				
				
				
				print("%s %s" % (checkValues, frameVolume))
				csv_writer.writerow([str(checkValues), str(frameVolume)])



print("==================Finshed==================")
