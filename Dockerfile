FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py .

# This example uses Python's standard library only: no pip packages needed.
EXPOSE 5000
CMD ["python", "app.py"]
