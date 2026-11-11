variable "subscription_id" {
  description = "ID da assinatura Azure for Students (az-fiap account show --query id)."
  type        = string
}

variable "location" {
  description = "Região. Se a assinatura de estudante bloquear, tente eastus2 ou centralus."
  type        = string
  default     = "brazilsouth"
}

variable "prefixo" {
  description = "Prefixo dos recursos (minúsculas, sem hífen)."
  type        = string
  default     = "zela"
}

variable "imagem" {
  description = "Imagem da API no ACR, por exemplo zelaacr.azurecr.io/zela-api:latest. Vazio usa uma imagem de teste até o primeiro push."
  type        = string
  default     = ""
}

variable "email_alerta" {
  description = "E-mail que recebe o alerta."
  type        = string
}

variable "robo_token" {
  description = "Token do robô UiPath (x-robo-token)."
  type        = string
  sensitive   = true
}

variable "operador_token" {
  description = "Token da triagem (x-operador-token)."
  type        = string
  sensitive   = true
}

variable "portal_demo_usuario" {
  type    = string
  default = ""
}

variable "portal_demo_senha" {
  type      = string
  default   = ""
  sensitive = true
}
