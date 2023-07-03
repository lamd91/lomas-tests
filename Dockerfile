# the dockerfile is for localhost testing and pytest
FROM python:3.8 AS sdd_server

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN git clone https://github.com/IBM/differential-privacy-library
RUN cd differential-privacy-library && pip install .

RUN rm -rf differential-privacy-library

# We do not copy the code here, but in the test and prod stages only.
# For developping, we mount a volume with the -v option at runtime.
#COPY ./src/ /code/

FROM sdd_server AS sdd_server_test
# run tests with pytest
COPY ./src/ /code/
COPY ./tests/ /code/tests/
COPY .configs/example_config.yaml /usr/sdd-poc-server/runtime.yaml
CMD ["python", "-m", "pytest", "tests/"]

FROM sdd_server AS sdd_server_prod
COPY ./src/ /code/
# run as local server
# Disable this for now, as we do not run a mongodb instance.
COPY ./configs/example_config.yaml /usr/sdd-poc-server/runtime.yaml
CMD ["python", "uvicorn_serve.py"]

FROM sdd_server AS sdd_server_dev
ENV PYTHONDONTWRITEBYTECODE 1
CMD ["python", "uvicorn_serve.py"]
# Empty, used for development.