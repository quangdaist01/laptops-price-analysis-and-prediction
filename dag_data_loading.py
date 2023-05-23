import logging
import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.models.connection import Connection
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator, PythonVirtualenvOperator
import sql_statements
import pandas as pd

from preprocessing_utils import *


# TODO: Add data quality checks
# def data_quality_checks(tables):
#     tables = tables.split(',')
#     redshift_hook = PostgresHook("redshift")
#     for table in tables:
#         records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {table}")
#         if len(records) < 1 or len(records[0]) < 1:
#             raise ValueError(f"Data quality check failed. {table} returned no results")
#         num_records = records[0][0]
#         if num_records < 1:
#             raise ValueError(f"Data quality check failed. {table} contained 0 rows")
#         logging.info(f"Data quality on table {table} check passed with {records[0][0]} records")
#
#
# def cleaning_stagings():
#     redshift_hook = PostgresHook("redshift")
#     sql_stmt = sql_statements.drop_staging
#     redshift_hook.run(sql_stmt)
#     print(f"Staging tables dropped successfully.")


def loading_table(table):
    redshift_hook = PostgresHook("postgres_conn")

    if table == 'dim_ram':
        sql_stmt = sql_statements.load_dim_ram
    if table == 'dim_ram_type':
        sql_stmt = sql_statements.load_dim_ram_type
    elif table == 'dim_ram_speed':
        sql_stmt = sql_statements.load_dim_ram_speed
    elif table == 'dim_cpu_speed':
        sql_stmt = sql_statements.load_dim_cpu_speed
    elif table == 'dim_cpu_type':
        sql_stmt = sql_statements.load_dim_cpu_type
    elif table == 'dim_gpu_type':
        sql_stmt = sql_statements.load_dim_gpu_type
    elif table == 'dim_storage':
        sql_stmt = sql_statements.load_dim_storage
    elif table == 'dim_screen_size':
        sql_stmt = sql_statements.load_dim_screen_size
    elif table == 'dim_resolution':
        sql_stmt = sql_statements.load_dim_resolution
    elif table == 'dim_material':
        sql_stmt = sql_statements.load_dim_material
    elif table == 'dim_os':
        sql_stmt = sql_statements.load_dim_os
    elif table == 'dim_released_year':
        sql_stmt = sql_statements.load_dim_released_year
    elif table == 'dim_name':
        sql_stmt = sql_statements.load_dim_name
    elif table == 'dim_warranty':
        sql_stmt = sql_statements.load_dim_warranty
    elif table == 'dim_brand':
        sql_stmt = sql_statements.load_dim_brand
    elif table == 'fact_laptop':
        sql_stmt = sql_statements.load_fact_laptop

    redshift_hook.run(sql_stmt)
    print(f"Table {table} was loaded successfully.")


