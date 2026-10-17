$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\terraform"
try {
    terraform fmt -check -recursive
    terraform init -backend=false
    terraform validate

    $example = Get-Content ".\terraform.tfvars.example" -Raw
    if ($example -notmatch 'environment\s+=\s+"(staging|production)"') {
        throw "terraform.tfvars.example must select staging or production."
    }
    if ($example -notmatch 'certificate_arn') {
        throw "terraform.tfvars.example must define an ACM certificate."
    }
}
finally {
    Pop-Location
}
