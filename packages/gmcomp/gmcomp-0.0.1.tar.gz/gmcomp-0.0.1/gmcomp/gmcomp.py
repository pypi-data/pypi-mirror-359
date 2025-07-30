#!/usr/bin/python3

import os, sys, argparse, warnings, itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


#plot feature offsets
def plot_feature_offsets(ll,fl,feature_list,io):
    #grid spec
    fig,ax = plt.subplots(figsize= (5*len(fl),5*len(fl)), ncols=len(fl),nrows=len(fl))
    
    #pairwise comparisons. loop over combinations of 2 elements.
    for i in list(itertools.combinations([0,1,2,3],2)):
        #start
        t1 = pd.concat([fl[i[0]],fl[i[1]]],axis=0)
        t1 = t1[t1[2].isin(feature_list)].sort_values([0,3]).reset_index(drop=1)
        t2 = t1.shift(-1)
        ac = t1[(t1[0] == t2[0]) & (t1['sr'] != t2['sr']) & ((t1[3] <= t2[3]+io) & (t1[3] >= t2[3]-io))]
        
        ax[i[0],i[1]].hist((t2.loc[ac.index,3] - t1.loc[ac.index,3]),bins=100)
        ax[i[0],i[1]].set_xlabel('Gene start offset (bp)')
        #ax[i[0],i[1]].set_ylabel('Shared annotation count')
    
        #end
        t1 = t1.sort_values([0,4]).reset_index(drop=1)
        t2 = t1.shift(-1)
        ac = t1[(t1[0] == t2[0]) & (t1['sr'] != t2['sr']) & ((t1[4] <= t2[4]+io) & (t1[4] >= t2[4]-io))]
        
        ax[i[1],i[0]].hist((t2.loc[ac.index,4] - t1.loc[ac.index,4]),bins=100)
        ax[i[1],i[0]].set_xlabel('Gene end offset (bp)')
        #ax[i[1],i[0]].set_ylabel('Shared annotation count')
    
    for i in range(len(fl)):
        ax[0,i].set_title(ll[i], pad=10)
        ax[i,0].set_ylabel(ll[i], rotation=90, size='large', labelpad=10)

#find common features in pairs
def common_features(ll,fl,feature_list,o):
    t = []
    #pairwise comparisons. loop over combinations of 2 elements.
    for i in list(itertools.combinations([0,1,2,3],2)):
    
        #sort by start
        t1 = pd.concat([fl[i[0]],fl[i[1]]],axis=0)
        t1 = t1[t1[2].isin(feature_list)].sort_values([0,3]).reset_index(drop=1)
        t2 = t1.shift(-1)
        
        #start match on t1 and t2
        ac1 = t1[(t1[0] == t2[0]) & (t1['sr'] != t2['sr']) & ((t1[3] <= t2[3]+o) & (t1[3] >= t2[3]-o))]
        ac2 = t2.loc[ac1.index]
        
        #end match on t1 and t2
        ac3 = t1[(t1[0] == t2[0]) & (t1['sr'] != t2['sr']) & ((t1[4] <= t2[4]+o) & (t1[4] >= t2[4]-o))]
        ac4 = t2.loc[ac3.index]
        
        ##start and end both match for at least one gene model in the other file
        m1 = t1.loc[ac1.index.intersection(ac3.index)]
        m2 = t2.loc[ac2.index.intersection(ac4.index)]

        #relationship is not one to one. gene x from one annotation can match to more than 1 gene in other. 
        mt = pd.concat([m1,m2],axis=0).sort_values([0,3]).reset_index(drop =1)
        n1 = mt[(mt['sr'] == ll[i[0]])]
        n2 = mt[(mt['sr'] == ll[i[1]])]
        
        #one to one  
    
        #one for multiple

        
        t.append((n1,n2))
    return t


