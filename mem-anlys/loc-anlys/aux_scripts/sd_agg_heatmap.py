# Create intra-region heatmaps for Spatial affinity metrics
# Creates self-*, self, self+* for single metric
    # STEP 1 - Read spatial.txt and write inter-region file
    # STEP 2 - Get region ID's from inter-region file
    # STEP 2a - Add combine regions to the list
    # STEP 3 - Loop through regions in the list and plot heatmaps
        # STEP 3a - Combine regions if there are any - incremental heatmaps are written out as of March 2, 2023
        # STEP 3b - Read original spatial data input file to gather the pages-blocks in the region to a list
        # STEP 3b - Convert list to data frame
        # STEP 3c - Process data frame to get access, lifetime totals
        # STEP 3d - Get average of self before sampling for highest access blocks
        # STEP 3e - Range and Count mean, standard deviation to understand the original spread of heatmap
        # STEP 3e - Range and Count mean, calculate before sampling
        # STEP 3f - Sample dataframe for 50 rows based on access count as the weight
        # STEP 3g - drop columns with "all" NaN values
        # STEP 3g - add some columns above & below self line to visualize better
        # STEP 3h - get columns that are useful
        # STEP 3i - Start Heatmap Visualization

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import re
import csv
import os
import copy
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import datetime
from fileToDataframe import get_intra_obj,getFileColumnNames,getMetricColumns,getRearrangeColumns
from fileToDataframe import getFileColumnNamesPageRegion,getMetricColumnsPageRegion,getPageColListPageRegion
from fileToDataframe import getFileColumnNamesLineRegion,getMetricColumnsLineRegion,getPageColListLineRegion

sns.set_palette(sns.light_palette("seagreen"),100)
sns.set()

def weightMultiply(inValue, multValue):
    return (inValue * multValue)
vectorWeightMultiply = np.vectorize(weightMultiply)
vectorWeightMultiply.excluded.add(1)


