import re
import pandas as pd
import datetime
import time
import csv
import os

# This is for Bitcoin talk forum comments cleaning
# 1 Customized variables here
#sourceBTFFileNames=["1283183.0.csv","1954159.0.csv","2170941.0.csv","3020156.0.csv","5165342.0.csv"]
sourceBTFFileNames=["2021reviews.csv"]
#souceeBTFFileNames2=["reddit-part1of3.csv","reddit-part2of3.csv","reddit-part3of3.csv"]
souceeBTFFileNames2=["reddit_post_texts-part4.csv"]
sourceFilePath="./data/"
commentsFileName="_comments.csv"
topicFileName="_topic.csv"
mixComments="2021mixedComments.csv"  # just day and comments ordered descend
gatheredHeader="headers.csv"  #gathered by header
commentsCols0=["comments","time","day","header","reviewer","r_level","r_activity","r_merit"]
commentsCols1=["day","comments","header"]
topicCols=["header","publisher","reads","replies","p_activity","p_merit","time","day"]
checkCols=["day"]
checkColFormat=[r'[0-3]?[0-9]\/[01]?[0-9]\/20(([1][7-9])|(20))']
btcPrice="BTC_price_140917_210126.csv"
pricePeriod="period_price_comment.csv"

# Get date and time from time text 0 for date, 1 for time
def getTime(ttext,ind=0):
    if ttext:
        try:
            t = time.strptime(ttext, "%B %d, %Y, %X %p")
        except:
            ttext = "July 30, 2000, 03:29:55 AM"
            t = time.strptime(ttext, "%B %d, %Y, %X %p")
        if ind==0: return time.strftime("%d/%m/%Y",t)
        elif ind==1: return time.strftime("%H:%M:%S",t)
    else: return "Time not found"


# Get membership information 0_Member level: r'\b.*?(?= )' 1_Activity: r'(?<=Activity: )\d*?(?= )' 2_Merit: r'(?<=Merit: )\d*?(?= )'
def getMembership(ttext,reg=r'\b.*?(?= )'):
    if ttext:
        t=re.search(reg,ttext)
        if t:
            t = t.group()
            return t
        else: return "not found"
    else: return "not found"

def store2CSV(path, data):
    if os.path.isfile(path):
        with open(path, mode="a+", encoding="utf-8", newline="") as f:
            fcsv = csv.writer(f)
            for r in data:
                fcsv.writerow(r)
    else:
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            fcsv = csv.writer(f)
            for r in data:
                fcsv.writerow(r)

def makeComments0(filename):
    commentsdf=pd.read_csv(sourceFilePath+filename,header=None)
    commentsdf["time"]=commentsdf.loc[:,8].apply(lambda x:getTime(x,1))
    commentsdf["day"]=commentsdf.loc[:,8].apply(lambda x:getTime(x,0))
    commentsdf["comments"]=commentsdf.loc[:,7].apply(lambda x:x if x else "Neutral")
    commentsdf["header"]=commentsdf.loc[:,1].apply(lambda x:x if x else "Neutral")
    commentsdf["reviewer"]=commentsdf.loc[:,5].apply(lambda x:x if x else "Neutral")
    commentsdf["r_level"] = commentsdf.loc[:, 6].apply(lambda x: getMembership(x, r'\b.*?(?= )'))
    commentsdf["r_activity"] = commentsdf.loc[:, 6].apply(lambda x:getMembership(x,r'(?<=Activity: )\d*?(?= )'))
    commentsdf["r_merit"] = commentsdf.loc[:, 6].apply(lambda x:getMembership(x,r'(?<=Merit: )\d*?(?= )'))
    return commentsdf[commentsCols0]

def makeComments1(filename):
    commentsdf=pd.read_csv(sourceFilePath+filename,header=0)
    commentsdf["comments"]=commentsdf["update_text"]
    commentsdf["day"]=commentsdf["date"]
    header=commentsdf.iloc[0,4]
    for ind,r in commentsdf.iterrows():
        if r["header"]==1:
            header=r["comments"]
        r["header"]=header
    return commentsdf[commentsCols1]

def makeTopic(filename):
    ll=[]
    fcsv=csv.reader(open(sourceFilePath+filename,'r',encoding='utf-8'))
    rcount=""
    for r in fcsv:
        sl = []
        if r[2]==r[5] and r[4]!=rcount:
            rcount=r[4]
            sl.append(r[1])
            sl.append(r[2])
            sl.append(r[3])
            sl.append(r[4])
            sl.append(getMembership(r[6], r'\b.*?(?= )'))
            sl.append(getMembership(r[6], r'(?<=Activity: )\d*?(?= )'))
            sl.append(getMembership(r[6], r'(?<=Merit: )\d*?(?= )'))
            sl.append(getTime(r[8], 1))
            sl.append(getTime(r[8], 0))
            ll.append(sl)
    return ll

def makeMixed(df1,df_add,cols):
    df1=pd.concat([df1,df_add],axis=0,ignore_index=True,join="outer")
    return df1[cols]

def checkforamt(text,pattern): # r'[1-3]?[0-9]\/1?[0-9]\/20(([1][7-9])|(20))'
    if re.search(pattern,text): return True
    else: return False

