#dirPath = "/Users/soujanya basangari/Documents/Theses final code/Test_project_Codeclonetracer-main/Test_project_Codeclonetracer-main"

#dirPath = "C:/Users/soujanya basangari/Documents/Theses final code/Java_Repository_Test_Repo-main"

dirPath = "C:/Users/soujanya basangari/Desktop/Clonedetection/RxJava-3.x/RxJava-3.x"

#dirPath = "C:/Users/soujanya basangari/Documents/Theses final code/jEdit-master/jEdit-master"

# dirPath = "F:\8th-Sem-Project\src\examples\Single"
# outputPath = "F:\8th-Sem-Project\src\CodeCloneDetection\output.txt"
# outputCSVPath = "F:\8th-Sem-Project\src\CodeCloneDetection\clonesDetected.csv"
# This will be used as level for output into file
# 0 means everything
# 1 means current block's code and only clone blocks info
# 2 means only current block's and clone block's info
outputLevel = 2

# Minimum length of block to consider
minimumLengthBlock = 5

# Threshhold for considering as code clones
# Threshhold = 1 for type 2 clones
tokenSimilarityThreshold =0.85

# Threshold for similarity measure by data flow approach
similarityDataFlowThreshold =0.80

# Threshold for considering most frequent variables and methods
variableAndMethodsThreshold =0.80

# Threshold while comparing dataflow of two variables and methods
dataFlowSimilaritythreshold = 0.80

# Block level can be 0 = (file level) or 1 = (method level)
granularity = 'method_level'
