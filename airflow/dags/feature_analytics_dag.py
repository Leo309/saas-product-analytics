"""
Airflow DAG for SaaS Feature Adoption Analytics pipeline.

Schedule: Daily at 6:00 AM UTC
Flow: load_raw_data → dbt_staging → dbt_marts → dbt_test → dbt_docs
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/dbt"

default_args = {
    "owner": "analytics",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="feature_adoption_analytics",
    default_args=default_args,
    description="Daily pipeline: load raw data → dbt staging → marts → tests",
    schedule_interval="0 6 * * *",  # 6 AM UTC daily
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["analytics", "dbt", "feature-adoption"],
) as dag:

    # Step 1: Install dbt dependencies (idempotent)
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt deps",
    )

    # Step 2: Run staging models (views — clean & cast raw data)
    dbt_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select staging",
    )

    # Step 3: Run mart models (tables — business metrics)
    dbt_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select marts",
    )

    # Step 4: Run tests (data quality checks)
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    # Step 5: Generate dbt docs
    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt docs generate",
    )

    # DAG dependency chain
    dbt_deps >> dbt_staging >> dbt_marts >> dbt_test >> dbt_docs