#overlap and encapsulation
def overlaps(ll,fl,feature_list,o,xp):
    #grid
    fig,ax = plt.subplots(figsize= (5*len(fl),5*len(fl)), ncols=len(fl),nrows=len(fl), 
                             gridspec_kw={'hspace': 0.25})
    
    tg = []
    cn = 0
    #pairwise comparisons. loop over combinations of 2 elements.
    for j in list(itertools.combinations([0,1,2,3],2)):
        i = 1
        #sort by start
        t1 = pd.concat([fl[j[0]],fl[j[1]]],axis=0)
        t1 = t1[t1[2].isin(feature_list)].sort_values([0,3]).reset_index(drop=1)
        #unique key
        t1['uk'] = t1[0]+'_'+t1[3].astype(str)+'_'+t1[4].astype(str)+'_'+t1[8]
        t2 = t1.shift(-i)

        td= {}
        t =[]
        #how many genes start before the end, for each gene
        while ((t1[0] == t2[0]) & (t2[3]<t1[4])).sum() != 0:
            t2 = t1.shift(-i)
            #end surpassed genes
            for i2 in t1[(t1[0]==t2[0]) & (t2[3]>=t1[4])].index:
                if not (i2 in td.keys()):
                    td[i2] = i
            #not yet end surpassed
            for i2 in t1[(t1[0]==t2[0]) & (t2[3]<t1[4])].index:
                #gene n+1 has x% overlap with gene n
                t.append((t1.loc[i2,'uk'], t1.loc[i2,'sr'], t2.loc[i2,'uk'], t2.loc[i2,'sr'], 
                          (t1.loc[i2,4] - t2.loc[i2,3])/(t2.loc[i2,4] - t2.loc[i2,3])*100))
            i+=1
        tg.append(pd.DataFrame(t))

        #plot
        tmp = pd.DataFrame(t)
        tmp2 = xp[cn]
        #remove matches
        #print(tmp.shape)
        tmp = tmp[~tmp.iloc[:,:4].apply(tuple,1).isin(tmp2.apply(tuple,1))]
        ax[j[0],j[1]].hist(tmp[(tmp[1] == ll[j[0]]) & (tmp[3] == ll[j[1]]) & (tmp[4] > 2)][4].apply(lambda x: 100 if x>100 else x),bins=20) 
        ax[j[0],j[1]].set_xlabel(ll[j[0]]+'\n over \n'+ll[j[1]])
        #print(tmp[(tmp[1] == ll[j[0]]) & (tmp[3] == ll[j[1]]) & (tmp[4] > 2)].shape)
        
        tmp = pd.DataFrame(t)
        tmp2 = tmp2[[2,3,0,1]]
        #print(tmp.shape)
        tmp = tmp[~tmp.iloc[:,:4].apply(tuple,1).isin(tmp2.apply(tuple,1))]
        ax[j[1],j[0]].hist(tmp[(tmp[1] == ll[j[1]]) & (tmp[3] == ll[j[0]]) & (tmp[4] > 2)][4].apply(lambda x: 100 if x>100 else x),bins=20)
        ax[j[1],j[0]].set_xlabel(ll[j[1]]+'\n over \n'+ll[j[0]])
        #print(tmp[(tmp[1] == ll[j[0]]) & (tmp[3] == ll[j[1]]) & (tmp[4] > 2)].shape)
        
        cn+=1
           
    
    #self overlaps
    th = []
    cn=0
    for t1 in fl:
        t1 = t1[t1[2].isin(feature_list)].sort_values([0,3]).reset_index(drop=1)
        #unique key
        t1['uk'] = t1[0]+'_'+t1[3].astype(str)+'_'+t1[4].astype(str)+'_'+t1[8]
        t2 = t1.shift(-i)

        t =[]
        #how many genes start before the end, for each gene
        while ((t1[0] == t2[0]) & (t2[3]<t1[4])).sum() != 0:
            t2 = t1.shift(-i)
            #not yet end surpassed
            for i2 in t1[(t1[0]==t2[0]) & (t2[3]<t1[4])].index:
                #gene n+1 has x% overlap with gene n
                t.append((t1.loc[i2,'uk'], t1.loc[i2,'sr'], t2.loc[i2,'uk'], t2.loc[i2,'sr'], 
                          (t1.loc[i2,4] - t2.loc[i2,3])/(t2.loc[i2,4] - t2.loc[i2,3])*100))
            i+=1
        th.append(pd.DataFrame(t))

        #plot
        tmp = pd.DataFrame(t)
        if len(t) > 0:
            ax[cn,cn].hist(tmp[(tmp[4] > 2)][4].apply(lambda x: 100 if x>100 else x),bins=20)
        ax[cn,cn].set_xlabel(ll[cn]+'\n on \n'+ll[cn])
        cn+=1
    
    #array titles
    for i in range(len(fl)):
        ax[0,i].set_title(ll[i], pad=10)
        ax[i,0].set_ylabel(ll[i], rotation=90, size='large', labelpad=10)
    
    return tg+th

