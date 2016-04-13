#Capt Noah Lesch

#This application uses OpenCV version 3.1.0 to generate image histograms
#and SIFT features.  These features are output to a .csv file which can be
#rebuilt into the original histograms.  More....
import os
import numpy
import cv2 #OpenCV functionality
from matplotlib import pyplot as plt #Graphing/plotting functionality with TkAgg backend (very important)
import xml.etree.ElementTree as ET #XML read/write functionality
import exifread #Allows import of image metadata
import glob #Allows directory parsing for certain file extensions
from Tkinter import Tk #GUI functionality in Python
from tkFileDialog import askopenfilename #Will allow Pyton to query user for file

def print_intro():
    print("H - Help Menu")
    print("HIST - Create and saves RGB and grayscale histograms of an image.")
    print("HISTD - Creates and saves RGB and grayscale histograms of an entire directory.")
    print("HISTX - Same as 'HIST' with the addition of metadata being read/written")
    print("LOADRGB - Loads the RGB histogram of an image.  Select either the original image or one of the RGB histogram .csv files.")
    print("LOADGRAY - Loads grayscale histogram of an image.  Select either the original image or the gray histogram .csv file.")
    print("EXIT - Exit Application")
    print("COMP - Compare two histograms to see the correlation")
    return

def compare_hist():
    #compare_hist()
    #This function will allow the user to choose two image file and then compare their
    #correlation using the cv2.cv.CV_COMP_CORREL function to compute the correlation between
    #two histograms.  Results are then displayed back to the user.
    from Tkinter import Tk #GUI functionality in Python
    from tkFileDialog import askopenfilename #Will allow Pyton to query user for file

    print "Select first file..."
    Tk().withdraw() #Hides the Tk window that always appears
    firstHist = askopenfilename() # Opens directory dialog
    fileName, fileExt = os.path.splitext(firstHist)
    filePath, fileTail = os.path.split(firstHist)

    base=cv2.imread(fileTail)
    base=cv2.cvtColor(base, cv2.COLOR_BGR2RGB)
    histbase = cv2.calcHist([base],[0], None, [256], [0,256])

    print "Select second file..."
    Tk().withdraw() #Hides the Tk window that always appears
    secondHist = askopenfilename() # Opens directory dialog
    test=cv2.imread(secondHist)
    test=cv2.cvtColor(test, cv2.COLOR_BGR2RGB)
    histtest = cv2.calcHist([test],[0], None, [256], [0,256])

    d = cv2.compareHist(histbase, histtest, 0)
    print d
    
    return

def histd():
    #This function selects a user defined directory to parse all .jpg and .png images
    #Returns a list of all image prefix names and file extensions, plus the directory
    #of all images.
    
    from Tkinter import Tk #GUI functionality in Python
    from tkFileDialog import askdirectory #Will allow Pyton to query user for directory
    Tk().withdraw() #Hides the Tk window that always appears
    newDir = askdirectory() # Opens directory dialog
    os.chdir(newDir) #Change the directory to the user selected directory
    jpgList = glob.glob('*.jpg')
    pngList = glob.glob('*.png')
    imageList = jpgList + pngList #Combines list of .jpg and .png images together
    #print imageList #Prints image list; used for debugging
    imageList.append(os.getcwd()) #Concatenates the desired directory to the end of the imageList
    return imageList


