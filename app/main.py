
# uvicorn app.main:app --reload --port 8000

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os

from app.models import Record
from app.database import DatabaseManager

# Инициализация
app = FastAPI(title="Модуль интеграции с БД")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Создание экземпляра БД
db_manager = DatabaseManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница — список записей"""
    records = db_manager.get_all_records()
    return templates.TemplateResponse("records.html", {
        "request": request,
        "records": records,
        "total": len(records)
    })

@app.get("/add", response_class=HTMLResponse)
async def show_add_form(request: Request):
    """Форма добавления записи"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": "add",
        "record": None
    })

@app.post("/add")
async def add_record(
    name: str = Form(...),
    value: float = Form(...),
    category: str = Form(...),
    description: str = Form("")
):
    """Добавление новой записи"""
    try:
        record = Record(name=name, value=value, category=category, description=description)
        db_manager.add_record(record)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка добавления: {str(e)}")

@app.get("/edit/{record_id}", response_class=HTMLResponse)
async def show_edit_form(request: Request, record_id: int):
    """Форма редактирования записи"""
    record = db_manager.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": "edit",
        "record": record
    })

@app.post("/edit/{record_id}")
async def edit_record(
    record_id: int,
    name: str = Form(...),
    value: float = Form(...),
    category: str = Form(...),
    description: str = Form("")
):
    """Обновление существующей записи"""
    try:
        record = Record(id=record_id, name=name, value=value, category=category, description=description)
        success = db_manager.update_record(record)
        if not success:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обновления: {str(e)}")

@app.get("/delete/{record_id}")
async def delete_record(record_id: int):
    """Удаление записи"""
    try:
        success = db_manager.delete_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка удаления: {str(e)}")

@app.get("/search", response_class=HTMLResponse)
async def search_records(request: Request, q: str = ""):
    """Поиск записей"""
    if q.strip():
        records = db_manager.search_records(q.strip())
    else:
        records = db_manager.get_all_records()
    return templates.TemplateResponse("records.html", {
        "request": request,
        "records": records,
        "total": len(records),
        "search_query": q
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Страница о проекте"""
    return templates.TemplateResponse("about.html", {"request": request})

# API эндпоинты для тестирования
@app.get("/api/health")
async def health_check():
    """Проверка подключения к БД"""
    try:
        records = db_manager.get_all_records()
        return {"status": "ok", "database": "connected", "records_count": len(records)}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}