def raw_df_from_s3_to_postgresql():
    # ------------ Read raw df from S3
    import boto3, io
    REGION = "us-east-1"
    ACCESS_KEY_ID = ""
    SECRET_ACCESS_KEY = ""
    BUCKET_NAME = "laptopraw"
    KEY = "raw_data_TGDD_all_used.csv"  # file path in S3 
    s3c = boto3.client("s3", region_name=REGION, aws_access_key_id=ACCESS_KEY_ID,
                       aws_secret_access_key=SECRET_ACCESS_KEY)
    obj = s3c.get_object(Bucket=BUCKET_NAME, Key=KEY)
    df = pd.read_csv(io.BytesIO(obj["Body"].read()), encoding='utf8')

    # ------------ Data cleaning
    df = rename_columns(df, alternative_name=alternative_names)
    # %% CLEANSING
    # Preprocess features
    # todo: Fix nhiều thuộc tính bị nan
    df["brand"] = df["name"].apply(preprocess_name)
    df["used_price"] = df["used_price"].apply(preprocess_used_price)
    df["new_price"] = df["new_price"].apply(preprocess_new_price)
    df['cpu_type'] = df['cpu_type'].apply(preprocess_cpu_type)
    df['cached_cpu'] = df['cached_cpu'].apply(preprocess_cached_cpu)
    df["ram_type"] = df["ram_type"].apply(preprocess_ram_type)
    df["ram_speed"] = df["ram_speed"].apply(preprocess_ram_speed)
    df["storage"] = df["storage"].apply(preprocess_storage)
    df["audio_tech"] = df["audio_tech"].apply(preprocess_audio_tech)
    df["resolution"] = df["resolution"].apply(preprocess_resolution)
    df["os"] = df["os"].apply(preprocess_os)
    df['gpu_type'] = df['gpu_type'].apply(preprocess_gpu_type)
    df['cpu_speed'] = df['cpu_speed'].apply(preprocess_cpu_speed)
    df['max_cpu_speed'] = df['max_cpu_speed'].apply(preprocess_max_cpu_speed)
    df['ram'] = df['ram'].apply(preprocess_ram)
    df['max_ram'] = df['max_ram'].apply(preprocess_max_ram)
    df['has_lightning'] = df['has_lightning'].apply(preprocess_has_lightning)
    df['material'] = df['material'].apply(preprocess_material)
    df['new_warranty'] = df['new_warranty'].apply(preprocess_new_warranty)
    df["used_warranty"] = df["used_warranty"].apply(preprocess_used_warranty)
    df['has_thunderbolt'] = df['ports'].apply(preprocess_thunderbolt)
    df['has_antiglare'] = df['screen_tech'].apply(preprocess_antiglare)
    df['screen_size'] = df['screen_size'].apply(preprocess_screen_size)
    df["webcam"] = df["webcam"].apply(preprocess_webcam)
    df["battery"] = df["battery"].apply(preprocess_battery)
    df['sd_slot'] = df['sd_slot'].apply(preprocess_sd_slot)
    df['scan_frequency'] = df['scan_frequency'].apply(preprocess_scan_frequency)

    #### Tách thuộc tính wireless
    df["bluetooth_tech"] = df["wireless"].apply(lambda s: preprocess_wireless(s)[0])
    df["wifi_tech"] = df["wireless"].apply(lambda s: preprocess_wireless(s)[1])

    #### Tách thuộc tính size_weight
    df["weight"] = df["size_weight"].apply(lambda s: preprocessing_size_weight(s)[0])
    df["thickness"] = df["size_weight"].apply(lambda s: preprocessing_size_weight(s)[1])
    df["width"] = df["size_weight"].apply(lambda s: preprocessing_size_weight(s)[2])
    df["length"] = df["size_weight"].apply(lambda s: preprocessing_size_weight(s)[3])

    #### Tách thuộc tính savings
    df['saved_percent'] = df['savings'].apply(lambda s: preprocess_savings(s)[0])
    df['saved_money'] = df['savings'].apply(lambda s: preprocess_savings(s)[1])

    #### Tách thuộc tính others
    df['has_fingerprint'] = df['others'].apply(lambda s: preprocess_others(s)[0])
    df['has_camera_lock'] = df['others'].apply(lambda s: preprocess_others(s)[1])
    df['has_180_degree'] = df['others'].apply(lambda s: preprocess_others(s)[2])
    df['has_face_id'] = df['others'].apply(lambda s: preprocess_others(s)[3])

    # %%
    # Drop unused columns
    old_columns = ["wireless", "size_weight", "ports", "screen_tech", "savings", 'others', 'Màn hình cảm ứng']
    df.drop(columns=old_columns, inplace=True)

    # Reoder columns
    df = df[ordered_columns]

    # ------------ Load to Postgresql table
    postgres_sql_upload = PostgresHook(postgres_conn_id='postgres_conn', schema='laptop')
    df_iterable = df.fillna(0).itertuples(index=False)
    # Upsert
    postgres_sql_upload.insert_rows('staging_laptop', df_iterable, target_fields=list(df.columns))


def check_is_sold_status():
    pass


def update_is_sold_status_in_staging():
    redshift_hook = PostgresHook("postgres_conn")
    redshift_hook.run(sql_statements.create_is_sold_table)


