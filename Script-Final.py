import csv
import sys
import os
import tkinter as tk

# user input - input the order file and cartons file (with correct filepaths) into the quotations below:
csv_items = csv.reader(open('C:\\Users\\Desktop\\order.csv'))
csv_cartons = csv.reader(open('C:\\Users\\Desktop\\carton.csv'))

# region import data

#define preliminary data structures for orders
orderNumber = []
SKULength = []
SKUWidth = []
SKUHeight = []
count1 = 0

# add to data structures from orders txt file
for row in csv_items:
    if (count1==0):
        count1+=1
    else:
        orderNumber.append(int(row[0]))
        SKULength.append(float(row[2]))
        SKUWidth.append(float(row[3]))
        SKUHeight.append(float(row[4]))

# define preliminary data structures for cartons
cartonNumber = []
cartonID = []
cartonLength = []
cartonWidth = []
cartonHeight = []
count2 = 0

# add to data structures from cartons txt file
for row in csv_cartons:
    if (count2==0):
        count2+=1
    else:
        cartonNumber.append(count2)
        cartonID.append(row[0])
        cartonLength.append(float(row[1]))
        cartonWidth.append(float(row[2]))
        cartonHeight.append(float(row[3]))
        count2 += 1

#endregion

#region creating required data structures

# creating dict of orders

orders = {}

for x in range(orderNumber[-1]):
    orders[x+1] = [0]

for x in range(len(orderNumber)):
    y = orderNumber[x]
    tempList = orders[y]

    if (tempList[0] == 0):
        tempList.remove(tempList[0])

    tempList.append(x)
    orders[y] = tempList

# obtaining carton volumes

cartonVolumes = {}

for x in range(len(cartonID)):
    cLength = cartonLength[x]
    cWidth = cartonWidth[x]
    cHeight = cartonHeight[x]
    cVolume = cLength * cWidth * cHeight

    cartonVolumes[x+1] = cVolume

# obtaining total order volumes (sum of all item volumes)

orderVolumes = {}

for x in range(1, orderNumber[-1] + 1):
    orderVolumes[x] = 0

for x in range(len(orderNumber)):
    oLength  = SKULength[x]
    oWidth = SKUWidth[x]
    oHeight = SKUHeight[x]
    oVolume = oLength * oWidth * oHeight

    orderVolumes[orderNumber[x]] += oVolume

# making dict of cartons that can fit the volume of each order

availableCartons = {}

for x in range(orderNumber[-1]):
    availableCartons[x+1] = []

for order in orderVolumes:
    for carton in cartonVolumes:
        if (orderVolumes[order] < cartonVolumes[carton]):
            tempList = availableCartons[order]
            tempList.append(carton)
            availableCartons[order] = tempList

#endregion

# region pick best cartons

# creating dicts that will be outputted, containing best cartons for each order
bestCartonsForOrder = {}
bestCartonsForOrderCUR = {}

for x in range(len(orders)+1):
    bestCartonsForOrder[x+1] = []
    bestCartonsForOrder[x+1] = 0

