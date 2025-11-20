from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates"), name="static")


@app.get("/")
def home():
    return HTMLResponse(open("templates/index.html", "r", encoding="utf-8").read())


@app.get("/webapp")
def webapp():
    return HTMLResponse(open("templates/index.html", "r", encoding="utf-8").read())


@app.post("/process")
async def process(main_file: UploadFile, payments_file: UploadFile):
    df_main = pd.read_excel(main_file.file)
    df_payments = pd.read_excel(payments_file.file)

    df_result = df_main.copy()
    df_result["Расходы"] = df_payments["Расходы"]
    df_result["Итог"] = df_result["Доход"] - df_result["Расходы"]

    output_path = "result.xlsx"
    df_result.to_excel(output_path, index=False)

    return FileResponse(output_path, filename="result.xlsx", media_type="application/vnd.ms-excel")
