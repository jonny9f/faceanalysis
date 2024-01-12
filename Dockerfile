FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime
ENV DEBIAN_FRONTEND noninteractive\
    SHELL=/bin/bash
RUN apt-get update && apt-get install -y --no-install-recommends wget
WORKDIR /app
RUN pip install deepface fastapi uvicorn && pip uninstall opencv-python -y && pip install opencv-python-headless 
COPY serve.py  haarcascade_frontalface_default.xml download_model.py .
RUN python download_model.py
#COPY runprod_entrypoint.py .
# RUN pip install runpod
# ENV MODEL_PATH="/app/model/"
EXPOSE 5000 
CMD [ "python", "-u", "serve.py" ]