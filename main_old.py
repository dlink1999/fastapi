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
from starlette.requests import Request


#import HTML
import pandas as pd
import csv
import json
#import requests
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
#drive = Drive("myfiles")
#df = pd.read_csv(data)

#some_file_path = "123.txt"


ironman_list = ["中信兄弟", "統一獅", "lamigo", "富邦悍將"]


#len_1 = 0
#df = pd.read_csv("AII_sample01.csv")
#len_1 = len(list(df['sym_all']))

#result = drive.list()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/")
async def read_items(q: Union[List[str], None] = Query(default=None)):
    query_items = {"q": q}
    return query_items


@app.get("/item2/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id ** 2}


@app.get("/file1/")
async def main1():
    return FileResponse('static/123.txt')


@app.get("/file2/")
async def main2():
    return FileResponse('static/sym2.csv')


@app.get("/file3/")
async def main3():
    return {dfm.shape}


class Item(BaseModel):
    name: str
    description: str


pattern_list = [
    {"name": "心火亢盛證", "description": "口舌生瘡,心中煩熱,急躁失眠,口渴,欲冷飲,小便赤澀","solution" : "治宜滋陰降火", "herb" : "知柏地黃丸(《醫考方》)合交泰丸(《韓氏醫通》)"}
#    {"證型": "心火亢盛證", "症狀": "口舌生瘡,心中煩熱,急躁失眠,口渴,欲冷飲,小便赤澀","治法" : "治宜滋陰降火", "方劑" : "知柏地黃丸(《醫考方》)合交泰丸(《韓氏醫通》)"}
]


app.get("/pattern5/{ptn_name}", response_model=List[Item])
async def read_item(ptn_name):
    return pattern_list




dfall = pd.read_csv("static/database_all2.csv")
dfm = pd.read_csv('static/sym_matrix.csv')
dfm1 = dfm.fillna(0)
dfm2 = pd.read_csv('static/sym2.csv')
list_t = ["SYMP02", "SYMP05", "SYMP07", "SYMP08", "SYMP09"]
dft=pd.DataFrame(list_t)

dft.columns = ['Sym']
result = dfm2.merge(dft, how='outer', indicator=True)
result['Value']=result['_merge'].apply(lambda x: 1 if x=="both" else 0)
result2=result.drop(['_merge'],axis=1)
dfr2=dfm1.dot(result2.set_index('Sym'))


df_html = dfm1.to_html()
df1_html = dfm1.to_html()

df2_html = dfr2.to_html()

@app.get("/pattern2/{ptn_name}")
async def read_item(request: Request, ptn_name: str):
    dfall2 = dfall.query('name == @ptn_name')
    dfall2_html = dfall2.to_html()
    return templates.TemplateResponse("item.html", {"request": request, "id": dfall2_html})

@app.get("/pattern/{ptn_name}" , response_class=JSONResponse)
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


@app.get("/pattern3/{ptn_name}" , response_class=JSONResponse)
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

@app.get("/disease1A/" , response_class=JSONResponse)
async def read_items(dslist: Union[List[str], None] = Query(default=None)):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    filter_list=["心火亢盛證","心氣虛證","心血氣虛兩證","心氣陰兩虛證","心陰虛證"]
    dfall2 = dfall.query('name.isin(@filter_list)')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    #dfall3_list = dfall2_list[0]
    zipbObj = zip(listOfTitle, dfall2_list)
    dictOfWords = dict(zipbObj)
    json_object = json.dumps(dictOfWords, indent = 4 ,ensure_ascii=False)
    return json.JSONDecoder().decode(json_object)
    
@app.get("/disease1/" , response_class=JSONResponse)
async def read_items(dslist: Union[List[str], None] = Query(default=None)):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    filter_list=["心火亢盛證","心氣虛證","心血氣虛兩證","心氣陰兩虛證","心陰虛證"]
    dfall2 = dfall.query('name.isin(@filter_list)')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    
    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="records")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  

    return json.JSONDecoder().decode(json_object)

@app.get("/disease3/" , response_class=JSONResponse)
async def read_items(ds: Union[List[str], None] = Query(default=None)):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    filter_list=["心火亢盛證","心氣虛證","心血氣虛兩證","心氣陰兩虛證","心陰虛證"]
    dfall2 = dfall.query('name.isin(@filter_list)')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    
    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="records")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  

    return {"ds" : ds}
#    return json.JSONDecoder().decode(json_object)

@app.get("/disease2/" , response_class=JSONResponse)
async def read_items(dslist: Union[List[str], None] = Query(default=None)):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    filter_list=["心火亢盛證","心陽暴脫證","肝血虛證","心氣陰兩虛證","痰火擾心證"]
    dfall2 = dfall.query('name.isin(@filter_list)')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    #dfall3_list = dfall2_list[0]
    #zipbObj = zip(listOfTitle, dfall2_list)
    #dictOfWords = dict(zipbObj)
    #json_object = json.dumps(dictOfWords, indent = 4 ,ensure_ascii=False)
    #result = zipbObj.to_json(orient="records")
    
    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="records")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  

    #result = dfall2_list.to_json(orient="records")
    #parsed = json.loads(result)
    #json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  
    
    return json.JSONDecoder().decode(json_object)


@app.get("/pattern5/{ptn_name}" , response_class=JSONResponse)
async def read_item(request: Request, ptn_name: str):
    listOfTitle = ["name", "description" , "solution" , "herb"]
    #listOfTitle = ["證型", "病症" , "治法" , "方劑"]
    dfall2 = dfall.query('name == @ptn_name')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
#    dfall3_list = dfall2_list[0]
#    zipbObj = zip(listOfTitle, dfall3_list)
#    dictOfWords = dict(zipbObj)
#    json_object = json.dumps(dictOfWords, indent = 4, ensure_ascii=False)

    df3 = pd.DataFrame(dfall2_list, columns = listOfTitle)
    result = df3.to_json(orient="table")
    parsed = json.loads(result)
    json_object = json.dumps(parsed, indent=4,ensure_ascii=False)  



    #jsonString = json.dumps(dfall2_list, ensure_ascii=False)
    #return dfall2
    #return dfall3_list
    #return dictOfWords
    #return json.JSONDecoder().decode(json_object),json.JSONDecoder().decode(json_object)
    return json.JSONDecoder().decode(json_object)
    #return json_object

@app.get("/pattern4/{ptn_name}")
async def read_item(request: Request, ptn_name: str):
    dfall2 = dfall.query('name == @ptn_name')
    dfall2v = dfall2.values
    dfall2_list = dfall2v.tolist()
    return dfall2_list


@app.get("/file4/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("df.html", {"request": request, "html": df_html})

@app.get("/item6/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

@app.get("/item7/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": df_html})

@app.get("/item8/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": df2_html})