def hist(imgList):
    #This function calculates the histogram for either a single image or for a directory of
    #images depending on how this function is called.  Its input is a list of images (in the case
    #of parsing an entire directory) or the list will be set to empty if a single image will be
    #parsed for histogram data
    
    from Tkinter import Tk #GUI functionality in Python
    from tkFileDialog import askopenfilename #Will allow Pyton to query user for file

    #If an empty imgList was passed to hist() then the below code will execute for the image

    if (len(imgList) == 0):
        Tk().withdraw() #Hides the small Tk window that always appears
        fileName = askopenfilename() # Opens directory dialog
        fileName, fileExt = os.path.splitext(fileName)
        filePath, fileTail = os.path.split(fileName)
        os.chdir(filePath)
        var = str(fileTail+fileExt) #This is the file's name.ext in the user-chosen directory
        img = cv2.imread(var)
        #cv2.imshow('User Image', img)

        #The below code sets up the XML shell file that will be populated with
        #the image and histogram metadata
        root = ET.Element(str(fileTail)) #Root of the XML tree is the filename Prefix
        root.attrib["fileExtension"] = str(fileExt)
        blueElement = ET.SubElement(root, "Blue")
        greenElement = ET.SubElement(root, "Green")
        redElement = ET.SubElement(root, "Red")
        grayElement = ET.SubElement(root, "Gray")

        #open image and begin to extract/populate metadata
        data = open(var) #The file that will be read for metadata
        tags = exifread.process_file(data) #Reads metadata
        #print data.exif_keys #Prints a list of all keys of available EXIF tags

        try:
            dateTag= tags['EXIF DateTimeOriginal'] #Finds the date/time tag in the metadata
            #print dateTag
            dateElement = ET.SubElement(root, "TimeofExposure")
            ET.SubElement(dateElement, "DateTime").text = str(dateTag)
        except:
            #print "No Date/Time metadata in image"
            dateElement = ET.SubElement(root, "TimeofExposure")
            ET.SubElement(dateElement, "DateTime").text = ""
        try:        
            rawLatTag = str(tags['GPS GPSLatitude'])
            #print rawLatTag
            LatTag = rawLatTag.split()
            strLatTag = str(LatTag[0].strip('[')) + str(LatTag[1].strip()) + str(LatTag[2].strip().strip(']'))
            latElement = ET.SubElement(root, "LatitudeDMS")
            ET.SubElement(latElement, "Coordinates").text = strLatTag
        except:
            #print "No GPS.Latitude metadata in image"
            latElement = ET.SubElement(root, "LatitudeDMS")
            ET.SubElement(latElement, "Coordinates").text = ""
        try:
            rawLonTag = str(tags['GPS GPSLongitude'])
            LonTag = rawLonTag.split()
            strLonTag = str(LonTag[0].strip('[')) + str(LonTag[1].strip()) + str(LonTag[2].strip().strip(']'))
            #print strLonTag
            lonElement = ET.SubElement(root, "LongitudeDMS")
            ET.SubElement(lonElement, "Coordinates").text = strLonTag
        except:
            #print "No GPS.Longitude metadata in image"
            lonElement = ET.SubElement(root, "LongitudeDMS")
            ET.SubElement(lonElement, "Coordinates").text = ""
            
        tree = ET.ElementTree(root)
        tree.write(str(fileName)+'.xml')
    
        color = ( 'b', 'g', 'r')
        for i,col in enumerate(color):
            histr = cv2.calcHist([img],[i],None,[256],[0,256]) #histr is an array of 256 numbers
            strArray = ''
            for x in histr:
                strArray = strArray + (str(int(x))) + '|'
            #print strArray
            
            f = open(fileTail + "_" + col + "_" + "hist.csv", 'w')
            #for x in range(0,256):
            if col == 'b':
                blueElement.text = strArray
            elif col == 'g':
                greenElement.text = strArray
            elif col == 'r':
                redElement.text = strArray
            f.write(strArray)
            tree.write(str(fileTail)+'.xml')
            f.close()
            plt.plot(histr, color=col)
            plt.xlim([0,256])
        imgExt = '.png'
        plt.savefig(fileTail + '_color_Hist' + imgExt)
        #plt.ion()
        #plt.show()
        #plt.pause(0.01)
        #cv2.waitKey(2000)
        #plt.clf()
        plt.close()
        img= cv2.imread(var, cv2.IMREAD_GRAYSCALE)
        #cv2.imshow('img',img)    
        hist = cv2.calcHist([img],[0], None, [256], [0,256])
        strArray = ''
        for x in hist:
                strArray = strArray + (str(int(x))) + '|'
            #[img] is the variable 'img'
            #[0] corresponds to the 0th channel, or grayscale
            #None is mask.  Using none means take the histogram of the full image
            #[256] represents the bin count
            #[0,256] is our range
        g = open(fileTail + "_" + "gray" + "_" + "hist.csv", 'w')
        grayElement.text = strArray
        g.write(strArray)
        tree.write(str(fileTail)+'.xml')
        g.close()
        plt.plot(hist, color='k')
        plt.xlim([0,256])
        plt.savefig(fileTail + '_gray_Hist' + imgExt)
        #plt.ion() #Enables interactive mode so our plot is non-blocking to program execution
        #plt.show() #Shows the plot
        #plt.pause(0.01)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()
        #plt.clf()
        plt.close('all')
        return (var) #Return the file name (name.ext)

    #Otherwise if an imageList is passed to this hist() function the file directory will be the last element of that list
    #Change directory to the location at the end of imgList, then strip off the list entry that contains the directory information
    #and begin to iterate through the images in that directory
    elif (len(imgList) >0):
        numberImages = len(imgList) - 1
        os.chdir(imgList[-1]) #Changes our directory to the last element of imgList which was passed to hist() via the list from histd()
        print os.getcwd()
        del imgList[-1] #Removes directory at the end of our list so we can iterate through images in the next section

    #If a populated imgList was passed to hist() then the below code will iterate through all images 

    for image in imgList:
        fileName, fileExt = os.path.splitext(image)
        #fileName is the prefix of the file (i.e. prefix.jpg or prefix.png)
        #fileExt is the suffix (extension) of the file .jpg, .png
        var = str(fileName+fileExt) #Concatenates prefix/suffix so you have foo.jpg bar.png etc.
        img = cv2.imread(var)
        #cv2.imshow('User Image', img)
        #plt.close('all')

        #The below code sets up the XML shell file that will be populated with
        #the image and histogram metadata
        root = ET.Element(str(fileName)) #Root of the XML tree is the filename Prefix
        root.attrib["fileExtension"] = str(fileExt)
        blueElement = ET.SubElement(root, "Blue")
        greenElement = ET.SubElement(root, "Green")
        redElement = ET.SubElement(root, "Red")
        grayElement = ET.SubElement(root, "Gray")
    
         #open image and begin to extract/populate metadata
        data = open(var) #The file that will be read for metadata
        tags = exifread.process_file(data) #Reads metadata

        try:
            dateTag= tags['EXIF DateTimeOriginal'] #Finds the date/time tag in the metadata
            #print dateTag
            dateElement = ET.SubElement(root, "TimeofExposure")
            ET.SubElement(dateElement, "DateTime").text = str(dateTag)
        except:
            #print "No Date/Time metadata in image"
            dateElement = ET.SubElement(root, "TimeofExposure")
            ET.SubElement(dateElement, "DateTime").text = ""
        try:        
            rawLatTag = str(tags['GPS GPSLatitude'])
            #print rawLatTag
            LatTag = rawLatTag.split()
            strLatTag = str(LatTag[0].strip('[')) + str(LatTag[1].strip()) + str(LatTag[2].strip().strip(']'))
            latElement = ET.SubElement(root, "LatitudeDMS")
            ET.SubElement(latElement, "Coordinates").text = strLatTag
        except:
            #print "No GPS.Latitude metadata in image"
            latElement = ET.SubElement(root, "LatitudeDMS")
            ET.SubElement(latElement, "Coordinates").text = ""
        try:
            rawLonTag = str(tags['GPS GPSLongitude'])
            LonTag = rawLonTag.split()
            strLonTag = str(LonTag[0].strip('[')) + str(LonTag[1].strip()) + str(LonTag[2].strip().strip(']'))
            #print strLonTag
            lonElement = ET.SubElement(root, "LongitudeDMS")
            ET.SubElement(lonElement, "Coordinates").text = strLonTag
        except:
            #print "No GPS.Longitude metadata in image"
            lonElement = ET.SubElement(root, "LongitudeDMS")
            ET.SubElement(lonElement, "Coordinates").text = ""
            
        tree = ET.ElementTree(root)
        tree.write(str(fileName)+'.xml')
        
        color = ( 'b', 'g', 'r')
        for i,col in enumerate(color):
            histr = cv2.calcHist([img],[i],None,[256],[0,256]) #histr is an array of 256 numbers
            strArray = ''
            for x in histr:
                strArray = strArray + (str(int(x))) + '|'
                
            f = open(fileName + "_" + col + "_" + "hist.csv", 'w')
            #for x in range(0,256):
            if col == 'b':
                blueElement.text = strArray
            elif col == 'g':
                greenElement.text = strArray
            elif col == 'r':
                redElement.text = strArray
            f.write(strArray)
            f.write("\n")
            tree.write(str(fileName)+'.xml')
            f.close()
            plt.plot(histr, color=col)
            plt.xlim([0,256])
        imgExt = '.png'
        plt.savefig(fileName+'_color_Hist'+imgExt)
        #plt.ion()
        #plt.show()
        #plt.pause(0.01)
        #cv2.waitKey(2000)
        #plt.clf()
        plt.close('all') #Closes all figures

        '''

        img= cv2.imread(var, cv2.IMREAD_GRAYSCALE)
        #cv2.imshow('img',img)
        #cv2.waitKey(10)
        hist = cv2.calcHist([img],[0], None, [256], [0,256])
        strArray = ''
        for x in hist:
                strArray = strArray + (str(int(x))) + '|'
        g = open(fileName + "_" + "gray" + "_" + "hist.csv", 'w')
        grayElement.text = strArray
        g.write(strArray)
        g.write("\n")
        tree.write(str(fileName)+'.xml')
        g.close()
        #plt.plot(hist, color='k')
        #plt.xlim([0,256])
        #plt.savefig(fileName+'_gray_Hist'+imgExt)
        #plt.ion() #Enables interactive mode so our plot is non-blocking to program execution
        #plt.show() #Shows the plot
        #plt.pause(0.01)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()
        plt.close('all')
        #img = ""
        #img2 = ""
        #histr = ""
        #hist = ""
        '''
    return (var)