#
def reformat_commons(xp):
    t = []
    for i in xp:
        t1 = i[0]
        t2 = i[1]
        t1['uk'] = t1[0]+'_'+t1[3].astype(int).astype(str)+'_'+t1[4].astype(int).astype(str)+'_'+t1[8]
        t2['uk'] = t2[0]+'_'+t2[3].astype(int).astype(str)+'_'+t2[4].astype(int).astype(str)+'_'+t2[8]
        tmp = pd.concat([t1[['uk','sr']].reset_index(drop=1),t2[['uk','sr']].reset_index(drop=1)],axis=1)
        tmp.columns = range(4)
        t.append(tmp)
    return t


def gmcomp(args):

    l = args.annotation_files
    
    #initial offset to find optimal match offset
    io = args.initial_offset
    #default optimal offset
    o = args.offset
    outdir = args.outdir
    
    fl =[]

    #check file presence
    for i in l:
        if not os.path.isfile(i):
            print("File {0} not found.".format(i))
            sys.exit()
    
    #load files and check file format
    for i in l:
        try:
            tmp = pd.read_csv(i,sep ='\t',encoding='utf-8', header = None,comment='#')
            tmp['sr'] = i.replace(' ','_')
            fl.append(tmp)
        except:
            print("File {0} may not be a tab-separated, utf-8 encoded annotation file with # comment character.".format(i))
            sys.exit()
        
        if (tmp[0].dtype == 'O') and (tmp[2].dtype == 'O') and (tmp[3].dtype == 'int64') and (tmp[4].dtype == 'int64'):
            pass
        else:
            print("Something may be wrong with data fields in columns 1 (Contig ID), 3 (Feature Type), 4 (Feature Start) and 5 (Feature End) \
                  of file {0}.".format(i))
            sys.exit()

    ll = [x.replace(' ','_') for x in l]

    #plot feature offsets for genes and mRNA/transcripts
    #genes
    plot_feature_offsets(ll,fl,['gene'],io)
    plt.savefig(outdir+'/'+'gene_offsets.pdf', format = 'pdf')
    #mRNA
    plot_feature_offsets(ll,fl,['mRNA','transcript'],io)
    plt.savefig(outdir+'/'+'mRNA_offsets.pdf', format = 'pdf')
    

    #grid for common features
    fig,ax = plt.subplots(figsize= (14,7), ncols=2,nrows=1)

    #export common features
    x = common_features(ll,fl,['gene'],o)
    xp = reformat_commons(x)
    #shared between any n
    tdf = pd.DataFrame()
    for i in range(len(fl)-1):
        tdf = pd.concat([tdf,x[i][0].drop_duplicates()],axis=0).reset_index(drop=1)
    tdf = tdf.groupby(tdf.columns.tolist(),as_index=False).size().sort_values('size')
    tdf['size'] = tdf['size']+1
    tdf.to_csv(outdir+'/'+'genes_shared.tsv',index = False, sep = '\t', header=None)

    #plot genes
    ax[0].set_title('Genes',size=10)
    ax[0].hist(tdf['size'], bins=len(fl)-1, range=(2,len(fl)+1), rwidth=0.9)
    ax[0].set_xticks([x+1.5 for x in range(1,len(fl))], labels = [x+1 for x in range(1,len(fl))])
    ax[0].set_xlabel('Shared across annotations')
    ax[0].set_ylabel('Count')

    #export common features
    x = common_features(ll,fl,['mRNA','transcript'],o)
    xp2 = reformat_commons(x)
    #shared between any n
    tdf = pd.DataFrame()
    for i in range(len(fl)-1):
        tdf = pd.concat([tdf,x[i][0].drop_duplicates()],axis=0).reset_index(drop=1)
    tdf = tdf.groupby(tdf.columns.tolist(),as_index=False).size().sort_values('size')
    tdf['size'] = tdf['size']+1
    tdf.to_csv(outdir+'/'+'mRNA_shared.tsv',index = False, sep = '\t', header=None)

    #plot mRNA
    ax[1].set_title('mRNA/transcript',size=10)
    ax[1].hist(tdf['size'], bins=len(fl)-1, range=(2,len(fl)+1), rwidth=0.9)
    ax[1].set_xticks([x+1.5 for x in range(1,len(fl))], labels = [x+1 for x in range(1,len(fl))])
    ax[1].set_xlabel('Shared across annotations')
    ax[1].set_ylabel('Count')

    plt.savefig(outdir+'/'+'common_feature_counts.pdf', format = 'pdf')

    #plot overlaps
    x = overlaps(ll,fl,['gene'],o,xp)
    plt.savefig(outdir+'/'+'gene_overlaps.pdf', format = 'pdf')

    x = overlaps(ll,fl,['mRNA','transcript'],o,xp2)
    plt.savefig(outdir+'/'+'mRNA_overlaps.pdf', format = 'pdf')