# going through every order
for order in orders:

    availableCartonsForOrder = availableCartons[order]

    # dict for empty space per carton per order
    emptySpaceperCarton = {}

    # going through every carton and checking if they are available for the order
    for carton in cartonNumber:
        for x in availableCartonsForOrder:
            if (carton==x):

                # get carton dimensions
                cLength = cartonLength[carton - 1]
                cWidth = cartonWidth[carton - 1]
                cHeight = cartonHeight[carton - 1]

                # vars to help with fitting
                lengthLeft = cLength
                widthLeft = cWidth
                heightLeft = cHeight
                maxHeightPerLayer = 0.0
                emptySpace = 0.0

                # packing algorithm
                for item in orders[order]:

                    # get item dimensions
                    length = SKULength[item-1]
                    width = SKUWidth[item-1]
                    height = SKUHeight[item-1]

                    # vars to help with fitting
                    tryToFit = True
                    didFit = True

                    #priority system changing dimension values for better fit
                    if (height>length):
                        tempDim = height
                        height = length
                        length = tempDim

                    if (height>width):
                        tempDim = height
                        height = width
                        width = tempDim

                    hcount = 0

                    while(tryToFit):
                        # if item fits in current layer
                        if (length<lengthLeft and width<widthLeft and height<heightLeft):
                            # item is placed at this point

                            # setting max height per layer
                            if (height>maxHeightPerLayer):
                                maxHeightPerLayer =  height

                            # recreating empty space left in layer
                            if ((lengthLeft-length)>(widthLeft-width)):
                                emptySpace += maxHeightPerLayer * (widthLeft-width) * length
                                lengthLeft -= length
                            elif ((lengthLeft-length)<(widthLeft-width)):
                                emptySpace += maxHeightPerLayer * (lengthLeft-length) * width
                                widthLeft -= width

                            tryToFit = False
                        elif (height<(heightLeft-maxHeightPerLayer) and hcount < 3):

                            # creating new layer for iterm
                            heightLeft -= maxHeightPerLayer
                            maxHeightPerLayer = 0
                            lengthLeft = cLength
                            widthLeft = cWidth
                            hcount += 1

                        else:
                            didFit = False
                            tryToFit = False
                            emptySpace = -1

                # final dictionary of empty space for each carton in current order
                emptySpaceperCarton[carton] = emptySpace

    # setting vars to help with picking best cartons
    firstValue = 999999
    firstKey = 999
    secondValue = 999999
    secondKey = 999

    for x in emptySpaceperCarton:

        # if empty space is not -1 (meaning order fits in carton)
        if (emptySpaceperCarton[x]>=0):

            # set vars for current carton
            spaceLeftValue = emptySpaceperCarton[x]
            spaceLeftKey = x

            # place carton accordingly
            if (spaceLeftValue < secondValue):
                if (spaceLeftValue < firstValue):
                    secondKey = firstKey
                    secondValue = firstValue
                    firstKey = spaceLeftKey
                    firstValue = spaceLeftValue
                else:
                    secondKey = spaceLeftKey
                    secondValue = spaceLeftValue

    # storing results into dicts

    bestCartonsForOrderList = []
    bestCartonKeyCUR = 1

    if (firstKey > 0 and firstKey<len(cartonNumber)):
        bestCartonsForOrderList.append(str(cartonID[firstKey-1]))
        bestCartonKeyCUR = firstKey
    if (secondKey > 0 and secondKey<len(cartonNumber)):
        bestCartonsForOrderList.append(str(cartonID[secondKey-1]))

    bestCartonsForOrder[order] = bestCartonsForOrderList
    bestCartonsForOrderCUR[order] = bestCartonKeyCUR

#endregion

#region calculating carton utilization rate

totalCURNum = 0
count3 = 0

# calculate carton utilization rate for every order
for x in range(len(orderVolumes)):
    CUROfOrder = orderVolumes[x+1]/cartonVolumes[bestCartonsForOrderCUR[x+1]]
    if (CUROfOrder > 0 and CUROfOrder <= 1):
        totalCURNum += CUROfOrder
        count3+=1

# creating the average carton utilization rate (uncomment print statement for result)
avgCartonUtilizationRate = totalCURNum / count3
#print(avgCartonUtilizationRate)

#endregion

#region User Interface

# creating user interface
def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    self.controller = controller

window = tk.Tk()
window.title("DHL Box Packer")
window.geometry("500x400")
window.configure(bg='#FFCC00')

titlefont = ('Helvetica', 35, 'bold')
title = tk.Label(text = "DHL Box Packer", fg='#D40511', bg='#FFCC00', pady=20)
title.config(font=titlefont)
title.pack()

# Entry box with label
lfont = ('Helvetica', 12, 'bold')
l = tk.Label(text="Enter Order Number", bg='#FFCC00')
l.config(font=lfont)
l.pack()
e = tk.Entry()
e.pack()

# calls required data structures to create output
def selection():
    selectionHelp()

# Enter button
b = tk.Button(text="Enter", command=selection, padx=68, pady=0.1)
b.pack()

# resultant information display
bord = tk.LabelFrame(text="Order Information", padx=10, pady=10, bg='#FFCC00', fg='#D40511', bd=5)
bord.pack()
bord2 = tk.LabelFrame(text="Carton Selections", padx=10, pady=10, bg='#FFCC00', fg='#D40511', bd=5)
bord2.pack()

# helper method for selection
def selectionHelp():
    orderNum = int(e.get())  ##takes order inputted in entry box
    if (orderNum>0):
        bestCartonList = bestCartonsForOrder[orderNum]
        tk.Label(bord, text="Order Number: " + str(orderNum), bg='#FFCC00').pack()
        tk.Label(bord, text="Items in Order: " + str(len(orders[orderNum])), bg='#FFCC00').pack()
        tk.Label(bord2, text="Option 1: " + str(bestCartonList[0]), bg='#FFCC00').pack()
        tk.Label(bord2, text="Option 2: " + str(bestCartonList[1]), bg='#FFCC00').pack()
    else:
        print("error: order number is not inputted correctly")

def reset():
    python = sys.executable
    os.execl(python, os.path.abspath('C:\\Users\\karth\\Desktop\\IISE_Submission\\Script-Final.py'), * sys.argv)
    

# New Entry button
b2 = tk.Button(text="New Entry", command=reset, padx=55, pady=0.1)
b2.pack()

window.mainloop() ##UI content must be between line 7 and this line

#endregion
