# CodeCloneTrackingSystem_Master_Thesis

## Approach 1

For local project copy CodeCloneTracer.zip and place in your working directory

run following required packages

python -m pip install -r CodeCloneTracer/requirements.txt

Change Config.py

Replace dirPath with local repository path,set extract_from_git to false

set the granularity of the cloning- method_level,file_level,block_level

set extract_from_git to False

check tracking_report.txt 

## Approach 2

For git project place CodeCloneTracer folder in working branch

run following required packages

python -m pip install -r CodeCloneTracer/requirements.txt

Change Config.py

Replace url with git repository, set extract_from_git to true , set first_git parameter to true if its first time and then modify

set the granularity of the cloning- method_level,file_level,block_level

set extract_from_git to False

check tracking_report.txt 

check test project https://github.com/SoujanyaBasangari/test_project 


