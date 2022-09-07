import sys
sys.path.append('//Users/vivekgoud/Documents/GitHub/CodeCloneTrackingSystem_Master_Thesis')

import chars2vecmodel
import sklearn.decomposition
import matplotlib.pyplot as plt
import numpy
import pandas as pd
from sklearn.metrics import DistanceMetric
from scipy.spatial.distance import pdist
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt
import numpy as np
import scipy.cluster.hierarchy as hcluster


def cluster_indices(cluster_assignments):
    n = cluster_assignments.max()
    indices = []
    for cluster_number in range(1, n + 1):
        indices.append(np.where(cluster_assignments == cluster_number)[0])
    return indices


def clonetracingModel(df):
    df = df.drop_duplicates(subset=['codeBlockId', 'Revision', 'codeCloneBlockId'], keep='last')
    df["unique"] = "R1" + df["Revision"].astype(str) + df["codeBlockId"]
    df = df.reset_index(drop=True)
    c2v_model = chars2vecmodel.load_model('ccmodel')

    preprocessed_dataset = df[
        ['codeBlockId', 'codeblock_Code', 'Revision', 'codeBlock_start', 'codeBlock_end', 'codeBlock_fileinfo',
         "unique"]]

    preprocessed_dataset = preprocessed_dataset.drop_duplicates(subset=['codeBlockId', 'Revision'], keep='last')

    codeblock_Code = preprocessed_dataset['codeblock_Code'].tolist()
    # Create word embeddings
    codeblock_Code = c2v_model.vectorize_words(codeblock_Code)
    preprocessed_dataset['emdedding_codeblock_Code'] = codeblock_Code.tolist()
    data = preprocessed_dataset[['unique', 'emdedding_codeblock_Code']]
    dist = DistanceMetric.get_metric('manhattan')  # manhattan euclidean

    manhattan_distance_df = pd.DataFrame(
        dist.pairwise(numpy.asarray([numpy.array(xi) for xi in data['emdedding_codeblock_Code']])),
        columns=data.unique.unique(), index=data.unique.unique())

    # clustering
    thresh = 1.5
    clusters = hcluster.fclusterdata(manhattan_distance_df, thresh, criterion="distance")

    data['clonesets'] = clusters

    # Print the indices of the data points in each cluster.
    num_clusters = clusters.max()
    print("Total %d clonesets" % num_clusters)
    indices = cluster_indices(clusters)
    for k, ind in enumerate(indices):
        print("cloneset", k + 1, "is", ind)
    
    with open('tracking_result.txt', 'w') as f:
        for k, ind in enumerate(indices):
            f.write("cloneset", k + 1, ":") 
            f.write('\t',data.iloc[ind]['unique'].to_list())
    
    final_dataframe = pd.merge(data, df, on='unique', how='inner')

    return final_dataframe

    # scale(manhattan_distance_df)
    # plt.figure(figsize=(50, 12))
    # dend=hcluster.dendrogram(hcluster.linkage(manhattan_distance_df,method='ward'))


