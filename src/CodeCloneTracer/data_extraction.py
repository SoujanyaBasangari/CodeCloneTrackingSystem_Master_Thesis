from datetime import datetime
import itertools
import logging
import os
# import GetFunctions
import re
import sys
import traceback
import CloneDetector
import javalang

import Config
import pandas as pd

global found_parent


def extractMethodsAllFiles(listOfFiles):
    allFilesMethodsBlocks = {}
    blocksSoFar = 0
    linesofcode = 0
    codeBlocks = {}
    print("data extraction from source code")
    for filePath in listOfFiles:
        file = open(filePath, 'r', encoding='utf-8')
        originalCode = file.readlines()
        file.close()
        if Config.granularity == 'method_level':

            linesofcode = linesofcode + len(originalCode)
            codeBlocks = methodLevelBlocks(originalCode)

        else:
            linesofcode = linesofcode + len(originalCode)
            codeBlocks = fileLevelBlocks(originalCode)
        if len(codeBlocks) == 0:
            continue
        for codeBlock in codeBlocks:
            if len(codeBlock) == 0:
                continue
            codeBlock.update({"FileInfo": filePath})
            codeBlock.update({"nloc": len(codeBlock)})
            codeBlock.update({"source_code": originalCode})

            blocksSoFar += 1
            allFilesMethodsBlocks["CodeBlock" + str(blocksSoFar)] = codeBlock

    granularity = Config.granularity
    codeBlocks, codeclonelines = CloneDetector.detectClone(allFilesMethodsBlocks)
    print("detecting code clones")
    previous_file_name = '/Users/vivekgoud/Downloads/thesis/' + granularity + 'tracking.csv'
    current_dataset = dataset_creation(codeBlocks)
    print("Transforming detected code blocks into dataset")
    previous_dataset = pd.DataFrame()
    previous_clones = pd.DataFrame(
        columns=['codeBlockId', 'codeBlock_start', 'codeBlock_end', 'codeBlock_fileinfo', 'codeblock_Code',
                 'codeCloneBlockId',
                 'codeCloneBlock_Fileinfo', 'Similarity_Tokens', 'Similarity_Variable_Flow',
                 'Similarity_MethodCall_Flow', 'commitinfo', 'nloc', 'Revision'])
    if os.path.isfile(previous_file_name):  # previous_file_name.exists():
        previous_dataset = pd.read_csv(previous_file_name, index_col=0)
        revision = previous_dataset.Revision.unique()
        print("Revision", revision[0])
        # previous_clones = previous_dataset[~previous_dataset.codeBlock_fileinfo.isin(current_dataset.codeBlock_fileinfo)]
        # frames = [current_dataset,previous_clones]
        current_dataset['Revision'] = revision[0] + 1
        current_dataset = pd.concat([current_dataset, previous_dataset])
        current_dataset = current_dataset.loc[current_dataset.astype(str).drop_duplicates().index]

    else:
        print("First version, no cloning result exists")
        print("Revision", 1)
        current_dataset['Revision'] = 1

    current_dataset = current_dataset.convert_dtypes()
    all_columns = list(current_dataset)  # Creates list of all column headers
    current_dataset[all_columns] = current_dataset[all_columns].astype(str)
    current_dataset = current_dataset.loc[current_dataset.astype(str).drop_duplicates().index]
    current_dataset['datetime'] = datetime.now()
    current_dataset = current_dataset.reset_index(drop=True)
    current_dataset = current_dataset.drop_duplicates(subset=['codeBlockId', 'Revision', 'codeCloneBlockId'],
                                                      keep='last')
    current_dataset = current_dataset.reset_index(drop=True)
    current_dataset.to_csv('/Users/vivekgoud/Downloads/thesis/' + granularity + 'tracking.csv')
    # current_dataset.to_sql('rxjava', con= engine, if_exists='append', index=False)
    # pd.read_sql('select count(*) from rxjava', conn=engine)
    # current_dataset.to_sql('training_onlinebookstore', con=engine, if_exists='append', index=False)"""

    return current_dataset, linesofcode, codeclonelines


