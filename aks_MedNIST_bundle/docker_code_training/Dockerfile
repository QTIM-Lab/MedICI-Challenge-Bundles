FROM projectmonai/monai:latest

# Install vi
RUN apt update -y; apt-get install vim -y;

# Create appuser 
# Note: needed for use in kubernetes (otherwise the container has no user)
RUN groupadd -g 999 appuser && \
    useradd -r -u 1000 -g appuser appuser
USER appuser

COPY ./app.py /app/

WORKDIR /app/

CMD ["python", "app.py"]