def checkDf_format(df,cols,pattern):
    for c, p in zip(cols,pattern):
        df[c+"_ck"]=df[c].apply(lambda x:checkforamt(str(x),p))
    for c in cols:
        df=df[df[c+"_ck"]==True]
    return df[commentsCols1]

def makingAllcomments():
    out=pd.DataFrame()
    for f in sourceBTFFileNames:
        df=makeComments0(f)
        out=makeMixed(out,df,commentsCols1)
    for f in souceeBTFFileNames2:
        df=makeComments1(f)
        out=makeMixed(out,df,commentsCols1)
    out = out.dropna()
    out = checkDf_format(out,checkCols,checkColFormat)
    out=out.sort_values(by=["day","header"],ascending=False)
    out=out.reset_index(drop=True)
    out.to_csv(sourceFilePath + mixComments, header=commentsCols1)
    return out

def getPeriodopen(df: pd.DataFrame, type: int = 0):
    df.sort_index()
    if type == 0:
        return df.iloc[0,:]["Adj Close"]
    else:
        return df.iloc[-1,:]["Adj Close"]

def gatherByrow(df: pd.DataFrame, c: str):
    out = ""
    for d in df[c]:
        out = out + d + " "
    return out[:-1]


def tuple2str(tup: tuple):
    text = ""
    for t in tup:
        text = text + str(t) + "/"
    return text[:-1]

def gathercommentBytime(mixdf:pd.DataFrame,type:int=2): # 0 by day, 1 by week, 2 by month, 3 by quarter
    mixdf.set_index(pd.to_datetime(mixdf["day"]),inplace=True)
    out=pd.DataFrame(columns=["mark","comment"])
    ind=0
    if type==0:
        mixdf_g = mixdf.groupby([mixdf.index.year, mixdf.index.month, mixdf.index.day,mixdf["header"]], axis=0)
        for n in mixdf_g:
            out.loc[ind] = {"mark": tuple2str(n[0]), "comment": gatherByrow(mixdf_g.get_group(n[0]), "comments")}
            ind += 1
    elif type==1:
        mixdf_g = mixdf.groupby([mixdf.index.year, mixdf.index.month, mixdf.index.week], axis=0)
    elif type==2:
        mixdf_g = mixdf.groupby([mixdf.index.year, mixdf.index.month], axis=0)
        for n in mixdf_g:
            out.loc[ind] = {"mark": tuple2str(n[0]), "comment": gatherByrow(mixdf_g.get_group(n[0]), "comment")}
            ind += 1
    elif type == 2:
        mixdf_g = mixdf.groupby([mixdf.index.year, mixdf.index.quarter], axis=0)
    out.to_csv(sourceFilePath + gatheredHeader)
    return out


# def gathercommentByheader(mixdf:pd.DataFrame):
#     mixdf.set_index(pd.to_datetime(mixdf["day"]),inplace=True)
#     out=pd.DataFrame(columns=["period","comment","header"])
#     mixdf_g = mixdf.groupby([mixdf.index.year, mixdf.index.month, mixdf.index.day,mixdf["header"]], axis=0)
#     ind=0
#     for n in mixdf_g:
#         out.loc[ind] = {"header": tuple2str(n[0]), "comment": gatherByrow(mixdf_g.get_group(n[0])),"header":}
#         ind += 1


def getPrice(type:int=2):
    pricedf=pd.read_csv(sourceFilePath+btcPrice,header=0)
    pricedf.set_index(pd.to_datetime(pricedf["Date"]),inplace=True)
    if type==2:
        pricedf_g = pricedf.groupby([pricedf.index.year, pricedf.index.month], axis=0)
    out=pd.DataFrame(columns=["period","open","close"])
    ind=0
    for n in pricedf_g:
        out.loc[ind]={"period":tuple2str(n[0]), "open" : getPeriodopen(pricedf_g.get_group(n[0]),0),"close":getPeriodopen(pricedf_g.get_group(n[0]),1)}
        ind+=1
    return out

def CreateFile():
    if os.path.exists(sourceFilePath+mixComments):
        mixdf=pd.read_csv(sourceFilePath+mixComments,header=0)
    else:
        mixdf=makingAllcomments()
    if os.path.exists(sourceFilePath+gatheredHeader):
        gathered=pd.read_csv(sourceFilePath+mixComments,header=0)
    else:
        gathered=gathercommentBytime(mixdf,0)

def SplitbyMonth():
    cols=["date","comment","header"]
    df=pd.read_csv(sourceFilePath+mixComments,header=0)
    df.columns=["id","date","comment","header"]
    df.set_index(pd.to_datetime(df["date"]),inplace=True)
    df_group_Y=df.groupby(df.index.year,axis=0)
    for d in df_group_Y:
        tname=str(d[0])
        d[1].to_csv(sourceFilePath+tname+"_comments.csv",index=None)
        print("The year of {0} is stored!".format(tname))


if __name__=="__main__":
    CreateFile()
    # SplitbyMonth()
    # price=getPrice()
    # gathered2=pd.merge(gathered,price,on="period",how="inner")
    # gathered2["fluct"]=gathered2["close"]-gathered2["open"]
    # gathered2["fluct"]=gathered2["fluct"].shift(1)
    # gathered2.to_csv(sourceFilePath+pricePeriod)



