# AWS deployment

Terraform is the source of truth for the AWS infrastructure, including ECS
clusters, services, task definitions, ALBs, RDS, EFS, Secrets Manager, and
CloudWatch resources.

Apply the stack separately for Staging and Production with separate Terraform
state. Never share state between the environments and never run `terraform
apply` without selecting an environment variable file.

Each environment contains:

- A dedicated VPC, public ALB, private RDS MariaDB, ECS cluster and CloudWatch
  log groups.
- Staging: one API task, one frontend task, and one Uptime Kuma task in public
  subnets, with no NAT gateway. EFS mount targets are created in the same
  public subnets.
- Production: API and frontend tasks in private subnets, autoscaling between
  1 and 3 copies each when CPU stays above 70%, an ALB in public subnets, and
  one NAT gateway per Availability Zone for outbound image/log/secret access.
  Uptime Kuma and its EFS mount targets use private subnets.
- One Uptime Kuma task with an encrypted EFS volume. Create monitors in Kuma for
  the frontend URL and `/api/health/ready` on both environments.
- A deployment circuit breaker on the API and frontend. A deploy that fails its
  health checks rolls back to the last working version.
- CloudWatch alarms for API CPU (70%), memory (80%) and p95 response time
  (500 ms), sent to an SNS topic. Set `alert_email` to get them by email
  and confirm the email AWS sends, or subscribe to the topic in the SNS
  console (`terraform output alerts_topic`).
- A CloudWatch dashboard with CPU, memory, network, response time, running
  copies and database storage. `terraform output dashboard_url` links to it.

The deployed hostnames use the purchased `placeholder-store.site` domain:

| Environment | Frontend | API | Uptime Kuma |
|---|---|---|---|
| Staging | `staging.placeholder-store.site` | `staging.placeholder-store.site/api` | `staging-monitor.placeholder-store.site` |
| Production | `store.placeholder-store.site` | `store.placeholder-store.site/api` | `monitor.placeholder-store.site` |

Before the first apply:

1. Request an ACM certificate in `ap-southeast-2` covering the hostnames for
   the environment.
2. Complete ACM DNS validation.
3. Create DNS records for the hostnames pointing to the Terraform ALB output.
4. Confirm that the Docker image tags in the selected `.tfvars` file already
   exist in Docker Hub.

## Environment variable files

Use `terraform.tfvars.example` as a template. It contains no credentials and
is safe to commit. Copy it to an ignored file for the environment you are
deploying:

```powershell
Copy-Item `
  .\infra\terraform\terraform.tfvars.example `
  .\infra\terraform\staging.tfvars
```

For Production, create a separate file:

```powershell
Copy-Item `
  .\infra\terraform\terraform.tfvars.example `
  .\infra\terraform\production.tfvars
```

Edit the copied file and replace:

- `YOUR_DOCKERHUB_USERNAME` and `COMMIT_SHA` with an image that exists in
  Docker Hub.
- `AWS_ACCOUNT_ID` and `CERTIFICATE_ID` with the ACM certificate ARN for the
  selected environment.
- Hostnames if your DNS names differ.
- `environment` with `staging` or `production`.

Production uses the same images as staging:

```hcl
environment    = "production"
api_image      = "docker.io/YOUR_DOCKERHUB_USERNAME/placeholder-store:backend-COMMIT_SHA"
frontend_image = "docker.io/YOUR_DOCKERHUB_USERNAME/placeholder-store:frontend-COMMIT_SHA"
frontend_host  = "store.placeholder-store.site"
uptime_host    = "monitor.placeholder-store.site"
```

The real `staging.tfvars` and `production.tfvars` files are ignored by Git.
Do not commit them if they contain environment-specific credentials or
secrets. Terraform obtains AWS authentication from the configured AWS CLI
profile or environment, not from these files:

```powershell
aws configure
# or
$env:AWS_PROFILE = "your-aws-profile"
```

The frontend calls the API at `/api` on its own domain. The load balancer sends `/api/*` to the API and strips the prefix.

## Terraform commands

Run these commands from the repository root. Always pass exactly one
environment file.

```powershell
terraform -chdir=infra/terraform init

terraform -chdir=infra/terraform plan -var-file=staging.tfvars
terraform -chdir=infra/terraform apply -var-file=staging.tfvars
```

For Production:

```powershell
terraform -chdir=infra/terraform plan -var-file=production.tfvars
terraform -chdir=infra/terraform apply -var-file=production.tfvars
```

Do not run:

```powershell
terraform -chdir=infra/terraform apply
```

because it does not explicitly identify the target environment.

## Validation and smoke tests

Run infrastructure validation before applying:

```powershell
.\infra\tests\validate.ps1
```

After DNS records and ECS services stabilize, run the smoke test for the
selected environment:

```powershell
.\infra\tests\smoke.ps1 `
  -FrontendUrl "https://staging.placeholder-store.site" `
  -ApiHealthUrl "https://staging.placeholder-store.site/api/health/ready" `
  -UptimeUrl "https://staging-monitor.placeholder-store.site"
```

Use the Production hostnames for a Production smoke test.

To show autoscaling and response times, send load to Production and watch the
dashboard. A new copy should start within 5 minutes:

```powershell
python infra/tests/load.py https://store.placeholder-store.site/api/places --minutes 10 --workers 50
```

## State and secrets

Use separate remote Terraform state for Staging and Production. Do not commit
the real `.tfvars` files, Terraform state, generated plans, database passwords,
JWT secrets, or AWS credentials. Only `terraform.tfvars.example` is intended
to be committed.

CD deploys new images by running `terraform apply` with the new image tags.
Terraform ignores `desired_count` on the services, so `apply` doesn't undo
autoscaling.

CD runs `.github/workflows/deploy.yml` for staging, then E2E, then production.
It needs `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` secrets (plus an
optional `ALERT_EMAIL` secret), and these repo variables: `TF_STATE_BUCKET`,
`STAGING_CERTIFICATE_ARN`, `PRODUCTION_CERTIFICATE_ARN`,
`STAGING_FRONTEND_HOST`, `PRODUCTION_FRONTEND_HOST`, `STAGING_UPTIME_HOST`
and `PRODUCTION_UPTIME_HOST`.
