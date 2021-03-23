FROM projectmonai/monai:latest

# Install vi
RUN apt update -y; apt-get install vim -y; apt-get -y install sudo


# Mounts
# /mnt/inputdata -> iris train data
# /mnt/validationdata -> iris validation data
# /mnt/output -> participant algorithm output -> 92-prediction-output
# /mnt/private -> participant private output -> 92-private-output

# Create appuser for use in kubernetes (otherwise the container has no user)
RUN groupadd -g 999 appuser && \
    useradd -r -u 1000 -g appuser appuser
USER appuser

COPY ./docker_code_inference/inference_on_test.py /app/
COPY ./model_output/best_metric_model.pth  /app/

WORKDIR /app/
#CMD sleep 1200 # for creating sleeping debug docker image
CMD ["python", "inference_on_test.py"]
