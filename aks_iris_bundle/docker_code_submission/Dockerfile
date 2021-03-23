FROM codalab/codalab-legacy:latest

# Install vi
RUN apt update -y; apt-get install vim -y; apt-get -y install sudo

COPY ./ingestion_program /app/ingestion_program
COPY ./sample_code_submission /app/sample_code_submission

WORKDIR /app/

RUN groupadd -g 999 appuser && \
    useradd -r -u 1000 -g appuser appuser
USER appuser

# CMD sleep 10000
CMD ["python", "/app/ingestion_program/ingestion.py", "/mnt/inputdata", "/mnt/output", "/appq/ingestion_program", "/app/sample_code_submission"]
