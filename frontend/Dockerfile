FROM python:3.10-slim

WORKDIR /app

# Copy requirements.txt first to leverage Docker cache efficiently
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the application code
COPY ./app.py /app/app.py

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
