# Timer-triggered Azure Function (runs daily, or weekly)
def archive_old_records_from_cosmos_to_blob(timer_event):
    from datetime import datetime, timedelta
    import json

    # Setup: Define time window
    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=90)

    # Setup: Initialize Cosmos DB client
    cosmos_client = CosmosClient(connection_string="COSMOS_CONN_STRING")
    container = cosmos_client.get_database_client("BillingDB").get_container_client("BillingRecords")

    # Setup: Initialize Blob Storage client
    blob_service = BlobServiceClient.from_connection_string("BLOB_CONN_STRING")
    container_client = blob_service.get_container_client("billing-archive")

    # Step 1: Query Cosmos DB for records older than 90 days
    query = "SELECT * FROM c WHERE c.timestamp < @cutoffDate"
    parameters = [{"name": "@cutoffDate", "value": cutoff_date.isoformat()}]

    old_records = container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True)

    batch = []
    for record in old_records:
        batch.append(record)

        # Optional: Process in batches (e.g., every 100 records)
        if len(batch) == 100:
            archive_batch_to_blob(batch, container_client)
            mark_records_as_archived(batch, container)
            batch = []

    # Archive remaining records
    if batch:
        archive_batch_to_blob(batch, container_client)
        mark_records_as_archived(batch, container)


def archive_batch_to_blob(records, container_client):
    from uuid import uuid4
    import json

    blob_name = f"archive_{uuid4()}.json"
    blob_data = json.dumps(records)

    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(blob_data, overwrite=True)


def mark_records_as_archived(records, cosmos_container):
    for record in records:
        record['archived'] = True  # Or remove if deletion is preferred
        cosmos_container.upsert_item(record)

    # OR: for deletion instead of marking
    # for record in records:
    #     cosmos_container.delete_item(record['id'], partition_key=record['partitionKey'])
