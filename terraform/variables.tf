variable "project_id" { type = string }
variable "region" { type = string default = "us-central1" }

variable "be_image" { type = string }
variable "be_service_name" { type = string default = "ofc-backend" }
variable "be_port" { type = number default = 8000 }
variable "be_min_instances" { type = number default = 0 }
variable "be_max_instances" { type = number default = 3 }
variable "be_cors_allow_origins" { type = string default = "*" }

variable "fe_image" { type = string }
variable "fe_service_name" { type = string default = "ofc-frontend" }
variable "fe_port" { type = number default = 8080 }
variable "fe_min_instances" { type = number default = 0 }
variable "fe_max_instances" { type = number default = 3 }
