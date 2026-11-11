resource "random_string" "sufixo" {
  length  = 5
  upper   = false
  special = false
}

resource "random_password" "db" {
  length  = 32
  special = false
}

locals {
  nome  = "${var.prefixo}-${random_string.sufixo.result}"
  acr   = "${var.prefixo}acr${random_string.sufixo.result}"
  tags  = { projeto = "zela", origem = "terraform", disciplina = "gs-citizentech" }
  image = var.imagem != "" ? var.imagem : "mcr.microsoft.com/k8se/quickstart:latest"
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.nome}"
  location = var.location
  tags     = local.tags
}

# ---------- Registro de imagens ----------
resource "azurerm_container_registry" "acr" {
  name                = local.acr
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = local.tags
}

# ---------- Banco ----------
resource "azurerm_postgresql_flexible_server" "db" {
  name                          = "psql-${local.nome}"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  version                       = "16"
  sku_name                      = "B_Standard_B1ms"
  storage_mb                    = 32768
  administrator_login           = "zela"
  administrator_password        = random_password.db.result
  backup_retention_days         = 7
  public_network_access_enabled = true
  zone                          = "1"
  tags                          = local.tags

  lifecycle {
    ignore_changes = [zone, high_availability[0].standby_availability_zone]
  }
}

resource "azurerm_postgresql_flexible_server_database" "zela" {
  name      = "zela"
  server_id = azurerm_postgresql_flexible_server.db.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

# A regra 0.0.0.0 a 0.0.0.0 é a regra especial do Azure "permitir serviços do Azure".
# Não abre o banco para a internet; a conexão ainda exige senha e TLS.
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure" {
  name             = "somente-servicos-azure"
  server_id        = azurerm_postgresql_flexible_server.db.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# ---------- Logs e métricas ----------
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "log-${local.nome}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}

# ---------- Aplicação ----------
resource "azurerm_container_app_environment" "env" {
  name                       = "cae-${local.nome}"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  tags                       = local.tags
}

resource "azurerm_user_assigned_identity" "app" {
  name                = "id-${local.nome}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
}

resource "azurerm_container_app" "api" {
  name                         = "ca-${local.nome}"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"
  tags                         = local.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.app.id]
  }

  registry {
    server   = azurerm_container_registry.acr.login_server
    identity = azurerm_user_assigned_identity.app.id
  }

  secret {
    name  = "database-url"
    value = "postgresql+psycopg://zela:${random_password.db.result}@${azurerm_postgresql_flexible_server.db.fqdn}:5432/zela?sslmode=require"
  }
  secret {
    name  = "robo-token"
    value = var.robo_token
  }
  secret {
    name  = "operador-token"
    value = var.operador_token
  }
  secret {
    name  = "portal-senha"
    value = var.portal_demo_senha != "" ? var.portal_demo_senha : "desativado"
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 1
    max_replicas = 2

    container {
      name   = "api"
      image  = local.image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
      env {
        name        = "ROBO_TOKEN"
        secret_name = "robo-token"
      }
      env {
        name        = "OPERADOR_TOKEN"
        secret_name = "operador-token"
      }
      env {
        name  = "PORTAL_DEMO_USUARIO"
        value = var.portal_demo_usuario
      }
      dynamic "env" {
        for_each = nonsensitive(var.portal_demo_senha != "") ? toset(["1"]) : toset([])
        content {
          name        = "PORTAL_DEMO_SENHA"
          secret_name = "portal-senha"
        }
      }
      env {
        name  = "UPLOAD_DIR"
        value = "/app/uploads"
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }
    }
  }

  depends_on = [azurerm_role_assignment.acr_pull]
}

# ---------- Alerta (Azure Monitor) ----------
resource "azurerm_monitor_action_group" "email" {
  name                = "ag-${local.nome}"
  resource_group_name = azurerm_resource_group.rg.name
  short_name          = "zela"

  email_receiver {
    name          = "equipe"
    email_address = var.email_alerta
  }
}

# Dispara quando a API devolve respostas 5xx.
resource "azurerm_monitor_metric_alert" "erros_5xx" {
  name                = "zela-erros-5xx"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_container_app.api.id]
  description         = "Mais de 5 respostas 5xx em 5 minutos."
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_namespace = "Microsoft.App/containerApps"
    metric_name      = "Requests"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5

    dimension {
      name     = "StatusCodeCategory"
      operator = "Include"
      values   = ["5xx"]
    }
  }

  action {
    action_group_id = azurerm_monitor_action_group.email.id
  }
  tags = local.tags
}
