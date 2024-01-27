FROM python:3.12.1-slim-bullseye

RUN apt update && \
    apt install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    PATH=PATH:$HOME/.local/bin

COPY ./car_cost /root/car-cost/car_cost
COPY ./poetry.lock /root/car-cost/poetry.lock
COPY ./pyproject.toml /root/car-cost/pyproject.toml

WORKDIR /root/car-cost/
RUN /root/.local/bin/poetry install

ENTRYPOINT [ "/root/.local/bin/poetry" ]
CMD [ "run", "streamlit", "run", "/root/car-cost/car_cost/app.py" ]