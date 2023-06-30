# app/Dockerfile

FROM python:3.11.4-slim

WORKDIR /recrete-prognosis

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "recrete-prognosis/app.py", "--server.port=8501", "--server.address=0.0.0.0"]