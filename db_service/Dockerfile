FROM python:3.12
WORKDIR /app
RUN pip install fastapi uvicorn tinydb pydantic
COPY main.py .
EXPOSE 8181
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]