# /// LOADING TABLES ///
with DAG(
        'laptop_analysis',
        description='Laptop Analysis',
        start_date=datetime.datetime.now(),
        schedule_interval='@weekly',
) as dag:
    loading_fact_laptop_task = PythonOperator(
            task_id='loading_fact_laptop',
            dag=dag,
            op_kwargs={'table': 'fact_laptop'},
            python_callable=loading_table,
    )

    loading_dim_cpu_type_task = PythonOperator(
            task_id='loading_dim_cpu_type',
            dag=dag,
            op_kwargs={'table': 'dim_cpu_type'},
            python_callable=loading_table,
    )

    loading_dim_cpu_speed_task = PythonOperator(
            task_id='loading_dim_cpu_speed',
            dag=dag,
            op_kwargs={'table': 'dim_cpu_speed'},
            python_callable=loading_table,
    )

    loading_dim_gpu_type_task = PythonOperator(
            task_id='loading_dim_gpu_type',
            dag=dag,
            op_kwargs={'table': 'dim_gpu_type'},
            python_callable=loading_table,
    )

    loading_dim_ram_type_task = PythonOperator(
            task_id='loading_dim_ram_type',
            dag=dag,
            op_kwargs={'table': 'dim_ram_type'},
            python_callable=loading_table,
    )

    loading_dim_ram_task = PythonOperator(
            task_id='loading_dim_ram',
            dag=dag,
            op_kwargs={'table': 'dim_ram'},
            python_callable=loading_table,
    )

    loading_dim_resolution_task = PythonOperator(
            task_id='loading_dim_resolution',
            dag=dag,
            op_kwargs={'table': 'dim_resolution'},
            python_callable=loading_table,
    )

    loading_dim_screen_size_task = PythonOperator(
            task_id='loading_dim_screen_size',
            dag=dag,
            op_kwargs={'table': 'dim_screen_size'},
            python_callable=loading_table,
    )

    loading_dim_os_task = PythonOperator(
            task_id='loading_dim_os',
            dag=dag,
            op_kwargs={'table': 'dim_os'},
            python_callable=loading_table,
    )

    loading_dim_material_task = PythonOperator(
            task_id='loading_dim_material',
            dag=dag,
            op_kwargs={'table': 'dim_material'},
            python_callable=loading_table,
    )

    loading_dim_ram_speed_task = PythonOperator(
            task_id='loading_dim_ram_speed',
            dag=dag,
            op_kwargs={'table': 'dim_ram_speed'},
            python_callable=loading_table,
    )

    loading_dim_storage_task = PythonOperator(
            task_id='loading_dim_storage',
            dag=dag,
            op_kwargs={'table': 'dim_storage'},
            python_callable=loading_table,
    )

    loading_dim_released_year_task = PythonOperator(
            task_id='loading_dim_released_year',
            dag=dag,
            op_kwargs={'table': 'dim_released_year'},
            python_callable=loading_table,
    )

    loading_dim_name_task = PythonOperator(
            task_id='loading_dim_name',
            dag=dag,
            op_kwargs={'table': 'dim_name'},
            python_callable=loading_table,
    )

    loading_dim_brand_task = PythonOperator(
            task_id='loading_dim_brand',
            dag=dag,
            op_kwargs={'table': 'dim_brand'},
            python_callable=loading_table,
    )

    loading_dim_warranty_task = PythonOperator(
            task_id='loading_dim_warranty',
            dag=dag,
            op_kwargs={'table': 'dim_warranty'},
            python_callable=loading_table,
    )

    fact_tables_ready_task = DummyOperator(
            task_id='fact_tables_ready'
    )

    dimensions_tables_loaded_task = DummyOperator(
            task_id='dimension_tables_ready'
    )

    staging_table_loaded_task = DummyOperator(
            task_id='staging_table_loaded'
    )

    check_is_sold_status_task = PythonOperator(
            task_id='check_is_sold_status',
            python_callable=check_is_sold_status,
            dag=dag
    )

    update_is_sold_status_in_staging_task = PythonOperator(
            task_id='update_is_sold_status_in_staging',
            python_callable=update_is_sold_status_in_staging,
            dag=dag
    )

    raw_df_from_s3_to_postgresql_task = PythonOperator(
            task_id='raw_df_from_s3_to_postgresql',
            python_callable=raw_df_from_s3_to_postgresql,
            dag=dag
    )

    start_data_cleaning = DummyOperator(
            task_id='start_data_cleaning'
    )

    start_data_cleaning >> raw_df_from_s3_to_postgresql_task

    raw_df_from_s3_to_postgresql_task >> staging_table_loaded_task

    staging_table_loaded_task >> [loading_dim_cpu_type_task,
                                  loading_dim_cpu_speed_task,
                                  loading_dim_gpu_type_task,
                                  loading_dim_ram_type_task,
                                  loading_dim_ram_task,
                                  loading_dim_ram_speed_task,
                                  loading_dim_storage_task,
                                  loading_dim_screen_size_task,
                                  loading_dim_resolution_task,
                                  loading_dim_material_task,
                                  loading_dim_os_task,
                                  loading_dim_released_year_task,
                                  loading_dim_name_task,
                                  loading_dim_warranty_task,
                                  loading_dim_brand_task]

    [loading_dim_cpu_type_task,
     loading_dim_cpu_speed_task,
     loading_dim_gpu_type_task,
     loading_dim_ram_type_task,
     loading_dim_ram_task,
     loading_dim_ram_speed_task,
     loading_dim_storage_task,
     loading_dim_screen_size_task,
     loading_dim_resolution_task,
     loading_dim_material_task,
     loading_dim_os_task,
     loading_dim_released_year_task,
     loading_dim_name_task,
     loading_dim_warranty_task,
     loading_dim_brand_task] >> dimensions_tables_loaded_task

    dimensions_tables_loaded_task >> check_is_sold_status_task >> update_is_sold_status_in_staging_task >> loading_fact_laptop_task >> fact_tables_ready_task
