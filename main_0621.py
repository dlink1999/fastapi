from fastapi import FastAPI, Query, File, UploadFile, Request 
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, ORJSONResponse, UJSONResponse, JSONResponse
from typing import List, Union
#from deta import Drive
from deta import Deta 
from pydantic import BaseModel
from io import StringIO
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

#import HTML
import pandas as pd
import csv
import json
#from io import StringIO

templates = Jinja2Templates(directory="templates")

app = FastAPI()  # notice that the app instance is called `app`, this is very important.

origins = [
    "http://tcm.aikampo.com",
    "https://tcm.aikampo.com",
    "http://localhost/",
    "http://localhost:8080",
    "http://localhost:60552",
    "http://localhost/*",
    "https://localhost/*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/file/")   #to save file to static, but it could be pasted into directly now.
async def main2():
    return FileResponse('static/test_file.csv')

class Item(BaseModel):
    name: str
    description: str

pattern_list = [
    {"name": "心火亢盛證", "description": "口舌生瘡,心中煩熱,急躁失眠,口渴,欲冷飲,小便赤澀","solution" : "治宜滋陰降火", "herb" : "知柏地黃丸(《醫考方》)合交泰丸(《韓氏醫通》)"}
#    {"證型": "心火亢盛證", "症狀": "口舌生瘡,心中煩熱,急躁失眠,口渴,欲冷飲,小便赤澀","治法" : "治宜滋陰降火", "方劑" : "知柏地黃丸(《醫考方》)合交泰丸(《韓氏醫通》)"}
]

dfa = pd.read_csv("static/AII_sample.csv") # sample 表目前是 50 組的 sample, 注意是原始, 或是已加 sym_cnt
dfall=dfa.fillna(0)  #因為後面用 df
#dfall = pd.read_csv("static/database_all2.csv")

dfm = pd.read_csv('static/sym_matrix.csv')
dfm1 = dfm.fillna(0)
dfm2 = pd.read_csv('static/sym.csv')

#listofTitle 視需求而變, 此處列出 complete sample 
#listOfTitle = ["name", "sym_all" ,"tongue", "pulse", "solution" , "herb_all", "note" ]  #選出要顯示的欄位


@app.get("/pattern3/{ptn_name}" , response_class=JSONResponse)
async def read_item(request: Request, ptn_name: str):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    #listOfTitle = ["證型", "病症" , "治法" , "方劑"]
    dfall2 = dfall.query('name == @ptn_name')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()

    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="table")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  

    return json.JSONDecoder().decode(json_object)

@app.get("/pattern5/{ptn_name}" , response_class=JSONResponse)
async def read_item(request: Request, ptn_name: str):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    #listOfTitle = ["證型", "病症" , "治法" , "方劑"]
    dfall2 = dfall.query('name == @ptn_name')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()

    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="index")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  

    return json.JSONDecoder().decode(json_object)
    
@app.get("/disease1/" , response_class=JSONResponse)
async def read_items(dslist: List[str] = Query(default=["COVID19"])):
    #listOfTitle = ["name", "sym_all" ,"tongue", "pulse", "solution" , "herb_all", "note" ]  #選出要顯示的欄位
    listOfTitle = ["name", "description" , "solution" , "herb"]

    #dslist = ["心悸","COVID19","COVID20","頭暈","口苦","眩暈","氣短","咳嗽"]  #測試用, 程式中用輸入的字串
    dft=pd.DataFrame(dslist)
    dft.columns = ['Sym']  #標示 Columns 名稱, 才能做聯集

    #result = dfm2.merge(dft, how='outer', indicator=True)
    result0 = dft.merge(dfm2, how='inner') # 先做交集, 再做聯集, 以免有不 match
    result = dfm2.merge(result0, how='outer', indicator=True) #做聯集, 產出是 both left right  
    result['Value']=result['_merge'].apply(lambda x: 1 if x=="both" else 0)
    result2=result.drop(['_merge'],axis=1)

    dfr2=dfm1.dot(result2.set_index('Sym'))
    dfall['match_cnt']=dfr2
    dfall['match_ratio']=dfall['match_cnt']/dfall['sym_cnt']

    listOfTitle1 = ["name", "description" , "solution" , "herb" ]  #選出要顯示的欄位

    # disease1 is based on ratio
    dfall.sort_values(by=['match_ratio'], inplace=True, ascending=False)
    dfall_out1=dfall[listOfTitle1].head(5)
    result = dfall_out1.to_json(orient="table")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  
    
    return json.JSONDecoder().decode(json_object)


@app.get("/disease1h/" , response_class=HTMLResponse)
async def read_items(dslist: List[str] = Query(default=["COVID19"]), limit : int = 5):
    listOfTitle2 = ["name", "sym_all" ,"tongue", "pulse", "solution" , "herb_all", "note" ]  #選出要顯示的欄位
    #listOfTitle = ["name", "description" , "solution" , "herb"]

    dslist = ["心悸","COVID19","COVID20","頭暈","口苦","眩暈","氣短","咳嗽"]  #測試用, 程式中用輸入的字串
    dft=pd.DataFrame(dslist)
    dft.columns = ['Sym']  #標示 Columns 名稱, 才能做聯集

    #result = dfm2.merge(dft, how='outer', indicator=True)
    result0 = dft.merge(dfm2, how='inner') # 先做交集, 再做聯集, 以免有不 match
    result = dfm2.merge(result0, how='outer', indicator=True) #做聯集, 產出是 both left right  
    result['Value']=result['_merge'].apply(lambda x: 1 if x=="both" else 0)
    result2=result.drop(['_merge'],axis=1)

    dfr2=dfm1.dot(result2.set_index('Sym'))
    dfall['match_cnt']=dfr2
    dfall['match_ratio']=dfall['match_cnt']/dfall['sym_cnt']

    #listOfTitle1 = ["name", "description" , "solution" , "herb" ]  #選出要顯示的欄位

    dfall.sort_values(by=['match_ratio'], inplace=True, ascending=False)
    dfall_out1=dfall[listOfTitle2].head(limit)
    dfall_out1_html=dfall_out1.to_html()
    #result = dfall_out1.to_json(orient="table")
    #parsed = json.loads(result)
    #json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  
    
    return dfall_out1_html