def main():
    parser = argparse.ArgumentParser(prog='gmcomp', 
                                     usage='%(prog)s [options] annotation_file1 annotation_file2 annotation_file3 ...', 
                                     description="For comparing gene models across different annotations of the same genome.")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version='__version__'))
    
    parser.add_argument('annotation_files',  help = 'gff/gtf annotation file', nargs='*')

    parser.add_argument("-i", "--initial_offset", type=int, help="Initial positional match offset for feature", metavar="",
                        default = 5000)
  
    parser.add_argument("-f", "--offset", type=int, help="Positional offset for feature match", metavar="",
                        default = 1000)
    
    parser.add_argument("-o",'--outdir', type=str, help="Output directory", metavar='', default=os.getcwd())

    # parser.add_argument("-l",'--lineage', type=str, help="BUSCO lineage", metavar='lineage', required=True)
    # parser.add_argument("-t",'--threads', type=int, help="Compleasm threads", metavar='threads', default=4)
    # parser.add_argument("-r",'--reference', type=str, help="Reference assembly", metavar='reference')
    # parser.add_argument("-m",'--rcompdir', type=str, help="Reference compleasm output directory", metavar='rcompleasm_directory')
    # parser.add_argument("-n",'--nullify', action='store_true', help="Remove all BUSCO genes in assembly")
    # parser.add_argument("-s",'--syndis', action='store_true', help="Compute syntenic distance from reference")
    # parser.add_argument("-i","--ignore_orientation", action='store_true', 
    #                     help="Ignores orientation and only considers gene order for syntenic distances.")
    # parser.add_argument("-d","--include_duplications", action='store_true', 
    #                     help="Duplicated gene pairs are considered distinct for syntenic distances.")
    # parser.add_argument("-w","--include_singleton_contigs", action='store_true', 
    #                     help="Includes contigs with single genes for syntenic distances.")
    

    parser.set_defaults(func=gmcomp)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()