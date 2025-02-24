FROM python:3.8-slim

EXPOSE 8002

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt . 
RUN python -m pip install -r requirements.txt 
    
WORKDIR /app     
COPY . /app      
  
# Install your app
COPY . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# Install your app
CMD python -m uvicorn main:app --host 0.0.0.0 --port 8081     