def get_billing_record(billing_id):
    # Step 1: Try to read from Cosmos DB (hot data)
    record = read_from_cosmos_db(billing_id)
    if record:
        record['source'] = 'cosmos'
        return record

    # Step 2: Fallback – Read from Blob Storage (cold data)
    record = read_from_blob_storage(billing_id)
    if record:
        record['source'] = 'blob'
        return record

    # Step 3: Record not found
    return {
        "error": "Billing record not found",
        "billingId": billing_id
    }


def read_from_cosmos_db(billing_id):
    container = cosmos_client.get_database_client("BillingDB").get_container_client("BillingRecords")
    
    try:
        # Assume billing_id is the partition key and ID
        return container.read_item(item=billing_id, partition_key=billing_id)
    except CosmosResourceNotFoundError:
        return None


def read_from_blob_storage(billing_id):
    import json

    # Assume blobs are stored in format: "billing-archive/YYYY/MM/batch.json"
    # You may need to maintain an index or naming convention to locate the right file
    archive_blobs = get_candidate_blobs(billing_id)  # e.g., recent months or index scan

    for blob_name in archive_blobs:
        blob_client = blob_service.get_container_client("billing-archive").get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()
        records = json.loads(blob_data)

        for record in records:
            if record["billingId"] == billing_id:
                return record

    return None


def get_candidate_blobs(billing_id):
    # If you're not indexing, you may need to scan known archive files
    # Ideally, maintain an index mapping billingId -> blobName for fast lookup
    return [
        "2023/12/archive_batch_1.json",
        "2024/01/archive_batch_2.json",
        # ...
    ]
