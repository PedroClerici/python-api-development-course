FROM python:3

# Intalling and configuring poetry
RUN pip install "poetry"
RUN poetry config virtualenvs.create false

WORKDIR /usr/src/app

COPY poetry.lock pyproject.toml ./

RUN poetry install

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]