FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY application
# copy everything from the local directory(first .) into the container's /app directory(second .)
COPY  . .

# expose port
EXPOSE 8000

# run application
CMD [ "uvicorn","main:app","--host","0.0.0.0","--port","8000" ]