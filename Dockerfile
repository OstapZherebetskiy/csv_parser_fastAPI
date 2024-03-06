#
FROM python:3.11.6

#
WORKDIR /fast_api_test_tast

#
COPY ./requirements.txt /fast_api_test_tast/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /fast_api_test_tast/requirements.txt

#
COPY ./csv_app /fast_api_test_tast/csv_app

#
CMD ["uvicorn", "csv_app.main:app", "--host", "0.0.0.0", "--port", "80"]