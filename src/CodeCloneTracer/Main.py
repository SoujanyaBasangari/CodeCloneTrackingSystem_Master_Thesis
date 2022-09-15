#import GetFiles
import data_extraction
import CloneDetector
#import CloneSave
import cloneTracking
#import ml
# save char2vec with diff name and load clustering model pickle file
# allFilesData is list which have all files with specific extension
print("Getting all file info from folder")
#dirPath = "C:/Users/soujanya basangari/Documents/Theses final code/Test_project_Codeclonetracer-main/Test_project_Codeclonetracer-main/onlinebookstore-J2EE"

#dirPath = "C:/Users/soujanya basangari/Documents/Theses final code/Java_Repository_Test_Repo-main"
dirPath = "C:/Users/soujanya basangari/Desktop/Clonedetection/RxJava-3.x/RxJava-3.x"

#dirPath = "C:/Users/soujanya basangari/Documents/Theses final code/jEdit-master/jEdit-master"

allFilesData= data_extraction.getAllFilesUsingFolderPath(dirPath)

print("Extracting methods from files",len(allFilesData),"total_files")

current_dataset,linesofcode,codeclonelines= data_extraction.extractMethodsAllFiles(allFilesData)
print("load transformed dataset to ML model",linesofcode,codeclonelines)

total_files=len(allFilesData)

ml_dataset,indices= cloneTracking.clonetracingModel(current_dataset)

cloning_percentage = (codeclonelines/linesofcode)*100

tracking_result = cloneTracking.analysis_creating_report(ml_dataset,total_files,cloning_percentage,indices )

print("check tracking.txt for latest report")

#print(linesofcode,"total lines",codeclonelines,"total cloned lines", (codeclonelines/linesofcode)*100 , "cloning_percentage")

# CloneSave.writeToFile(codeBlocks)
#CloneSave.writeToCSV(codeBlocks)


#pip install python-Levenshtein

#pip install pydriller
#pip install fuzzywuzzy
#pip install pandas
#pip install javalang

#pip install virtualenv

# virtualenv ENV

# source ENV/bin/activate