# Works for spatial denity, Spatial Probability and Proximity
def intraObjectPlot(strApp, strFileName,numRegion, strMetric=None, f_avg=None,listCombineReg=None,flWeight=None,numExtraPages:int=0,affinityOption:int=None,flPlot=None):
    flagPhysicalPages = 0
    flagHotPages =0
    flagHotLines = 0
    if(affinityOption==1):
        flagPhysicalPages = 1
    elif (affinityOption == 2):
        flagHotPages = 1
    elif (affinityOption == 3):
        flagHotLines = 1
    # STEP 1 - Read spatial.txt and write inter-region file
    strPath=strFileName[0:strFileName.rindex('/')]
    if (strMetric == 'SD' or strMetric == None):
        strMetric='SD'
        fileName='/inter_object_sd.txt'
        lineStart='***'
        lineEnd='==='
        strMetricIdentifier='Spatial_Density'
        strMetricTitle='Spatial Density'
    elif(strMetric == 'SP'):
        fileName='/inter_object_sp.txt'
        lineStart='==='
        lineEnd='---'
        strMetricIdentifier='Spatial_Prob'
        strMetricTitle='Spatial Aniticpation'
    elif(strMetric == 'SI'):
        fileName='/inter_object_si.txt'
        lineStart='---'
        lineEnd='<----'
        strMetricIdentifier='Spatial_Interval'
        strMetricTitle='Spatial Interval'
    strWeight = ''
    if (flWeight == True):
       strWeight = ' Weighted '
    #print(strPath)
    # Write inter-object_sd.txt
    strInterRegionFile=strPath+fileName
    f_out=open(strInterRegionFile,'w')
    with open(strFileName) as f:
        for fileLine in f:
            data=fileLine.strip().split(' ')
            if (data[0] == lineStart):
                #print (fileLine)
                f_out.write(fileLine)
            if (data[0] == lineEnd):
                f_out.close()
                break
    f.close()
    plotFilename=strInterRegionFile
    appName=strApp
    colSelect=0
    sampleSize=0
    print(strFileName, plotFilename, colSelect,appName,sampleSize)
    if(f_avg != None):
        f_avg.write('\nfilename ' + strFileName + ' ' + plotFilename+' col select '+ str(colSelect)+ ' app '+appName+strWeight+ ' sample '+str(sampleSize)+'\n')
    #spatialPlot(plotFilename, colSelect, appName,sampleSize)

    # STEP 2 - Get region ID's from inter-region file
    df_inter=pd.read_table(strInterRegionFile, sep=" ", skipinitialspace=True, usecols=range(2,15),
                     names=['RegionId_Name','Page', 'RegionId_Num','colon', 'ar', 'Address Range', 'lf', 'Lifetime', 'ac', 'Access count', 'bc', 'Block count','Type'])
    df_inter = df_inter[df_inter['Type'] == strMetricIdentifier]
    #print(df_inter)
    df_inter_data=df_inter[['RegionId_Name', 'RegionId_Num', 'Address Range', 'Lifetime', 'Access count', 'Block count']]
    df_inter_data['Reg_Num-Name']=df_inter_data.apply(lambda x:'%s-%s' % (x['RegionId_Num'],x['RegionId_Name']),axis=1)
    numRegionInFile = df_inter_data['RegionId_Num'].count()

    #print(df_inter_data)
    df_inter_data_sample=df_inter_data.nlargest(n=numRegion,  columns=['Access count'])
    arRegionId = df_inter_data_sample['Reg_Num-Name'].values.flatten().tolist()

    # STEP 2a - Add combine regions to the list
    if (listCombineReg != None):
        arRegionId.extend(x for x in listCombineReg if x not in arRegionId)
    arRegionId.sort()
    #print(arRegionId)

    data_list_combine_Reg =[]
    flagProcessCombine=0
    combineCount=0
    # STEP 3 - Loop through regions in the list and plot heatmaps
    for j in range(0, len(arRegionId)):
        regionIdNumName=arRegionId[j]
        regionIdNumName_copy=arRegionId[j]
        regionIdName =regionIdNumName[regionIdNumName.index('-')+1:]
        regionIdNum= regionIdNumName[:regionIdNumName.index('-')]
        print('regionIdName ', regionIdName, 'regionIdNumName ', regionIdNumName, regionIdNum)
        data_list_intra_obj=[]

        # STEP 3a - Combine regions if there are any - incremental heatmaps are written out as of March 2, 2023
        if(listCombineReg != None and regionIdNumName in listCombineReg):
            print('Not None', regionIdNumName)
            if(flagProcessCombine == 0):
                flagProcessCombine=1
                combRegionIdNumName=arRegionId[j]
                arCombRegionAccess = df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Access count'].values.flatten()[0]
                numCombRegionBlocks = df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Block count'].values.flatten()[0]
            else:
                arCombRegionAccess += df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Access count'].values.flatten()[0]
                numCombRegionBlocks += df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Block count'].values.flatten()[0]
                combRegionIdNumName = combRegionIdNumName+' & '+arRegionId[j]
            regionIdNumName = combRegionIdNumName
            arRegionAccess = arCombRegionAccess
            numRegionBlocks = numCombRegionBlocks
        else:
            arRegionAccess = df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Access count'].values.flatten()[0]
            numRegionBlocks = df_inter_data[ df_inter_data['Reg_Num-Name']==regionIdNumName]['Block count'].values.flatten()[0]

        # STEP 3b - Read original spatial data input file to gather the pages-blocks in the region to a list
        if (flagPhysicalPages== 1):
            numExtra = numExtraPages
        elif(flagHotPages ==1):
            numExtra = 10+numRegionInFile+2
        elif(flagHotLines ==1 ):
            numExtra = 10+numRegionInFile+2
        with open(strFileName) as f:
            for fileLine in f:
                data=fileLine.strip().split(' ')
                if (data[0] == lineStart and (data[2][0:len(data[2])-1]) == regionIdName):
                    pageId=data[2][-1]
                    #print('region line' , regionIdNumName, blockId, data[2])
                    get_intra_obj(data_list_intra_obj,fileLine,regionIdNum+'-'+pageId,regionIdNum,numExtra)
        f.close()
        print('**** before regionIdNumName ', regionIdNumName, 'list length', len(data_list_intra_obj))

        if(listCombineReg != None and regionIdNumName_copy in listCombineReg):
            combineCount= combineCount+1
            data_list_combine_Reg.extend(data_list_intra_obj)
            data_list_intra_obj=copy.deepcopy(data_list_combine_Reg)
            print('***** after combineCount ', combineCount, ' regionIdNumName ', regionIdNumName, 'list data_list_intra_obj length', len(data_list_intra_obj), 'list data_list_combine_Reg', len(data_list_combine_Reg))

        if((listCombineReg != None) and (regionIdNumName_copy in listCombineReg) and (combineCount < len(listCombineReg))):
            print(" should break out of loop")
            continue
        else:
            print("Proceed to plot")

        # STEP 3b - Convert list to data frame
        if (flagPhysicalPages== 1):
            list_col_names=getFileColumnNames(numExtraPages)
        elif(flagHotPages == 1):
            list_col_names =getFileColumnNamesPageRegion (regionIdNum, numRegionInFile)
        elif(flagHotLines == 1):
            list_col_names =getFileColumnNamesLineRegion (strFileName, numRegionInFile)
        print((list_col_names))
        df_intra_obj=pd.DataFrame(data_list_intra_obj,columns=list_col_names)
        #print(df_intra_obj[['Address', 'reg-page-blk','self-2','self-1','self','self+1','self+2']])

        # STEP 3c - Process data frame to get access, lifetime totals
        df_intra_obj = df_intra_obj.astype({"Access": int, "Lifetime": int})
        accessSumBlocks= df_intra_obj['Access'].sum()
        arRegPages=df_intra_obj['reg_page_id'].unique()
        #print (arRegionBlocks)
        
        arRegPageAccess = np.empty([len(arRegPages),1])
        for arRegPageId in range(0, len(arRegPages)):
            #print(arRegionBlockId, df_intra_obj[df_intra_obj['blockid']==arRegionBlocks[arRegionBlockId]]['Access'].sum())
            arRegPageAccess[int(arRegPageId)] = df_intra_obj[df_intra_obj['reg_page_id']==arRegPages[arRegPageId]]['Access'].sum()
        #print (arBlockIdAccess)
        print(arRegPageAccess.shape)
        listCombine = zip(arRegPages, arRegPageAccess.tolist())
        df_reg_pages = pd.DataFrame(listCombine, columns=('reg-page', 'Access'))
        #df_reg_pages = df_reg_pages.astype({"Access": int})
        df_reg_pages.set_index('reg-page')
        df_reg_pages.sort_index(inplace=True)
        df_reg_pages["Access"] = df_reg_pages["Access"].apply(pd.to_numeric)
        df_reg_pages = df_reg_pages.astype({"Access": int})
        df_reg_pages.sort_values(by=['Access'],ascending=False,inplace=True)
        arRegPageAccess=(df_reg_pages[['Access']]).to_numpy()
        arRegPages=df_reg_pages['reg-page'].to_list()

        # Change data to numeric
        if(flagPhysicalPages ==1):
            metricColumns = getMetricColumns(numExtraPages)
        elif(flagHotPages == 1):
            metricColumns = getMetricColumnsPageRegion(regionIdNum, numRegionInFile)
        elif(flagHotLines == 1):
            metricColumns = getMetricColumnsLineRegion(regionIdNum, numRegionInFile)

        for i in range (0,len(metricColumns)):
            df_intra_obj[metricColumns[i]]=pd.to_numeric(df_intra_obj[metricColumns[i]])

        # STEP 3d - Get average of self before sampling for highest access blocks
        average_sd= pd.to_numeric(df_intra_obj["self"]).mean()
        print('*** Before sampling , weighted = ' +str(flWeight)+'Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd))
        if (f_avg != None):
            if(flWeight):
                f_avg.write ( '*** Before sampling Weighted Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd)+'\n')
            else:
                f_avg.write ( '*** Before sampling Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd)+'\n')

        print(df_intra_obj.columns.to_list())
        colRearrangeList =[]
        if ((numExtraPages !=0) and (flagPhysicalPages ==1)):
            #print('in numExtraPages NOT 0')
            colRearrangeList = getRearrangeColumns(df_intra_obj.columns.to_list())
        else:
            #print('in numExtraPages 0')
            colRearrangeList = df_intra_obj.columns.to_list()

        df_intra_obj = df_intra_obj[colRearrangeList]
        df_intra_obj.drop('Type',axis=1,inplace=True)
        colNameList =df_intra_obj.columns.to_list()
        print(colNameList)
        # Adding weighting by page access total here
        if (flWeight == True):
            #print('before weight \n ' , df_intra_obj[['reg-page-blk', 'Access', 'self', 'self+1', 'self-255']])
            normSDMax=np.ones(len(arRegPages))
            list_DF_Intra_obj = df_intra_obj.values.tolist()
            #print(list_DF_Intra_obj)
            for i in range (0, len(list_DF_Intra_obj)):
                regPageId = list_DF_Intra_obj[i][0]
                regPageBlkId = list_DF_Intra_obj[i][1]
                weightAccess = (df_reg_pages[(df_reg_pages['reg-page'] == regPageId)]['Access'].item())
                percentAccess = df_intra_obj[(df_intra_obj['reg-page-blk'] == regPageBlkId)]['Access'].item() * (100 / weightAccess)
                #print('percentAccess ', percentAccess)
                arRegPageIndex = arRegPages.index(regPageId)
                for j in range(5, len(list_DF_Intra_obj[i])):
                    list_DF_Intra_obj[i][j]=list_DF_Intra_obj[i][j]*percentAccess
                    if ((normSDMax[arRegPageIndex]) < list_DF_Intra_obj[i][j]):
                            normSDMax[arRegPageIndex] = list_DF_Intra_obj[i][j]
            df_intra_obj=pd.DataFrame(list_DF_Intra_obj,columns=(colNameList))

            for colName in metricColumns:
                df_intra_obj[colName]=pd.to_numeric(df_intra_obj[colName])

            #print('before normalize \n ' , df_intra_obj[['reg-page-blk', 'Access', 'self', 'self+1']])
            arRegPageIndex = 0
            for regPageId in arRegPages:
                for colName in metricColumns:
                    df_intra_obj.loc[df_intra_obj['reg_page_id'] == regPageId,[colName]] = df_intra_obj.loc[df_intra_obj['reg_page_id'] == regPageId, [colName]].div(normSDMax[arRegPageIndex])
                arRegPageIndex = arRegPageIndex + 1

            #print('afer normalize \n ' , df_intra_obj[['reg-page-blk', 'Access', 'self', 'self+1']])

        # STEP 3e - Range and Count mean, standard deviation to understand the original spread of heatmap
        # STEP 3e - Range and Count mean, calculate before sampling
        # START Lexi-BFS - experiment #3 - SD range & gap analysis
        print('dataframe row count', len(df_intra_obj))
        #print(df_intra_obj['Access'])
        df_intra_obj_sort=df_intra_obj.sort_values(by=['Access'],ascending=False)
        sumAccess = df_intra_obj_sort['Access'].sum()
        #print(df_intra_obj_sort['Access'])
        print(sumAccess)
        #print(df_intra_obj_sort.columns)
        list_SD_range_gap=[]
        #print('self columns ',df_intra_obj_sort.iloc[0,5:(516)] )
        blkAccessPercent =0
        sumBlkAccess =0
        hotRefMaxAccess=df_intra_obj_sort['Access'].max()
        hotRefMinAccess=df_intra_obj_sort['Access'].min()
        refRange=hotRefMaxAccess-hotRefMinAccess
        #print((df_SP_SI_SD['Access']-hotRefMinAccess)/refRange)
        if (strMetric == 'SD'):
            for df_id in range (0, len(df_intra_obj_sort)):
                #blkAccessPercent = float(sumBlkAccess / sumAccess)
                #if(blkAccessPercent <= 1.0 ):
                    #print(' % ' , blkAccessPercent)
                blk_id=df_intra_obj_sort.iloc[df_id,1]
                blk_access = df_intra_obj_sort.iloc[df_id,2]
                if( (blk_access - hotRefMinAccess) / refRange > 0.1):
                    #sumBlkAccess += blk_access
                    #print(blk_id, blk_access)
                    df_row=pd.to_numeric(df_intra_obj_sort.iloc[df_id,5:(516)]).squeeze()
                    first_index=df_row.first_valid_index()
                    last_index=df_row.last_valid_index()

                    if ( first_index == 'self'):
                        first_value=0
                    else:
                        first_value=int(''.join(filter(str.isdigit, first_index)))
                    if ( last_index == 'self'):
                        last_value=0
                    else:
                        last_value=int(''.join(filter(str.isdigit, last_index)))
                    valid_range=first_value+last_value+1
                    #print(blk_id, blk_access, first_index, last_index, valid_range)

                    list_SD_range_gap.append([blk_id,blk_access, first_value,last_value,valid_range, df_row.count() ])

            #print(list_SD_range_gap)
            df_range_gap=pd.DataFrame(list_SD_range_gap,columns=['reg-page-blk','Access', 'first','last','range','count'])
            df_range_gap = df_range_gap.astype({"range": int, "count": int})
            print(strApp,' ', strMetric, ', Region ', regionIdNumName.replace(' ','').replace('&','-'), ' Range mean ', pd.to_numeric(df_range_gap["range"]).mean())
            print(strApp,' ', strMetric, ', Region ', regionIdNumName.replace(' ','').replace('&','-'), ' Range std ', pd.to_numeric(df_range_gap["range"]).std())
            print(strApp,' ', strMetric, ', Region ', regionIdNumName.replace(' ','').replace('&','-'), ' Count mean ', pd.to_numeric(df_range_gap["count"]).mean())
            print(strApp,' ', strMetric, ', Region ', regionIdNumName.replace(' ','').replace('&','-'), ' Count std ', pd.to_numeric(df_range_gap["count"]).std())
            # END Lexi-BFS - experiment #3 - SD range & gap analysis

            if(f_avg != None):
                f_avg.write(strApp+' '+ strMetric+ ' '+', Region '+regionIdNumName.replace(' ','').replace('&','-')+strWeight+ ' Range mean '+ str(pd.to_numeric(df_range_gap["range"]).mean())+'\n')
                f_avg.write(strApp+' '+ strMetric+ ' '+', Region '+regionIdNumName.replace(' ','').replace('&','-')+strWeight+ ' Range std '+ str(pd.to_numeric(df_range_gap["range"]).std())+'\n')
                f_avg.write(strApp+' '+ strMetric+ ' '+', Region '+regionIdNumName.replace(' ','').replace('&','-')+strWeight+ ' Count mean '+ str(pd.to_numeric(df_range_gap["count"]).mean())+'\n')
                f_avg.write(strApp+' '+ strMetric+ ' '+', Region '+regionIdNumName.replace(' ','').replace('&','-')+strWeight+ ' Count std '+ str(pd.to_numeric(df_range_gap["count"]).std())+'\n')

        elif (strMetric == 'SP' or strMetric =='SI'):
            list_SP_range=[]
            for df_id in range (0, len(df_intra_obj_sort)):
                blkAccessPercent = float(sumBlkAccess / sumAccess)
                if(blkAccessPercent <= 0.9 ):
                    blk_id=df_intra_obj_sort.iloc[df_id,1]
                    blk_access = df_intra_obj_sort.iloc[df_id,2]
                    sumBlkAccess += blk_access
                    print(blk_id, blk_access, ' % ' , blkAccessPercent,df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self'].item(), \
                          df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self+1'].item(), df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self+2'].item())
                    list_SP_range.append([blk_id,blk_access, df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self'].item(), \
                                        df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self+1'].item(), \
                                        df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self+2'].item(),\
                                        df_intra_obj_sort[df_intra_obj_sort['reg-page-blk'] == blk_id]['self+3'].item()] )

            df_range_gap=pd.DataFrame(list_SP_range,columns=['reg-page-blk','Access', 'self','self+1','self+2','self+3'])
            df_range_gap = df_range_gap.astype({"self": float, "self+1": float, "self+2": float, "self+3":float})
            percentileValue =df_range_gap['self'].quantile(0.01)
            #print(df_range_gap['self'].quantile(0.01))
            #print(df_range_gap[(df_range_gap.self > percentileValue)]['self'])
            print(strApp,' ', strMetric, ' Region ',regionIdNumName.replace(' ','').replace('&','-'), \
                  'self = ', df_range_gap[(df_range_gap.self > percentileValue)]['self'].min(), df_range_gap['self'].max(), 'self+1 = ', df_range_gap['self+1'].min(),  df_range_gap['self+1'].max(), \
                  "self+2 = ", df_range_gap['self+2'].mean())


        if(flPlot != False):
            # STEP 3f - Sample dataframe for 50 rows based on access count as the weight
            # Sample 50 reg-page-blkid lines from all blocks based on Access counts
            num_sample=50
            df_intra_obj_rows=df_intra_obj.shape[0]
            if ( df_intra_obj_rows < num_sample):
                num_sample = df_intra_obj_rows

            #print('self before sample ', df_intra_obj['self'])
            df_intra_obj_sample=df_intra_obj.nlargest(num_sample, 'Access')
            df_intra_obj_sample.set_index('reg-page-blk')
            df_intra_obj_sample.sort_index(inplace=True)
            df_intra_obj_sample.sort_values(by=['Access'],ascending=False,inplace=True)
            list_xlabel=df_intra_obj_sample['reg-page-blk'].to_list()
            accessBlockCacheLine = (df_intra_obj_sample[['Access']]).to_numpy()
            colHeatMap= [x for x in colRearrangeList if x in metricColumns]
            df_intra_obj_sample_hm=df_intra_obj_sample[colHeatMap]
            #print('self in sample ', df_intra_obj_sample['self'])
            self_bef_drop=df_intra_obj_sample_hm['self'].to_list()

            # STEP 3g - drop columns with "all" NaN values
            # DROP - columns with no values
            average_sd= pd.to_numeric(df_intra_obj["self"]).mean()
            print('*** After weighting sampling Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd))
            if (f_avg != None):
                f_avg.write ( '*** After weighting sampling Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd)+'\n')

            get_col_list=df_intra_obj_sample_hm.columns.to_list()
            print('before drop', get_col_list)
            #print('before drop self \n', df_intra_obj_sample_hm['self'])
            df_intra_obj_drop=df_intra_obj_sample_hm.dropna(axis=1,how='all')
            get_col_list=df_intra_obj_drop.columns.to_list()
            print('after drop', get_col_list)
            # STEP 3g - add some columns above & below self line to visualize better
            flAddSelfBelow=1
            flAddSelfAbove=1
            pattern = re.compile('self-.*')
            if any((match := pattern.match(x)) for x in get_col_list):
                flAddSelfBelow=0
            pattern = re.compile('self\+.*')
            if any((match := pattern.match(x)) for x in get_col_list):
                #print(match.group(0))
                flAddSelfAbove=0
            if(flAddSelfBelow == 1):
                for i in range (1,10):
                    get_col_list.insert(0,'self-'+str(i))
            if(flAddSelfAbove == 1):
                for i in range (1,10):
                    get_col_list.append('self+'+str(i))

            # STEP 3h - get columns that are useful
            df_intra_obj_sample_hm=df_intra_obj_sample[get_col_list]
            print(df_intra_obj_sample_hm.columns.to_list())
            average_sd= pd.to_numeric(df_intra_obj_sample_hm["self"]).mean()
            print('*** After sampling Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+' '+str(average_sd))
            if (f_avg != None):
                f_avg.write ( '*** After sampling Average '+strMetric+' for '+strApp+', Region '+regionIdNumName.replace(' ','').replace('&','-')+strWeight+' '+str(average_sd)+'\n')
            self_aft_drop=df_intra_obj_sample_hm['self'].to_list()
            #print(self_aft_drop)
            if(self_bef_drop == self_aft_drop):
                print(" After drop equal ")
            else:
                print("Error - not equal")
                print ("before drop", self_bef_drop)
                print ("after drop", self_aft_drop)
                break

            # STEP 3i - Start Heatmap Visualization
            df_intra_obj_sample_hm.apply(pd.to_numeric)
            df_hm=np.empty([num_sample,len(get_col_list)])
            df_hm=df_intra_obj_sample_hm.to_numpy()
            df_hm=df_hm.astype('float64')
            df_hm=df_hm.transpose()

            #fig, ax =plt.subplots(1,3, figsize=(15, 10),gridspec_kw={'width_ratios': [11, 1.5, 1.5]})
            fig = plt.figure(constrained_layout=True, figsize=(15, 10))
            gs = gridspec.GridSpec(1, 2, figure=fig,width_ratios=[12,3])
            gs0 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec = gs[0] )
            gs1 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec = gs[1] ,wspace=0.07)
            ax_0 = fig.add_subplot(gs0[0, :])
            ax_1 = fig.add_subplot(gs1[0, 0])
            ax_2 = fig.add_subplot(gs1[0, 1])

            if(strMetric == 'SI'):
                vmin_val=0.0
                vmax_val=100.0
            else:
                vmin_val=0.02
                vmax_val=1.0

            if (1 == 0 and 'minivite' in strApp.lower() and strMetric == 'SI'):
                df_mask = df_intra_obj_sample_hm.applymap(lambda x: True if (x >150) else False).transpose().to_numpy().astype(bool)
                #print(df_mask,' \n', df_hm)
                print ('mask ', df_mask.shape, ' df_hm ', df_hm.shape)
                ax_0 = sns.heatmap(df_hm, mask=df_mask, cmap='mako',cbar=True, annot=False,ax=ax_0,vmin=0,vmax=20)

            ax_0 = sns.heatmap(df_hm,cmap='mako_r',cbar=True, annot=False,ax=ax_0,vmin=vmin_val,vmax=vmax_val)
            ax_0.set_facecolor('white')
            # Colors for Access heatmap, and labels for affinity matrix
            custom_blue = sns.light_palette("#79C")
            background_color = mpl.colormaps["Blues"]
            fig_xlabel=[]
            color_xlabel=[]
            my_colors=[]
            accessLowValue = accessBlockCacheLine.min()
            accessHighValue = accessBlockCacheLine.max()
            accessRange= accessHighValue-accessLowValue
            hotLineColor='darkred'
            affRegionColor='dodgerblue'
            hotLineInRegionColor='indianred'
            refRegionColor='black'
            pattern = re.compile('.*-.*-.*')
            listAffinityLines=list(filter(pattern.match, get_col_list))
            print('hot lines in affinity', listAffinityLines)
            refRgionNamelist = regionIdNumName.replace(' ','').split('&')
            refRegionList=[]
            print(refRgionNamelist)
            for item in refRgionNamelist:
                print('region id', item.split('-')[0])
                refRegionList.append(item.split('-')[0])

            ax_0.invert_yaxis()
            list_y_ticks=ax_0.get_yticklabels()
            fig_ylabel=[]
            for y_label in list_y_ticks:
                if ('self' in get_col_list[int(y_label.get_text())]):
                    fig_ylabel.append(get_col_list[int(y_label.get_text())][4:])
                else:
                    strColName = get_col_list[int(y_label.get_text())]
                    if(strColName.find('^') != -1):
                        strColName=strColName.replace('[2','[$2').replace('2^','2^{').replace('-2','}$-$2').replace(')','}$)')
                    if((strColName.find('r-') != -1)):
                        strColName=get_col_list[int(y_label.get_text())][2:]
                    fig_ylabel.append(strColName)
            ax_0.set_yticklabels(fig_ylabel,rotation='horizontal')
            for ticklabel in ax_0.get_yticklabels():
                #print(ticklabel.get_text())
                if(ticklabel.get_text().count('-')==2):
                    if(ticklabel.get_text().split('-')[0]  in refRegionList):
                        #print(ticklabel.get_text(), ' color ', hotLineInRegionColor)
                        ticklabel.set_color(hotLineInRegionColor)
                    else:
                        #print(ticklabel.get_text(), ' color ', hotLineColor)
                        ticklabel.set_color(hotLineColor)
                elif(ticklabel.get_text().isdigit()):
                    if(ticklabel.get_text()  in refRegionList):
                        #print(ticklabel.get_text(), ' color ', refRegionColor)
                        ticklabel.set_color(refRegionColor)
                    else:
                        #print(ticklabel.get_text(), ' color ', affRegionColor)
                        ticklabel.set_color(affRegionColor)

            list_x_ticks=ax_0.get_xticklabels()
            for x_label in list_x_ticks:
                fig_xlabel.append(list_xlabel[int(x_label.get_text())])
                color_xlabel.append((accessBlockCacheLine[int(x_label.get_text())].item()-accessLowValue)/accessRange)
                my_colors.append(background_color((accessBlockCacheLine[int(x_label.get_text())].item()-accessLowValue)/accessRange))
            ax_0.set_xticklabels(fig_xlabel,rotation='vertical')
            ax_0.set(xlabel="Region-Page-Block", ylabel="Affinity to contiguous blocks")
            #print(color_xlabel)
            i=0
            for ticklabel, tickcolor in zip(ax_0.get_xticklabels(), my_colors):
                if(color_xlabel[i]>0.5):
                    ticklabel.set_color('white')
                ticklabel.set_backgroundcolor(tickcolor)
                ticklabel.set_fontsize(10)
                i = i+1

            #ax_0.set_ylabel("")
            sns.heatmap(accessBlockCacheLine, cmap="Blues", cbar=False,annot=True, fmt='g', annot_kws = {'size':12},  ax=ax_1)
            ax_1.set_facecolor('white')

            #ax_1.invert_yaxis()
            ax_1.set_xticks([0])
            length_xlabel= len(list_xlabel)
            list_blkcache_label=[]
            for i in range (0, length_xlabel):
                list_blkcache_label.append(list_xlabel[i])
            #print(range(0,len(list_blkcache_label)))
            #ax_1.set_yticks(range(0,len(list_blkcache_label)),list_blkcache_label, rotation='horizontal',  wrap=True )
            ax_1.set_yticklabels(list_blkcache_label, rotation='horizontal', wrap=True )
            ax_1.yaxis.set_ticks_position('right')

            rndAccess = np.round((arRegPageAccess/1000).astype(float),2)
            annot = np.char.add(rndAccess.astype(str), 'K')
            sns.heatmap(rndAccess, cmap=custom_blue, cbar=False,annot=annot, fmt='', annot_kws = {'size':12},  ax=ax_2)
            ax_2.set_facecolor('white')

            #ax_2.invert_yaxis()
            ax_2.set_xticks([0])
            list_blk_label=arRegPages
            ax_2.set_yticklabels(list_blk_label, rotation='horizontal', wrap=True )
            ax_2.yaxis.set_ticks_position('right')

            plt.suptitle(strMetricTitle +' and Access heatmap for '+strApp +' region - '+regionIdNumName)
            strArRegionAccess = str(np.round((arRegionAccess/1000).astype(float),2))+'K'
            strAccessSumBlocks= str(np.round((accessSumBlocks/1000).astype(float),2))+'K'
            strTitle = strMetricTitle+' \n Region\'s access - ' + strArRegionAccess + ', Access count for selected pages - ' + strAccessSumBlocks \
                       +' ('+ ("{0:.1f}".format((accessSumBlocks/arRegionAccess)*100)) +'%)\n Number of pages in region - '+ str(numRegionBlocks)
            #print(strTitle)
            ax_0.set_title(strTitle)
            ax_1.set_title('Access count for selected blocks and \n          hottest pages in the region\n ',loc='left')

            #plt.show()
            fileNameLastSeg = '_hm_order.pdf'
            if (flWeight == True):
                fileNameLastSeg = '_hm_order_Wgt.pdf'
            imageFileName=strPath+'/'+strApp.replace(' ','')+'-'+regionIdNumName.replace(' ','').replace('&','-')+'-'+strMetric+fileNameLastSeg
            print(imageFileName)
            plt.savefig(imageFileName, bbox_inches='tight')
            plt.close()



flWeight = False
mainPath='/Users/suri836/Projects/spatial_rud/'
numExtraPages=64

#intraObjectPlot('Alpaca',mainPath+'spatial_pages_exp/alpaca/mg-alpaca/chat-trace-b8192-p5000000/spatial.txt',3,strMetric='SD', \
#            flWeight=flWeight,affinityOption=3)
if(1):
    f_avg1=None
    #f_avg1=open(mainPath+'spatial_pages_exp/miniVite/hot_lines/sd_avg_log_new.txt','w')
    intraObjectPlot('miniVite-v1',mainPath+'spatial_pages_exp/miniVite/hot_lines/v1_spatial_det.txt',1,strMetric='SD', \
             flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)
    #intraObjectPlot('miniVite-v1',mainPath+'spatial_pages_exp/miniVite/hot_lines/v1_spatial_det.txt',1,strMetric='SP', \
    #         flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)
    #intraObjectPlot('miniVite-v1',mainPath+'spatial_pages_exp/miniVite/hot_lines/v1_spatial_det.txt',1,strMetric='SI', \
    #         flWeight=False,affinityOption=3,f_avg=f_avg1,flPlot=False)
    #intraObjectPlot('miniVite-v3',mainPath+'spatial_pages_exp/miniVite/hot_lines/v3_spatial_det.txt',3,strMetric='SD', \
    #        listCombineReg=['1-A0000001','5-A0001200'] ,flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)
    intraObjectPlot('miniVite-v2',mainPath+'spatial_pages_exp/miniVite/hot_lines/v2_spatial_det.txt',3,strMetric='SD', \
            listCombineReg=['1-A0000010','4-A0002000'] ,flWeight=flWeight,affinityOption=3,f_avg=f_avg1)

    intraObjectPlot('miniVite-v3',mainPath+'spatial_pages_exp/miniVite/hot_lines/v3_spatial_det.txt',3,strMetric='SD', \
            listCombineReg=['1-A0000001','5-A0001200'] ,flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)

  #  intraObjectPlot('miniVite-v2',mainPath+'spatial_pages_exp/miniVite/hot_lines/v2_spatial_det.txt',3,strMetric='SD', \
  #          listCombineReg=['1-A0000010','4-A0002000'] ,flWeight=flWeight,affinityOption=3,f_avg=f_avg1)
  #  intraObjectPlot('miniVite-v3',mainPath+'spatial_pages_exp/miniVite/hot_lines/v3_spatial_det.txt',3,strMetric='SD', \
  #          listCombineReg=['1-A0000001','5-A0001200'] ,flWeight=flWeight,affinityOption=3,f_avg=f_avg1)
    #f_avg1.close()

if (0):
    f_avg1=None
    #f_avg1=open(mainPath+'spatial_pages_exp/XSBench/openmp-threading-noinline/memgaze-xs-sel-gs-2/sd_avg_log.txt','w')
    intraObjectPlot('XSB-rd-EVENT_k0', \
        mainPath+'spatial_pages_exp/XSBench/openmp-threading-noinline/memgaze-xs-sel-gs-2/XSBench-memgaze-trace-b32768-p3000000-event-k-0/hot-insn/spatial.txt', 10, strMetric='SD', \
        listCombineReg=['8-B0060001', '9-B0060002'],flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)
    intraObjectPlot('XSB-rd-EVENT_OPT_k1', \
        mainPath+'spatial_pages_exp/XSBench/openmp-threading-noinline/memgaze-xs-sel-gs-2/XSBench-memgaze-trace-b32768-p3000000-event-k-1/hot-insn/spatial.txt', \
        9, strMetric='SD', \
        listCombineReg=['7-HotIns-02','8-HotIns-01'], flWeight=flWeight,affinityOption=3,f_avg=f_avg1,flPlot=False)
    #f_avg1.close()

if(0):
    f_avg1=open(mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/sd_avg_log.txt','w')
    intraObjectPlot('HiParTi - CSR',mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/csr/spatial.txt',2,f_avg=f_avg1,strMetric='SD',\
                    flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTi - COO',mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/coo_u_0/spatial.txt',3,f_avg=f_avg1,\
                    listCombineReg=['1-A0000010','2-A0000020'], strMetric='SD', flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTi - COO-Reduce',mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/coo_u_1/spatial.txt', \
                    2,listCombineReg=['0-A0000000', '1-A1000000', '2-A2000000','3-A2000010'],f_avg=f_avg1, strMetric='SD', flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTi - HiCOO',mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/hicoo_u_0/spatial.txt',2,f_avg=f_avg1,strMetric='SD', \
                    flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTi - HiCOO-Schedule',mainPath+'spatial_pages_exp/HICOO-matrix/4096-same-iter/hot_lines/hicoo_u_1/spatial.txt',2,f_avg=f_avg1,strMetric='SD', \
                    flWeight=flWeight,affinityOption=3)
    f_avg1.close()

if(0):
    f_avg1=open(mainPath+'spatial_pages_exp/HICOO-tensor/sd_avg_log.txt','w')
    intraObjectPlot('HiParTI-HiCOO', mainPath+'spatial_pages_exp/HICOO-tensor/mttsel-re-0-b16384-p4000000-U-0/hot_lines/spatial.txt', 1,\
                    f_avg=f_avg1,strMetric='SD',flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTI-HiCOO-Lexi', mainPath+'spatial_pages_exp/HICOO-tensor/mttsel-re-1-b16384-p4000000-U-0/hot_lines/spatial.txt', 1,\
                    f_avg=f_avg1,strMetric='SD',flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTI-HiCOO-BFS', mainPath+'spatial_pages_exp/HICOO-tensor/mttsel-re-2-b16384-p4000000-U-0/hot_lines/spatial.txt', 1,\
                    f_avg=f_avg1,strMetric='SD',flWeight=flWeight,affinityOption=3)
    intraObjectPlot('HiParTI-HiCOO-Random', mainPath+'spatial_pages_exp/HICOO-tensor/mttsel-re-3-b16384-p4000000-U-0/hot_lines/spatial.txt', 1,\
                    f_avg=f_avg1,strMetric='SD',flWeight=flWeight,affinityOption=3)
    f_avg1.close()

if ( 1 == 0):
    #f_avg1=open(mainPath+'HiParTi/4096-same-iter/sd_agg_log_Wgt','w')
    f_avg1=None
    now = datetime.datetime.now()
    print(now)
    intraObjectPlot('HiParTi - HiCOO-Schedule',mainPath+'HiParTi/4096-same-iter/mg-spmm-hicoo/spmm_hicoo-U-1-trace-b8192-p4000000/spatial.txt',3,f_avg=f_avg1,flWeight=flWeight)
    now = datetime.datetime.now()
    print(now)
    f_avg1.close()

# HiParTI - HiCOO - Reorder heatmaps
if (1 ==0):
    f_avg1=open(mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/sd_avg_log_Wgt','w')
    intraObjectPlot('HiParTI-HiCOO', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-0-b16384-p4000000-U-0/sp-si/spatial.txt', 1, flWeight=flWeight, f_avg=f_avg1)
    intraObjectPlot('HiParTI-HiCOO-Lexi', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-1-b16384-p4000000-U-0/sp-si/spatial.txt', 1,flWeight=flWeight, f_avg=f_avg1)
    intraObjectPlot('HiParTI-HiCOO-BFS', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-2-b16384-p4000000-U-0/sp-si/spatial.txt', 1,flWeight=flWeight, f_avg=f_avg1)
    intraObjectPlot('HiParTI-HiCOO-Random', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-3-b16384-p4000000-U-0/sp-si/spatial.txt', 1,flWeight=flWeight, f_avg=f_avg1)
    f_avg1.close()

if ( 1 == 0):
    intraObjectPlot('HiParTI-HiCOO', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-0-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SP')
    intraObjectPlot('HiParTI-HiCOO', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-0-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SI')
    intraObjectPlot('HiParTI-HiCOO-Lexi', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-1-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SP')
    intraObjectPlot('HiParTI-HiCOO-Lexi', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-1-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SI')
    intraObjectPlot('HiParTI-HiCOO-BFS', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-2-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SP')
    intraObjectPlot('HiParTI-HiCOO-BFS', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-2-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SI')
    intraObjectPlot('HiParTI-HiCOO-Random', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-3-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SP')
    intraObjectPlot('HiParTI-HiCOO-Random', mainPath+'HiParTi/mg-tensor-reorder/nell-U-0/mttsel-re-3-b16384-p4000000-U-0/sp-si/spatial.txt', 1, 'SI')

if (1 ==0):
    intraObjectPlot('miniVite-v2',mainPath+'minivite_detailed_look/inter-region/v2_spatial_det.txt',3,strMetric='SP', listCombineReg=['1-A0000010','4-A0002000'] )
    intraObjectPlot('miniVite-v3',mainPath+'minivite_detailed_look/inter-region/v3_spatial_det.txt',3,strMetric='SP', listCombineReg=['1-A0000001','5-A0001200'] )
    intraObjectPlot('miniVite-v1',mainPath+'minivite_detailed_look/inter-region/v1_spatial_det.txt',1,strMetric='SI')
    intraObjectPlot('miniVite-v2',mainPath+'minivite_detailed_look/inter-region/v2_spatial_det.txt',3,strMetric='SI', listCombineReg=['1-A0000010','4-A0002000'] )
    intraObjectPlot('miniVite-v3',mainPath+'minivite_detailed_look/inter-region/v3_spatial_det.txt',3,strMetric='SI', listCombineReg=['1-A0000001','5-A0001200'] )

# HiParTi - Tensor variants - Use buffer
#intraObjectPlot('HiParTI-HiCOO ', mainPath+'HiParTi/mg-tensor-reorder/nell-U-1/mttsel-re-0-b16384-p4000000-U-1/spatial.txt', 2)
#intraObjectPlot('HiParTI-HiCOO Lexi', mainPath+'HiParTi/mg-tensor-reorder/nell-U-1/mttsel-re-1-b16384-p4000000-U-1/spatial.txt', 4)
#intraObjectPlot('HiParTI-HiCOO BFS', mainPath+'HiParTi/mg-tensor-reorder/nell-U-1/mttsel-re-2-b16384-p4000000-U-1/spatial.txt', 3)
#intraObjectPlot('HiParTI-HiCOO Random', mainPath+'HiParTi/mg-tensor-reorder/nell-U-1/mttsel-re-3-b16384-p4000000-U-1/spatial.txt', 4)

# HiParTi - Tensor variants - Freebase tensor
#intraObjectPlot('HiParTI-HiCOO ', mainPath+'HiParTi/mg-tensor-reorder/fb-U-0/mttsel-fb-re-0-b16384-p4000000-U-0/spatial.txt', 3)
#intraObjectPlot('HiParTI-HiCOO Lexi', mainPath+'HiParTi/mg-tensor-reorder/fb-U-0/mttsel-fb-re-1-b16384-p4000000-U-0/spatial.txt', 2)
#intraObjectPlot('HiParTI-HiCOO BFS', mainPath+'HiParTi/mg-tensor-reorder/fb-U-0/mttsel-fb-re-2-b16384-p4000000-U-0/spatial.txt', 4)
#intraObjectPlot('HiParTI-HiCOO Random', mainPath+'HiParTi/mg-tensor-reorder/fb-U-0/mttsel-fb-re-3-b16384-p4000000-U-0/spatial.txt', 3)

# ParTi - Tensor variants
#intraObjectPlot('ParTI-COO - m-0', mainPath+'HiParTi/mg-tensor/mttkrp-m-0-sel-trace-b8192-p5000000/spatial.txt', 6)
#intraObjectPlot('ParTI-COO - m-1', mainPath+'HiParTi/mg-tensor/mttkrp-m-1-sel-trace-b8192-p5000000/spatial.txt', 6)
#intraObjectPlot('ParTI-COO - m-2', mainPath+'HiParTi/mg-tensor/mttkrp-m-2-sel-trace-b8192-p5000000/spatial.txt', 6)

#intraObjectPlot('ParTI-HiCOO - m-0', mainPath+'HiParTi/mg-tensor/mttkrp_hicoo-m-0-sel-trace-b8192-p5000000/spatial.txt', 2)
#intraObjectPlot('ParTI-HiCOO - m-1', mainPath+'HiParTi/mg-tensor/mttkrp_hicoo-m-1-sel-trace-b8192-p5000000/spatial.txt', 3)
#intraObjectPlot('ParTI-HiCOO - m-2', mainPath+'HiParTi/mg-tensor/mttkrp_hicoo-m-2-sel-trace-b8192-p5000000/spatial.txt', 2)

