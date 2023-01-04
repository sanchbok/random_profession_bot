FROM python:3.9
WORKDIR /app
ADD bot ./bot
COPY ["requirements.txt", "commands.sh", "./"]
RUN python -m pip install --upgrade pip && pip install -r requirements.txt && mkdir data
ENTRYPOINT ["bash", "commands.sh"]