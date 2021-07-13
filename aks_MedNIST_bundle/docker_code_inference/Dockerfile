FROM projectmonai/monai:0.4.0

# Install vi
RUN apt update -y; apt-get install vim -y

# Create appuser 
# Note: needed for use in kubernetes (otherwise the container has no user)
# RUN groupadd -g 999 appuser && \
#     useradd -r -u 1000 -g appuser appuser
# USER appuser

COPY ./docker_code_inference/inference_on_test.py /app/
COPY ./model_output/best_metric_model.pth  /app/

WORKDIR /app/
CMD ["python", "inference_on_test.py"]