def dataset_creation(codeBlocks):
    df = pd.DataFrame(
        columns=['codeBlockId', 'codeBlock_start', 'codeBlock_end', 'codeBlock_fileinfo', 'codeblock_Code',
                 'codeCloneBlockId',
                 'codeCloneBlock_Fileinfo', 'Similarity_Tokens', 'Similarity_Variable_Flow',
                 'Similarity_MethodCall_Flow', 'nloc'])

    output = []
    for codeBlockId in codeBlocks:
        codeBlock = codeBlocks[codeBlockId]
        for codeCloneBlockData in codeBlock["CodeClones"]:
            codeCloneBlockId = codeCloneBlockData["codeCandidateId"]
            codeCloneBlock = codeBlocks[codeCloneBlockId]
            codeCloneSimilarity = codeCloneBlockData["Similarity"]
            output.append(
                [codeBlockId, str(codeBlock["Start"]), str(codeBlock["End"]), codeBlock["FileInfo"], codeBlock["Code"],
                 codeCloneBlockData["codeCandidateId"], codeCloneBlock["FileInfo"], str(codeCloneSimilarity[0]),
                 str(codeCloneSimilarity[1]), str(codeCloneSimilarity[2]), str(codeBlock["nloc"])
                 ])
    for index, x in enumerate(output):
        a_row = pd.Series([x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10]],
                          index=['codeBlockId', 'codeBlock_start', 'codeBlock_end', 'codeBlock_fileinfo',
                                 'codeblock_Code', 'codeCloneBlockId',
                                 'codeCloneBlock_Fileinfo', 'Similarity_Tokens', 'Similarity_Variable_Flow',
                                 'Similarity_MethodCall_Flow', 'nloc'])
        row_df = pd.DataFrame([a_row])
        df = df.append(row_df)
        # row_df = pd.DataFrame([a_row])
        # df=df.append(row_df)

    return df


def fileLevelBlocks(originalCode):
    """
    input : originalCode
    output : blocks using file level
    """

    allCodeBlocks = []
    commentsRemovedCode = removeCommentsFromCode(originalCode)
    startLine = 1
    endLine = len(commentsRemovedCode)
    allCodeBlocks.append(
        {"Start": startLine, "End": endLine, "Code": commentsRemovedCode})
    return allCodeBlocks


def methodLevelBlocks(originalCode):
    """
    input : originalCode
    output : blocks using method level
    """
    commentsRemovedCode = removeCommentsFromCode(originalCode)
    codeInSingleLine = "\n".join(commentsRemovedCode)

    output = method_extractor(codeInSingleLine)

    allCodeBlocks = []
    if output[0] == None:
        return allCodeBlocks
    for i in range(len(output[0])):
        if abs(output[0][i][1] - output[0][i][0]) < Config.minimumLengthBlock - 1:
            continue
        allCodeBlocks.append(
            {"Start": output[0][i][0], "End": output[0][i][1], "Code": output[1][i].split('\n')})

    return allCodeBlocks


# get all lines of code before detection
# get all clone code lines
# send code blocks to dataset creation

def removeCommentsFromCode(originalCode):
    """
    input : original Code
    output : code without comments 
    """

    DEFAULT = 1
    ESCAPE = 2
    STRING = 3
    ONE_LINE_COMMENT = 4
    MULTI_LINE_COMMENT = 5

    mode = DEFAULT
    strippedCode = []
    for line in originalCode:
        strippedLine = ""
        idx = 0
        while idx < len(line):
            subString = line[idx: min(idx + 2, len(line))]
            c = line[idx]
            if mode == DEFAULT:
                mode = MULTI_LINE_COMMENT if subString == "/*" else ONE_LINE_COMMENT if subString == "//" else STRING if c == '\"' else DEFAULT
            elif mode == STRING:
                mode = DEFAULT if c == '\"' else ESCAPE if c == '\\' else STRING
            elif mode == ESCAPE:
                mode = STRING
            elif mode == ONE_LINE_COMMENT:
                mode = DEFAULT if c == '\n' else ONE_LINE_COMMENT
                idx += 1
                continue
            elif mode == MULTI_LINE_COMMENT:
                mode = DEFAULT if subString == "*/" else MULTI_LINE_COMMENT
                idx += 2 if mode == DEFAULT else 1
                continue
            strippedLine += c if mode < 4 else ""
            idx += 1
        if len(strippedLine) > 0 and strippedLine[-1] == '\n':
            strippedLine = strippedLine[:-1]
        # strippedLine = re.sub('\t| +', ' ', strippedLine)
        strippedCode.append(strippedLine)
    return strippedCode


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

re_string = re.escape("\"") + '.*?' + re.escape("\"")


