provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-billing-archive"
  location = "East US"
}

resource "azurerm_storage_account" "storage" {
  name                     = "billingarchivestorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  kind                     = "StorageV2"

  lifecycle_rule {
    name = "move-to-cool-then-archive"
    enabled = true

    filters {
      blob_types = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 30
        tier_to_archive_after_days_since_modification_greater_than = 90
      }
    }
  }
}

resource "azurerm_storage_container" "archive_container" {
  name                  = "billing-archive"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}
