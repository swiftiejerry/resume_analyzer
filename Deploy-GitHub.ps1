param (
    [string]$RepoName = "resume_analyzer",
    [string]$Description = "AI Resume Analyzer"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 AI Resume Analyzer - GitHub Deploy Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will automate:"
Write-Host "1. Creating a public repository named $RepoName"
Write-Host "2. Configuring Git and committing code"
Write-Host "3. Pushing code and triggering GitHub Actions"
Write-Host ""
Write-Host "You need a GitHub Personal Access Token (Classic)."
Write-Host "Get it here: https://github.com/settings/tokens/new"
Write-Host "(Make sure to tick 'repo' and 'workflow' permissions)"
Write-Host ""

$username = Read-Host "Enter your GitHub Username"
$token = Read-Host "Enter your GitHub Token (starts with ghp_)"

if ([string]::IsNullOrWhiteSpace($username) -or [string]::IsNullOrWhiteSpace($token)) {
    Write-Host "Username or Token cannot be empty. Exiting." -ForegroundColor Red
    exit
}

# 1. Create GitHub Repo
Write-Host "`n[1/3] Creating GitHub Repository '$RepoName'..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "token $token"
    "Accept"        = "application/vnd.github.v3+json"
}
$body = @{
    name        = $RepoName
    description = $Description
    private     = $false
} | ConvertTo-Json

try {
    # Check if repo exists
    $checkUrl = "https://api.github.com/repos/$username/$RepoName"
    Invoke-RestMethod -Uri $checkUrl -Headers $headers -Method Get -ErrorAction Stop > $null
    Write-Host "Repository '$RepoName' already exists. Will push directly." -ForegroundColor Green
}
catch {
    # Create if not exists
    try {
        $createUrl = "https://api.github.com/user/repos"
        Invoke-RestMethod -Uri $createUrl -Headers $headers -Method Post -Body $body -ErrorAction Stop > $null
        Write-Host "Repository '$RepoName' created successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create repository. Check your Token permissions." -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit
    }
}

# 2. Configure and Commit Git
Write-Host "`n[2/3] Configuring local Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

# Configure git committer temp details if empty
$gitName = git config user.name
$gitEmail = git config user.email

if ([string]::IsNullOrWhiteSpace($gitName)) {
    git config user.name $username
}
if ([string]::IsNullOrWhiteSpace($gitEmail)) {
    git config user.email "$username@users.noreply.github.com"
}

git add .
$status = git status --porcelain
if (-not [string]::IsNullOrWhiteSpace($status)) {
    git commit -m "Initial deploy of AI Resume Analyzer"
    Write-Host "Code committed successfully." -ForegroundColor Green
}
else {
    Write-Host "No changes to commit." -ForegroundColor Green
}

# 3. Push to GitHub
Write-Host "`n[3/3] Pushing code to GitHub..." -ForegroundColor Yellow
$remoteUrl = "https://${username}:${token}@github.com/${username}/${RepoName}.git"

# Check remotes
$remotes = git remote
if ($remotes -contains "origin") {
    git remote set-url origin $remoteUrl
}
else {
    git remote add origin $remoteUrl
}

git push -u origin main --force

Write-Host "`nDeploy completed!" -ForegroundColor Green
Write-Host "Your frontend will be live at: https://${username}.github.io/${RepoName}/" -ForegroundColor Cyan
Write-Host "(Please wait 1-3 minutes for GitHub Actions to build the site)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next, deploy your backend API to Aliyun FC."
Write-Host "After that, update API_BASE in static/index.html and run this script again."
Write-Host ""
Read-Host "Press Enter to exit..."
