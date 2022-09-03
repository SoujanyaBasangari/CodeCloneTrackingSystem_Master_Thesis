#import GetFiles
import data_extraction
import CloneDetector
#import CloneSave

#import ml
# save char2vec with diff name and load clustering model pickle file
# allFilesData is list which have all files with specific extension
print("Getting all file info from folder")
dirPath = "/Users/vivekgoud/Documents/GitHub/Test_project_Codeclonetracer/onlinebookstore-J2EE/"
allFilesData= data_extraction.getAllFilesUsingFolderPath(dirPath)
print("Extracting methods from files")

codeBlocks,linesofcode = data_extraction.extractMethodsAllFiles(allFilesData)


# codeBlocksWithClonePairsType1 = TypeOneDetector.detectClone(allFilesMethods)
# print(codeBlocksWithClonePairsType1)
print("Detecting clones")
clones,codeclonelines= CloneDetector.detectClone(codeBlocks)

print(linesofcode,"total lines",codeclonelines,"total cloned lines", (codeclonelines/linesofcode)*100 , "cloning percentage")
print("Saving to CSV")
# CloneSave.writeToFile(codeBlocks)
#CloneSave.writeToCSV(codeBlocks)


