# AWS deployment

Terraform is the source of truth for the AWS infrastructure, including ECS
clusters, services, task definitions, ALBs, RDS, EFS, Secrets Manager, and
CloudWatch resources.

Apply the stack separately for Staging and Production with separate Terraform
state. Never share state between the environments and never run `terraform
apply` without selecting an environment variable file.

Each environment contains:

- A dedicated VPC, public ALB, private RDS PostgreSQL, ECS cluster and CloudWatch
  log groups.
- Staging: one API task, one frontend task, and one Uptime Kuma task in public
  subnets, with no NAT gateway. EFS mount targets are created in the same
  public subnets.
- Production: two API tasks and two frontend tasks in private subnets, an ALB in
  public subnets, and one NAT gateway per Availability Zone for outbound
  image/log/secret access. Uptime Kuma and its EFS mount targets use private
  subnets.
- One Uptime Kuma task with an encrypted EFS volume. Create monitors in Kuma for
  the frontend URL and `/health/ready` on both environments.

The deployed hostnames use the purchased `placeholder-store.site` domain:

| Environment | Frontend | API | Uptime Kuma |
|---|---|---|---|
| Staging | `staging.placeholder-store.site` | `staging-api.placeholder-store.site` | `staging-monitor.placeholder-store.site` |
| Production | `store.placeholder-store.site` | `api.placeholder-store.site` | `monitor.placeholder-store.site` |

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

Production must use the production frontend image tag and API hostname:

```hcl
environment    = "production"
api_image      = "docker.io/YOUR_DOCKERHUB_USERNAME/placeholder-store:backend-COMMIT_SHA"
frontend_image = "docker.io/YOUR_DOCKERHUB_USERNAME/placeholder-store:frontend-production-COMMIT_SHA"
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

The frontend images must be built with the matching API hostname embedded:

- Staging: `https://staging-api.placeholder-store.site`
- Production: `https://api.placeholder-store.site`

The CD workflow publishes separate frontend image tags for these builds.

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
  -ApiHealthUrl "https://staging-api.placeholder-store.site/health/ready" `
  -UptimeUrl "https://staging-monitor.placeholder-store.site"
```

Use the Production hostnames for a Production smoke test.

## State and secrets

Use separate remote Terraform state for Staging and Production. Do not commit
the real `.tfvars` files, Terraform state, generated plans, database passwords,
JWT secrets, or AWS credentials. Only `terraform.tfvars.example` is intended
to be committed.

The `.aws` task-definition JSON files are legacy configuration. Terraform
manages the active ECS task definitions, so do not deploy the legacy JSON files
unless the deployment process is intentionally changed later.
