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

resource "google_service_account" "be_sa" {
  account_id   = "${var.be_service_name}-sa"
  display_name = "Cloud Run SA for Backend"
}

resource "google_service_account" "fe_sa" {
  account_id   = "${var.fe_service_name}-sa"
  display_name = "Cloud Run SA for Frontend"
}

resource "google_cloud_run_v2_service" "backend" {
  name     = var.be_service_name
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.be_sa.email
    scaling {
      min_instance_count = var.be_min_instances
      max_instance_count = var.be_max_instances
    }
    containers {
      image = var.be_image
      env { name = "PORT" value = tostring(var.be_port) }
      env { name = "CORS_ALLOW_ORIGINS" value = var.be_cors_allow_origins }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  project  = google_cloud_run_v2_service.backend.project
  location = google_cloud_run_v2_service.backend.location
  name     = google_cloud_run_v2_service.backend.name
  role   = "roles/run.invoker"
  member = "allUsers"
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = var.fe_service_name
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.fe_sa.email
    scaling {
      min_instance_count = var.fe_min_instances
      max_instance_count = var.fe_max_instances
    }
    containers {
      image = var.fe_image
      env { name = "PORT" value = tostring(var.fe_port) }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  project  = google_cloud_run_v2_service.frontend.project
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  role   = "roles/run.invoker"
  member = "allUsers"
}
