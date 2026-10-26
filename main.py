import calendar
from datetime import date
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    relativedelta = None

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR))


def compute_age(birth_date: date, today: date) -> tuple[int, int, int]:
    """Calculate age in years, months, and days."""
    if relativedelta is not None:
        diff = relativedelta(today, birth_date)
        return diff.years, diff.months, diff.days

    y = today.year - birth_date.year
    m = today.month - birth_date.month
    d = today.day - birth_date.day

    if d < 0:
        m -= 1
        prev_month = today.month - 1 if today.month > 1 else 12
        prev_year = today.year if today.month > 1 else today.year - 1
        d += calendar.monthrange(prev_year, prev_month)[1]

    if m < 0:
        y -= 1
        m += 12

    return y, m, d


@app.get("/static/{file_name}")
async def get_static_file(file_name: str):
    file_path = BASE_DIR / file_name
    if file_path.is_file() and file_path.resolve().is_relative_to(BASE_DIR):
        return FileResponse(file_path)
    return HTMLResponse(status_code=404, content="File Not Found")


@app.get("/style.css")
async def get_style_direct():
    return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "result": None, "birthdate": ""},
    )


@app.post("/", response_class=HTMLResponse)
async def calculate_age(request: Request, birthdate: str = Form(...)):
    try:
        birth_date = date.fromisoformat(birthdate)
        today = date.today()

        if birth_date > today:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "request": request,
                    "result": {"error": "Birthdate cannot be in the future."},
                    "birthdate": birthdate,
                },
            )

        years, months, days = compute_age(birth_date, today)
        result = {"years": years, "months": months, "days": days}
    except Exception:
        result = {"error": "Please provide a valid date."}

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "result": result, "birthdate": birthdate},
    )





