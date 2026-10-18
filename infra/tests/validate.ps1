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
    if ($example -notmatch 'frontend_host') {
        throw "terraform.tfvars.example must define the frontend host."
    }
}
finally {
    Pop-Location
}
