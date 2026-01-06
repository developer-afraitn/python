FROM python:3.11-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستم
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    locales-all \
    build-essential \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# تنظیمات زبان
ENV LANG=fa_IR.UTF-8
ENV LANGUAGE=fa_IR:fa
ENV LC_ALL=fa_IR.UTF-8

# کپی و نصب کتابخانه‌های اصلی
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

# کپی فایل dev (روی سرور هم هست، ممکن است خالی یا متفاوت باشد)
COPY requirements-dev.txt .
RUN if [ -s requirements-dev.txt ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    else \
        echo "requirements-dev.txt خالی است، نصب رد شد"; \
    fi

# کپی اپلیکیشن
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000", "--reload"]
