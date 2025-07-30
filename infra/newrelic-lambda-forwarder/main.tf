provider "aws" {
  region = "ap-southeast-2"
}

module "newrelic_log_forwarder" {
  source         = "github.com/newrelic/aws-log-ingestion"
  nr_license_key = "XXX-XXXX-XXXX"
  nr_tags        = "owner:emily"
}