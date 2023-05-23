FROM apache/airflow:2.5.3
RUN pip instaLL 'apache-airflow[pandas]'
RUN pip instaLl boto3 botocore==1.29.102 s3fs
