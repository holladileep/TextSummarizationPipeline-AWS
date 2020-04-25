FROM python:3.7
RUN pip3 install pandas
RUN pip3 install newspaper3k
RUN pip3 install sentry_sdk
RUN pip3 install boto3
COPY . /src
CMD ["python", "/src/docker-auto-build.py"]