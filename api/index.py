import io
import time
import os
import psutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import polars as pl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", "development")
    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title="Polars High-Speed Data Engine API")

@app.post("/api/v1/analyze")
async def analyze_excel(file: UploadFile = File(...)):
    start_time = time.perf_counter()
    process = psutil.Process(os.getpid())
    
    try:
        contents = await file.read()
        # Calamine reader for blazing fast Excel ingestion
        df = pl.read_excel(io.BytesIO(contents), engine="calamine")
        
        # Calculate structural metrics
        num_rows, num_cols = df.shape
        columns = df.columns
        schema_types = {col: str(dtype) for col, dtype in zip(columns, df.dtypes)}
        
        # Performance Tracking
        execution_time = time.perf_counter() - start_time
        mem_info = process.memory_info()
        
        return {
            "status": "success",
            "meta": {
                "rows": num_rows,
                "columns_count": num_cols,
                "schema": schema_types,
                "diagnostics": {
                    "execution_time_seconds": execution_time,
                    "memory_rss_mb": mem_info.rss / (1024 * 1024),
                    "cpu_percent": process.cpu_percent(interval=None)
                }
            },
            "data": df.head(100).to_dicts()  # Return safe preview slice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing failed: {str(e)}")

@app.post("/api/v1/export")
async def export_excel():
    # Example generator endpoint: generates a clean Polars export in-memory
    df = pl.DataFrame({"Target_Metric": [10, 20, 30], "Prediction_Value": [10.5, 20.1, 29.8]})
    
    buffer = io.BytesIO()
    df.write_excel(buffer)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=exported_analysis.xlsx"}
    )