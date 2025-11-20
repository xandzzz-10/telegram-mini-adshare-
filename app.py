from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import tempfile
import os
from starlette.requests import Request
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Ad Share MiniApp")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_payments_bytes(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes), header=None)

    header_row = None
    for i in range(min(10, len(df))):
        row = df.iloc[i].astype(str).str.lower().tolist()
        if any('sku' in c for c in row) or any('артикул' in c for c in row):
            header_row = i
            break

    if header_row is None:
        payments = pd.read_excel(io.BytesIO(file_bytes), header=0)
    else:
        payments = pd.read_excel(io.BytesIO(file_bytes), header=header_row)
        payments = payments.loc[~payments.apply(lambda r: all(r == payments.columns), axis=1)].reset_index(drop=True)

    payments.columns = [str(c).strip() for c in payments.columns]

    col_sku = None
    col_art = None
    col_clicks = None
    col_order = None

    for c in payments.columns:
        lc = str(c).lower()
        if "sku" in lc and col_sku is None:
            col_sku = c
        if "артикул" in lc and col_art is None:
            col_art = c
        if "клики" in lc and col_clicks is None:
            col_clicks = c
        if "заказ" in lc and col_order is None:
            col_order = c

    payments[col_clicks] = pd.to_numeric(payments[col_clicks], errors="coerce").fillna(0)
    payments[col_order] = pd.to_numeric(payments[col_order], errors="coerce").fillna(0)

    payments["total_ad_spend"] = payments[col_clicks] + payments[col_order]

    if col_art is not None:
        payments = payments.rename(columns={col_art: "Артикул"})
    else:
        if col_sku:
            payments = payments.rename(columns={col_sku: "Артикул"})

    return payments[["Артикул", "total_ad_spend"]]


def compute_ad_share(main_bytes: bytes, payments_bytes: bytes) -> pd.DataFrame:
    main = pd.read_excel(io.BytesIO(main_bytes))

    if "Артикул" not in main.columns or "Заказано на сумму" not in main.columns:
        raise ValueError("В основном файле должны быть столбцы 'Артикул' и 'Заказано на сумму'")

    payments_spend = load_payments_bytes(payments_bytes)
    ad_spend = payments_spend.groupby("Артикул", as_index=False)["total_ad_spend"].sum()

    merged = main.merge(ad_spend, on="Артикул", how="left")
    merged["total_ad_spend"] = merged["total_ad_spend"].fillna(0)
    merged["Заказано на сумму"] = pd.to_numeric(merged["Заказано на сумму"], errors="coerce")

    def calc_share(row):
        denom = row["Заказано на сумму"]
        if pd.isna(denom) or denom == 0:
            return pd.NA
        return row["total_ad_spend"] / denom

    merged["Доля рекламных расходов"] = merged.apply(calc_share, axis=1)
    return merged


# ===========================
#           ROUTES
# ===========================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process")
async def process_files(main_file: UploadFile = File(...), payments_file: UploadFile = File(...)):
    try:
        main_bytes = await main_file.read()
        payments_bytes = await payments_file.read()

        result_df = compute_ad_share(main_bytes, payments_bytes)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        result_df.to_excel(tmp.name, index=False)
        tmp.close()

        return FileResponse(
            tmp.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="result.xlsx"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