def metadata(fileLocation):
    #This function will parse metadata from an image that is geotagged
    #The resulting output is written to an XML file in the same directory
    #as the existing image with the file name prefix .xml

    name, ext = os.path.splitext(fileLocation) #Parse filename foo.jpg -> foo=name .jpg=ext

    #The below try/except statement will see if an XML file exists already for selected image
    #and get the root to continue populating the XML tree.  Otherwise the root of the tree is created.
    try:
        tree=ET.parse(fileLocation) #Checks to see if XML file already exists for this image
        root = tree.getroot() #root is now the root node in the XML file
    except:
        root = ET.Element(str(name)) #Creates the root of the tree
        tree=ET.ElementTree(root)
        
    #open image and begin to extract/populate metadata
    data = '' #The file that will be read for metadata
    data.read() #Reads metadata
    
    try:
        dateTag= data['Exif.Image.DateTime'] #Finds the date/time tag in the metadata
        #print dateTag
        element = ET.SubElement(root, "TimeofExposure")
        ET.SubElement(element, "DateTime").text = str(dateTag.raw_value)
        element.append(root)
    except:
        print "No Date/Time metadata!"
        element = ET.SubElement(root, "TimeofExposure")
        ET.SubElement(element, "DateTime").text = "NoData"
        element.append(root)
    try:        
        latTag = data['Exif.GPSInfo.GPSLatitude']
        #print latTag
        element2 = ET.SubElement(root, "LatitudeDMS")
        ET.SubElement(element2, "Coordinates").text = str(latTag.raw_value)
    except:
        print "No GPS.Latitude metadata!"
        element2 = ET.SubElement(root, "LatitudeDMS")
        ET.SubElement(element2, "Coordinates").text = "NoData"
    try:
        lonTag = data['Exif.GPSInfo.GPSLongitude']
        #print lonTag
        element3 = ET.SubElement(root, "LongitudeDMS")
        ET.SubElement(element3, "Coordinates").text = str(lonTag.raw_value)
    except:
        print "No GPS.Longitude metadata!"
        element3 = ET.SubElement(root, "LongitudeDMS")
        ET.SubElement(element3, "Coordinates").text = "NoData"

    #tree = ET.ElementTree(root)
    tree.write(str(name)+'.xml')
    return

