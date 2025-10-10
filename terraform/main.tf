############################################################
# Overseas Food Trading (OFC) - Cloud Run (FE & BE)
# Terraform Configuration File (main.tf)
############################################################

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.39"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region"
}

variable "be_image" {
  type        = string
  description = "Backend container image"
}

variable "fe_image" {
  type        = string
  description = "Frontend container image"
}

variable "be_service_name" {
  type    = string
  default = "ofc-be2"
}

variable "fe_service_name" {
  type    = string
  default = "ofc-frontend2"
}

variable "be_sa_account_id" {
  type    = string
  default = "ofc-backend-sa"
}

variable "fe_sa_account_id" {
  type    = string
  default = "ofc-frontend-sa"
}

data "google_service_account" "be_sa" {
  project    = var.project_id
  account_id = var.be_sa_account_id
}

data "google_service_account" "fe_sa" {
  project    = var.project_id
  account_id = var.fe_sa_account_id
}

resource "google_cloud_run_v2_service" "backend" {
  name     = var.be_service_name
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = data.google_service_account.be_sa.email

    containers {
      image = var.be_image

    }
  }
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = var.fe_service_name
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = data.google_service_account.fe_sa.email

    containers {
      image = var.fe_image
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  project  = google_cloud_run_v2_service.backend.project
  location = google_cloud_run_v2_service.backend.location
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  project  = google_cloud_run_v2_service.frontend.project
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "backend_url" {
  value = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.frontend.uri
}
