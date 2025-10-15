project_id = "nulleffect-qa"
region     = "us-central1"

be_image = "us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-be:latest"
fe_image = "us-central1-docker.pkg.dev/nulleffect-qa/ofc/ofc-fe:latest"
fe_service_name = "ofc-frontend2"

be_min_instances      = 0
be_max_instances      = 3
fe_min_instances      = 0
fe_max_instances      = 3
be_cors_allow_origins = "*"
