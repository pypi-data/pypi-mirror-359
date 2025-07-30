from google.cloud import bigquery

_bigquery_client = None
APPEND = bigquery.WriteDisposition.WRITE_APPEND

def _initialize_client():
    global _bigquery_client
    
    if _bigquery_client is None:
        _bigquery_client = bigquery.Client()
    return _bigquery_client

def query_to_dataframe(query):
    client = _initialize_client()
    query_job = client.query(query)
        
    return query_job.result().to_dataframe()

def load_from_dataframe(df, table, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE):
    client = _initialize_client()
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )
    job = client.load_table_from_dataframe(df, table, job_config=job_config)
    job.result()
    print(f'uploaded {len(df)} rows to {table}')