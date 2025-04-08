# 🔄 Azure Serverless Billing Archival Solution

## 🧩 Problem
As billing records grow in Azure Cosmos DB, we face increased costs and performance issues. We need to:
- Retain recent (hot) billing data in Cosmos DB
- Archive old (cold) data to cheaper storage
- Enable seamless access to both without client changes

---

## 🚀 Solution
We built a cost-optimized, serverless architecture using:
- **Azure Functions (Timer Trigger)** for scheduled archival
- **Azure Cosmos DB** for hot records
- **Azure Blob Storage** for archived cold records
- **Unified Read Function** to abstract source
- **Terraform** to provision the infrastructure
- **Blob Tiering** rules to reduce costs over time

---

## 🛠️ Components

### ✅ Timer-Triggered Archive Function
Pseudocode: [`functions/archive_function.py`](./functions/archive_function.py)

- Runs daily/weekly
- Moves records older than 90 days to Blob Storage
- Optional: deletes or flags records as archived

### ✅ Unified Read Function
Pseudocode: [`functions/read_function.py`](./functions/read_function.py)

- Reads from Cosmos DB first
- Falls back to archived JSON in Blob
- Returns uniform data format with `"source": "cosmos"` or `"blob"`

### ✅ Terraform Infra Setup
Code: [`terraform/main.tf`](./terraform/main.tf)

- Creates resource group, storage account, blob container
- Applies lifecycle rules:
  - Move to Cool tier after 30 days
  - Move to Archive tier after 90 days

---

## 📐 Architecture Diagram

![Billing Archival Diagram](./architecture/billing-archival-diagram.png)

---

## 💡 Cost Optimization
- **Blob tiering** reduces long-term storage costs
- **Serverless functions** eliminate compute provisioning
- Future improvements:
  - Add Azure Table/Redis index for archived lookups
  - Add compression (e.g. GZIP) for archived blobs

---

## ✅ To Run (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