def getFunctions(filestring, comment_inline_pattern=".*?$"):
    method_string = []
    method_pos = []
    method_name = []

    global found_parent
    found_parent = []

    tree = None

    try:
        tree = javalang.parse.parse(filestring)
        package = tree.package
        if package is None:
            package = 'DefaultPackage'
        else:
            package = package.name
            # print package,'####'
    except Exception as e:
        # logging.warning('Traceback:' + traceback.print_exc())
        return (None, None, [])

    file_string_split = filestring.split('\n')
    # print(file_string_split)
    nodes = itertools.chain(tree.filter(
        javalang.tree.ConstructorDeclaration), tree.filter(javalang.tree.MethodDeclaration))

    for path, node in nodes:
        # print(type(node))
        # print '---------------------------------------'
        name = '.' + node.name
        for i, var in enumerate(reversed(path)):
            # print var, i, len(path)-3
            if isinstance(var, javalang.tree.ClassDeclaration):
                # print 'One Up:',var,var.name
                if len(path) - 3 == i:  # Top most
                    name = '.' + var.name + check_repetition(var, var.name) + name
                else:
                    name = '$' + var.name + check_repetition(var, var.name) + name
            if isinstance(var, javalang.tree.ClassCreator):
                # print 'One Up:',var,var.type.name
                name = '$' + var.type.name + \
                       check_repetition(var, var.type.name) + name
            if isinstance(var, javalang.tree.InterfaceDeclaration):
                # print 'One Up:',var,var.name
                name = '$' + var.name + check_repetition(var, var.name) + name
        # print i,var,len(path)
        # print path
        # while len(path) != 0:
        #  print path[:-1][-1]
        args = []
        for t in node.parameters:
            dims = []
            if len(t.type.dimensions) > 0:
                for e in t.type.dimensions:
                    dims.append("[]")
            dims = "".join(dims)
            args.append(t.type.name + dims)
        args = ",".join(args)

        fqn = ("%s%s(%s)") % (package, name, args)
        # print "->",fqn

        (init_line, b) = node.position
        method_body = []
        closed = 0
        openned = 0

        # print '###################################################################################################'
        # print (init_line,b)
        # print 'INIT LINE -> ',file_string_split[init_line-1]
        # print '---------------------'

        for line in file_string_split[init_line - 1:]:
            # if len(line) == 0:
            #     continue
            # print '+++++++++++++++++++++++++++++++++++++++++++++++++++'
            # print line
            # print comment_inline_pattern
            line_re = re.sub(comment_inline_pattern, '',
                             line, flags=re.MULTILINE)
            line_re = re.sub(re_string, '', line_re, flags=re.DOTALL)

            # print line
            # print '+++++++++++++++++++++++++++++++++++++++++++++++++++'

            closed += line_re.count('}')
            openned += line_re.count('{')
            if (closed - openned) == 0 and openned > 0:
                method_body.append(line)
                break
            else:
                method_body.append(line)

        # print '\n'.join(method_body)

        end_line = init_line + len(method_body) - 1
        method_body = '\n'.join(method_body)

        method_pos.append((init_line, end_line))
        method_string.append(method_body)

        method_name.append(fqn)

    if (len(method_pos) != len(method_string)):
        # logging.warning("File " + file_path + " cannot be parsed. (3)")
        return (None, None, method_name)
    else:
        # logging.warning("File " + file_path + " successfully parsed.")
        return (method_pos, method_string, method_name)


def check_repetition(node, name):
    before = -1
    i = 0
    for (obj, n, value) in found_parent:
        if obj is node:
            if value == -1:
                return ''
            else:
                return '_' + str(value)
        else:
            i += 1
        if n == name:
            before += 1
    found_parent.append((node, name, before))
    if before == -1:
        return ''
    else:
        return '_' + str(before)


def method_extractor(file):
    methodsInfo = []

    FORMAT = '[%(levelname)s] (%(threadName)s) %(message)s'
    # logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    config = ConfigParser()

    # parse existing file
    # try:
    #   config.read(os.path.join(os.path.dirname(
    #      os.path.abspath(__file__)), 'config.ini'))
    # except IOError:
    #   print('ERROR - Config settings not found. Usage: $python this-script.py config-file.ini')
    #  sys.exit()

    separators = "; . [ ] ( ) ~ ! - + & * / % < > ^ | ? { } = # , \" \\ : $ ' ` @"
    comment_inline = "#"
    comment_inline_pattern = comment_inline + '.*?$'

    return getFunctions(file, comment_inline_pattern)

    # allFilesInFolder = GetFiles.getAllFilesUsingFolderPath(folderPath)

    # print(allFilesInFolder)


def getAllFilesUsingFolderPath(folderPath):
    allFilesInFolder = []
    fileCount = 0
    maxCount = 100
    for subdir, dirs, files in os.walk(folderPath):
        for fileName in files:
            fileCount += 1
            if fileName.split(".")[-1] != "java":
                continue
            fileFullPath = os.path.join(subdir, fileName)
            allFilesInFolder.append(fileFullPath)
            if fileCount > maxCount:
                break
    return allFilesInFolder