def loadRGBHist():
    #This function will load the RGB histogram of an image.  The user can select
    #the image itself or one of the existing RGB histogram files produced by the 'HIST'
    #command in the main program menu
    from Tkinter import Tk #GUI functionality in Python
    from tkFileDialog import askopenfilename #Will allow Pyton to query user for file
    Tk().withdraw() #Hides the Tk window that always appears
    fileName = askopenfilename() # Opens directory dialog
    fileName, fileExt = os.path.splitext(fileName)
    filePath, fileTail = os.path.split(fileName)
    os.chdir(filePath)
    fileCheck = str(fileTail + fileExt) #Concatenates file name and extension i.e. image.jpg, house.jpg, etc.
    name=fileTail.partition('_')
    histb = []
    histg = []
    histr = []

    if (fileExt == '.jpg' or fileExt == '.png' and os.path.isfile(fileCheck) == True):
        i=0
        with open(fileTail + "_b_hist.csv", 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histb.append(val)
                i = i+1
        plt.plot(histb, color='b')

        i=0
        with open(fileTail + '_g_hist.csv', 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histg.append(val)
                i = i+1
        plt.plot(histg, color='g')

        i=0
        with open(fileTail + '_r_hist.csv', 'r') as f:
           for line in f:                        
                val = int(filter(str.isdigit, line))
                histr.append(val)
                i = i+1
        plt.plot(histr, color='r')
        plt.xlim([0,256])
        plt.ion()
        plt.show()
        plt.pause(2)
        plt.close()
        return
    elif (fileExt == '.csv' and os.path.isfile(name[0] + '_g_hist.csv') == True
          and os.path.isfile(name[0] + '_b_hist.csv') == True
          and os.path.isfile(name[0] + '_r_hist.csv') == True):
        i=0
        with open(name[0] + "_b_hist.csv", 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histb.append(val)
                i = i+1
        plt.plot(histb, color='b')

        i=0
        with open(name[0] + '_g_hist.csv', 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histg.append(val)
                i = i+1
        plt.plot(histg, color='g')

        i=0
        with open(name[0] + '_r_hist.csv', 'r') as f:
           for line in f:                        
                val = int(filter(str.isdigit, line))
                histr.append(val)
                i = i+1
        plt.plot(histr, color='r')
        plt.xlim([0,256])
        plt.ion()
        plt.show()
        plt.pause(2)
        plt.close()
        return
    else:
        print "Error with files.  Make sure all RGB histogram .csv files exist before loading"
        return

def loadGrayHist():
    #This function will load the gray histogram of an image
    #The user can select either the image itself or the .csv file produced by the 'HIST'
    #command in the main program menu.
    
    from Tkinter import Tk #GUI functionality in Python
    from tkFileDialog import askopenfilename #Will allow Pyton to query user for file
    Tk().withdraw() #Hides the Tk window that always appears
    fileName = askopenfilename() # Opens directory dialog
    fileName, fileExt = os.path.splitext(fileName)
    filePath, fileTail = os.path.split(fileName)
    os.chdir(filePath)
    fileCheck = str(fileTail + fileExt) #Concatenates file name and extension i.e. image.jpg, house.jpg, etc.

    name=fileTail.partition('_') #Partitions our string with our known naming structure to find the original file prefix name
    histgray = []
    i=0
    
    if (fileExt == '.csv' and os.path.isfile(name[0] + '_gray_hist.csv') == True): #If the file is .csv and it exists then load from csv
        with open(fileCheck, 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histgray.append(val)
                i = i+1
        plt.plot(histgray, color='gray')
        plt.xlim([0,256])
        plt.ion()
        plt.show()
        plt.pause(2)
        plt.close()
        return
    elif (fileExt == '.jpg' or fileExt == '.png' and os.path.isfile(fileCheck) == True): #If the image is selected then find its .csv and load    
        with open(fileTail +'_gray_hist.csv', 'r') as f:
            for line in f:                        
                val = int(filter(str.isdigit, line))
                histgray.append(val)
                i = i+1
        plt.plot(histgray, color='gray')
        plt.xlim([0,256])
        plt.ion()
        plt.show()
        plt.pause(2)
        plt.close()
        return
    else:
        print "There was an error in your selection.  Returning to main menu."
        return

#from tkFileDialog import askdirectory #Will allow Pyton to query user for directory
#filename = askdirectory() # Opens directory dialog

def main():

    print("********************************************")
    print("Welcome to an OpenCV and Python Application!")
    print("********************************************")
    print_intro()

    while True:
        userInput = raw_input("Enter a command or type H for help: ")
        os.system('cls')
        if not (len(userInput) == 0):
            cmd = userInput.upper().split()
            print (cmd[0])
            if cmd[0] == 'COMP':
                compare_hist()
            if cmd[0] == 'EXIT':
                os._exit(0)
            if cmd[0] == 'H' or cmd[0] == 'HELP':
                #os.system('cls') #Command to clear the python console screen
                print_intro()
            elif cmd[0] == 'HIST':
                imgList = [] #Creates an empty list to pass into hist()
                hist(imgList)
            elif cmd[0] == 'HISTD':
                images=histd() #histd() returns a list of images and path to the user-selected directory
                hist(images) 
            elif cmd[0] == 'HISTX':
                #Histx needs to be able to choose a directory and parse the file that is requested
                #File Location is not being populated with any data.  Check the return statement in hist()
                try:
                    if (len(imgList) >0):
                        print "Length of imgList >0"
                except UnboundLocalError:
                    imgList = []

                fileLocation=hist(imgList) #The original image used for histogram is saved and then passed to the metadata function
                #metadata(fileLocation) #Commented out this function on 21 Mar; attemping to move metadata code into histrogram code
            elif cmd[0] == 'LOADRGB':
                loadRGBHist()
            elif cmd[0] == 'LOADGRAY':
                loadGrayHist()
            if cmd[0] == "XML":
                Tk().withdraw() #Hides the small Tk window that always appears
                fileName = askopenfilename() # Opens directory dialog
            if cmd[0] == 'SIFT':
                img = cv2.imread('arnold.jpg')
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                sift = cv2.xfeatures2d.SIFT_create()
                kp = sift.detection(gray,None)
                img = cv2.drawKeypoints(gray, kp)
                cv2.imwrite('sift_arnold.jpg', img)
                cv2.imshow('sift_arnold.jpg', img)

#This is our main entry point to our program
if __name__ == "__main__":
    main()

#Python Lessons Learned
#Using cv2.imread() then cv2.imshow and executing from IDLE (F5 in IDLE) will cause a crash
#Executing a file with these same functions from the python command line will cause it to crash too
#Executing the script file will NOT cause crashes and it runs perfectly.  Stackoverflow thinks this is a windows bug
