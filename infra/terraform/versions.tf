terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  # State local (fora do git, ver .gitignore). Para o grupo, trocar por backend "azurerm".
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  # Fixa a assinatura: se o az estiver logado na conta errada, o Terraform falha em vez de aplicar lá.
  subscription_id     = var.subscription_id
  storage_use_azuread = true
}