def analysis_creating_report(final_dataframe, total_files, cloning_percentage):
    output = final_dataframe[
        ['unique', 'Revision', 'clonesets', 'codeBlockId', 'codeBlock_start', 'codeBlock_end', 'nloc',
         'codeBlock_fileinfo', 'codeCloneBlockId']]
    output = output.drop_duplicates(subset=['unique'], keep='last')
    output = output.sort_values('Revision')

    output['codeBlockId'] = output['codeBlockId'].str.replace('CodeBlock', '')
    output["codeBlockId"] = output["codeBlockId"].astype(int)
    output['Revision'] = output['Revision'].str.replace('R', '')
    output["Revision"] = output["Revision"].astype(int)

    idx = output.index

    output.sort_values(['codeBlockId', 'Revision'], inplace=True)

    output['codeBlock_start_diffs'] = output['codeBlock_start'].diff()
    output['codeBlock_end_diff'] = output['codeBlock_end'].diff()
    output['nloc_diff'] = output['nloc'].diff()

    mask = output.codeBlockId != output.codeBlockId.shift(1)
    output['codeBlock_start_diffs'][mask] = np.nan
    output['codeBlock_end_diff'][mask] = np.nan
    output['nloc_diff'][mask] = np.nan

    output.sort_values(['Revision'], ascending=True, inplace=True)

    output.reindex(idx)

    output.sort_values(["Revision", "codeBlockId"], ascending=True).groupby("codeBlockId").first()

    output['ix'] = output.index
    ix_first = output.sort_values(["Revision", "codeBlockId"], ascending=True).groupby("codeBlockId").first()['ix']
    output['status'] = ''
    output['status'] = output['status'].where(output['ix'].isin(ix_first), 'stable')
    output['status'] = output['status'].replace('', 'new')
    output.loc[output.codeBlock_end_diff > 0, 'status'] = 'Modified/Added'
    output.loc[output.codeBlock_end_diff < 0, 'status'] = 'Modified/removed'
    output['codeBlock_start_diffs'] = output['codeBlock_start_diffs'].replace(np.NaN, 'new')
    output['codeBlock_end_diff'] = output['codeBlock_end_diff'].replace(np.NaN, 'new')
    output['nloc_diff'] = output['nloc_diff'].replace(np.NaN, 'new')
    output = output.drop(columns=['ix'])
    output['disappearing_clone'] = 3
    output = output.set_index(["Revision", 'codeBlockId'])

    index = pd.MultiIndex.from_product(output.index.levels, names=output.index.names)
    output = output.reindex(index, fill_value=2).reset_index(level=1, drop=False).reset_index()

    output.sort_values(['codeBlockId', 'Revision'], inplace=True)

    idx = output.index
    output['disappearing_clone_diffs'] = output['disappearing_clone'].diff()
    mask = output.codeBlockId != output.codeBlockId.shift(1)
    output['disappearing_clone_diffs'][mask] = np.nan
    output['disappearing_clone_diffs'] = output['disappearing_clone_diffs'].replace(-1.0, 'disappearing_clone')
    output = output.drop(columns=['disappearing_clone'])
    output['disappearing_clone_diffs'] = output['disappearing_clone_diffs'].fillna('disappearing_clone')
    output = output.drop(output[(output['disappearing_clone_diffs'] == 0.0) & (output['status'] == 2)].index)
    output.reindex(idx)
    output = output.sort_values('Revision')
    
    with open('tracking_result.txt', 'w') as f:
        
        f.write("cloning_percentage = "+cloning_percentage + "\n")

        f.write("FILE LEVEL INFORMATION")

        f.write("total_files = " + total_files + "\n")
        maxvalue=output['Revision'].max()
        final_revision = output[output.Revision == 4]
        f.write("final_revision = " + final_revision + "\n" )

        maxvalue=output['Revision'].max()
        final_revision = output[output.Revision == maxvalue]

        files_containing_clones = len(pd.unique(final_revision['codeBlock_fileinfo']))#final_revision.codeBlock_fileinfo.count()
        f.write("files_containing_clones",files_containing_clones+ "\n")


        added_files = len(pd.unique(final_revision[final_revision['status']== 'new']['codeBlock_fileinfo']))#

        f.write("added_files",added_files+ "\n")

        deleted_files_df = final_revision[(final_revision.disappearing_clone_diffs == 'disappearing_clone') & (final_revision.status == 2)]

        deleted_files =  len(pd.unique(deleted_files_df.codeBlock_fileinfo))

        f.write("deleted_files",deleted_files+ "\n")

        f.write("CLONESETS INFORMATION")

        total_clone_sets = len(pd.unique(final_revision.clonesets))

        f.write("total_clone_sets",total_clone_sets+ "\n")

        stable_clonesets = len(pd.unique(final_revision[final_revision['status']== 'stable']['clonesets']))

        f.write("stable_clonesets",stable_clonesets+ "\n")

        new_clonesets = len(pd.unique(final_revision[final_revision['status']== 'new']['clonesets']))

        f.write("new_clonesets",new_clonesets+ "\n")

        deleted_clonesets = len(pd.unique(final_revision[(final_revision.disappearing_clone_diffs == 'disappearing_clone') & (final_revision.status == 2)]['clonesets']))

        f.write("deleted_clonesets",deleted_clonesets+ "\n")

        final_revision['status']=final_revision['status'].astype(str)

        changed_clonesets = len(pd.unique(final_revision[final_revision['status'].str.contains('Modified')]['clonesets']))

        f.write("changed_clonesets",changed_clonesets+ "\n")

        f.write("CODECLONES INFORMATION")

        total_codeclones= len(pd.unique(final_revision.codeBlockId))

        f.write("total_codeclones",total_codeclones+ "\n")

        stable_codeclones = len(pd.unique(final_revision[final_revision['status']== 'stable']['codeBlockId']))

        f.write("stable_codeclones",stable_codeclones+ "\n")

        new_codeclones = len(pd.unique(final_revision[final_revision['status']== 'new']['codeBlockId']))

        f.write("new_codeclones",new_codeclones+ "\n")

        deleted_codeclones = len(pd.unique(final_revision[(final_revision.disappearing_clone_diffs == 'disappearing_clone') & (final_revision.status == 2)]['codeBlockId']))

        f.write("deleted_codeclones",deleted_codeclones+ "\n")

        changed_codeclones = len(pd.unique(final_revision[final_revision['status'].str.contains('Modified')]['codeBlockId']))

        f.write("changed_codeclones",changed_codeclones+ "\n")

        f.write('\n' )
        f.close()

    return output
