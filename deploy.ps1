param(
    [string]$Namespace = "default",
    [string]$Manifest = "k8s-deploy.yml",
    [int]$LocalPort = 1111,
    [int]$ServicePort = 80
)

$ErrorActionPreference = "Stop"

Write-Host "Deploying to Kubernetes cluster..."

if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    throw "kubectl is not installed or not found in PATH."
}

if (-not (Test-Path $Manifest)) {
    throw "Manifest file not found: $Manifest"
}

kubectl apply -f $Manifest
kubectl rollout status deployment/diabetes-api -n $Namespace
kubectl wait --for=condition=Ready pod -l app=diabetes-api -n $Namespace --timeout=180s

Write-Host "Deployment summary:"
kubectl get deploy,po,svc,hpa,pdb -n $Namespace

Write-Host "Starting port-forward in background..."
$pf = Start-Process -FilePath "kubectl" -ArgumentList @(
    "port-forward",
    "svc/diabetes-api-service",
    "$LocalPort`:$ServicePort",
    "--address=0.0.0.0",
    "-n",
    $Namespace
) -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 4

$healthUrl = "http://localhost:$LocalPort/health"
try {
    $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
        Write-Host "API reachable at http://localhost:$LocalPort/docs"
        Start-Process "http://localhost:$LocalPort/docs"
    } else {
        throw "Health check failed with status code $($response.StatusCode)"
    }
}
catch {
    if ($pf -and -not $pf.HasExited) {
        Stop-Process -Id $pf.Id -Force
    }
    throw "API is not reachable after deployment: $($_.Exception.Message)"
}

Write-Host "Port-forward PID: $($pf.Id)"
Write-Host "To stop it later: Stop-Process -Id $($pf.Id) -Force"