@app.get("/disease11/" , response_class=JSONResponse)
async def read_items(dslist: List[str] = Query(default=["心悸","面色蒼白"])):
    #listOfTitle = ["name", "sym_all" ,"tongue", "pulse", "solution" , "herb_all", "note" ]  #選出要顯示的欄位
    listOfTitle1 = ["name", "description" , "solution" , "herb"]

    #dslist = ["心悸","COVID19","COVID20","頭暈","口苦","眩暈","氣短","咳嗽"]  #測試用, 程式中用輸入的字串
    dft=pd.DataFrame(dslist)
    dft.columns = ['Sym']  #標示 Columns 名稱, 才能做聯集

    #result = dfm2.merge(dft, how='outer', indicator=True)
    result0 = dft.merge(dfm2, how='inner') # 先做交集, 再做聯集, 以免有不 match
    result = dfm2.merge(result0, how='outer', indicator=True) #做聯集, 產出是 both left right  
    result['Value']=result['_merge'].apply(lambda x: 1 if x=="both" else 0)
    result2=result.drop(['_merge'],axis=1)

    dfr2=dfm1.dot(result2.set_index('Sym'))
    dfall['match_cnt']=dfr2
    dfall['match_ratio']=dfall['match_cnt']/dfall['sym_cnt']

    listOfTitle1 = ["name", "description" , "solution" , "herb" ]  #選出要顯示的欄位

    dfall.sort_values(by=['match_ratio'], inplace=True, ascending=False)
    dfall_out1=dfall[listOfTitle1].head(5)
    result = dfall_out1.to_json(orient="table")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  
    
    return json.JSONDecoder().decode(json_object)


@app.get("/disease2/" , response_class=JSONResponse)
async def read_items(dslist: List[str] = Query(default=["COVID19"])):
    #listOfTitle = ["name", "sym_all" ,"tongue", "pulse", "solution" , "herb_all", "note" ]  #選出要顯示的欄位
    listOfTitle = ["name", "description" , "solution" , "herb"]

    #dslist = ["心悸","COVID19","COVID20","頭暈","口苦","眩暈","氣短","咳嗽"]  #測試用, 程式中用輸入的字串
    dft=pd.DataFrame(dslist)
    dft.columns = ['Sym']  #標示 Columns 名稱, 才能做聯集

    #result = dfm2.merge(dft, how='outer', indicator=True)
    result0 = dft.merge(dfm2, how='inner') # 先做交集, 再做聯集, 以免有不 match
    result = dfm2.merge(result0, how='outer', indicator=True) #做聯集, 產出是 both left right  
    result['Value']=result['_merge'].apply(lambda x: 1 if x=="both" else 0)
    result2=result.drop(['_merge'],axis=1)

    dfr2=dfm1.dot(result2.set_index('Sym'))
    dfall['match_cnt']=dfr2
    dfall['match_ratio']=dfall['match_cnt']/dfall['sym_cnt']

    listOfTitle1 = ["name", "description" , "solution" , "herb" ]  #選出要顯示的欄位

    dfall.sort_values(by=['match_cnt'], inplace=True, ascending=False)
    dfall_out1=dfall[listOfTitle1].head(5)
    result = dfall_out1.to_json(orient="table")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  
    
    return json.JSONDecoder().decode(json_object)


@app.get("/pattern99/{ptn_name}" , response_class=JSONResponse)
async def read_item(request: Request, ptn_name: str):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    #listOfTitle = ["證型", "病症" , "治法" , "方劑"]
    dfall2 = dfall.query('name == @ptn_name')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    dfall3_list = dfall2_list[0]
    zipbObj = zip(listOfTitle, dfall3_list)
    dictOfWords = dict(zipbObj)


    jsonString = json.dumps(dfall2_list[0], ensure_ascii=False)
    jsonString1 = json.dumps(jsonString[0], ensure_ascii=False)
    #return dfall2
    #return dfall3_list
    return dictOfWords
    #return json.JSONDecoder().decode(json_object)
    #return jsonString

@app.get("/pattern/{ptn_name}" , response_class=JSONResponse)
async def read_item(request: Request, ptn_name: str):
    listOfTitle1 = ["name", "description" , "solution" , "herb"]
    #listOfTitle = ["證型", "病症" , "治法" , "方劑"]
    dfall2 = dfall.query('name == @ptn_name')    
    dfall_out=dfall2[listOfTitle1]
    dfall2v = dfall_out.values  #becomes array

    dfall2_list = dfall2v.tolist()
    dfall3_list = dfall2_list[0]
    zipbObj = zip(listOfTitle1, dfall3_list)
    dictOfWords = dict(zipbObj)
#    dictOfWords = dict(dfall3_list)
    
    #dfall2_dict = dfall_out.to_dict('records')

    #result = dfall_out.to_json(orient="index")
    #parsed = json.loads(result)
    #json_object = json.dumps(str, indent=4,ensure_ascii=False)  

    #return json.JSONDecoder().decode(json_object)
    return dictOfWords
