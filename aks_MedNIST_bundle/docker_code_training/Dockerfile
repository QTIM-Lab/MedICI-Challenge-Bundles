FROM projectmonai/monai:latest

# Install vi
RUN apt update -y; apt-get install vim -y;

# Mounts
# /mnt/inputdata -> iris train data
# /mnt/validationdata -> iris validation data
# /mnt/output -> participant algorithm output -> 92-prediction-output
# /mnt/private -> participant private output -> 92-private-output

# Create appuser for use in kubernetes (otherwise the container has no user)
RUN groupadd -g 999 appuser && \
    useradd -r -u 1000 -g appuser appuser
USER appuser

COPY ./app.py /app/

WORKDIR /app/

CMD ["python", "app.py"]
# CMD sleep 600
#bCMD ["python", "/app/ingestion_program/ingestion.py", "/mnt/inputdata", "/mnt/output", "/app/ingestion_program", "/app/sample_code_submission"]
