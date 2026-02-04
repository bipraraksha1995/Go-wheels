# ⚡ Vulnerability Scanning - Quick Reference Card

## 🚀 ONE-TIME SETUP

### Windows
```powershell
scripts/setup-security-scanning.bat
```

### Linux/macOS
```bash
bash scripts/setup-security-scanning.sh
```

This installs everything and runs initial scans.

---

## 🔍 SCAN COMMANDS

### Quick Scan (All Tools)
```bash
pip-audit && safety check && bandit -r gowheels/
```

### Detailed Scan
```bash
pip-audit --verbose --format json > audit.json
safety check --full-report > safety-report.json
bandit -r gowheels/ -f json > bandit-report.json
```

### Auto-Fix Vulnerabilities
```bash
pip-audit --fix
pip freeze > requirements.txt
```

### Scan Specific Package
```bash
pip-audit --desc requests
bandit gowheels/views.py
```

---

## 📋 OUTPUT INTERPRETATION

### ✅ All Clear
```
Found 0 vulnerabilities in 16 packages
```

### ⚠️ Vulnerabilities Found
```
Name: requests
Version: 2.25.0
Fix Version: 2.31.0
ID: GHSA-7wfx-fcpm-jpf5
```

### 🔴 Critical (Update Now)
```
Severity: Critical | CVSS: 9.5
Action: Update within 24 hours
```

### 🟠 High (Update This Week)
```
Severity: High | CVSS: 8.2
Action: Update within 7 days
```

### 🟡 Medium (Plan Update)
```
Severity: Medium | CVSS: 5.8
Action: Update within 2-4 weeks
```

### 🟢 Low (Monitor)
```
Severity: Low | CVSS: 2.1
Action: Update within 30 days
```

---

## 🛠️ FIX VULNERABILITIES

### Step 1: Identify
```bash
pip-audit
```

### Step 2: Update
```bash
pip install --upgrade <package-name>
# Or specific version
pip install <package-name>==<version>
```

### Step 3: Save
```bash
pip freeze > requirements.txt
```

### Step 4: Verify
```bash
pip-audit
```

### Step 5: Commit
```bash
git add requirements.txt
git commit -m "Security: Fix vulnerabilities"
git push
```

---

## 🚫 IGNORE VULNERABILITY (Document It!)

### Add to pyproject.toml
```toml
[tool.pip-audit]
ignore = [
    "GHSA-xxxx-xxxx-xxxx",  # Reason: Not applicable to our use
]
```

### Document Decision
```bash
# Add to VULNERABILITY_EXCEPTIONS.md:
# Vulnerability: [Name]
# Reason: [Why we accept this risk]
# Accepted by: [Your name]
# Date: [Today]
# Review date: [90 days from now]
```

---

## 📦 GIT HOOKS (Automatic Checks)

### Install
```bash
pre-commit install
```

### Test
```bash
pre-commit run --all-files
```

### Now vulnerabilities checked automatically on commit!

---

## 🔄 GITHUB ACTIONS

### Triggers
- Push to main/develop
- Pull request
- Daily at 2 AM UTC

### View Results
1. Go to: Actions tab on GitHub
2. Click: security-scan workflow
3. See: All scan results
4. On PR: See check status

---

## 📊 REPORTS

### Location
```
reports/
  initial-pip-audit.json
  initial-safety.json
  initial-bandit.json
  pip-audit-YYYY-MM-DD.json
  safety-YYYY-MM-DD.json
```

### View
```bash
cat reports/initial-pip-audit.json
```

### Track
```bash
# Weekly
0 2 * * 1 pip-audit --format json > reports/weekly-$(date +%Y-%m-%d).json
```

---

## ⏱️ TYPICAL WORKFLOW

```
You: git commit -m "Fix bug"
     ↓
System: Runs pip-audit automatically
         ↓
         ✅ Pass → Commit succeeds
         ❌ Fail → Fix required
             ↓
         You: pip-audit --fix
         You: pip freeze > requirements.txt
         You: git add requirements.txt
         You: git commit -m "Fix"
             ↓ Success!
```

---

## 🆘 TROUBLESHOOTING

### "Hook not running on commit"
```bash
pre-commit uninstall
pre-commit install
```

### "Tool not installed"
```bash
pip install pip-audit safety bandit
```

### "GitHub Actions failing"
- Check: requirements.txt is valid
- Check: Dockerfile builds successfully
- Check: Python 3.12+ installed

### "False positive - not a real vulnerability"
```toml
[tool.pip-audit]
ignore = ["GHSA-xxxx-xxxx-xxxx"]  # Add vulnerability ID
```

---

## 📚 DOCUMENTATION

| File | Read This For |
|------|----------------|
| **VULNERABILITY_SCANNING_GUIDE.md** | All command options + tool details |
| **VULNERABILITY_REMEDIATION.md** | How to handle vulns + exceptions |
| **DEPENDENCY_SCANNING_SUMMARY.md** | Overview + setup |
| **This card** | Quick reference |

---

## 🎯 SEVERITY ACTION MATRIX

```
CVSS 9.0-10.0 (Critical) → Fix in 24-48 hours
CVSS 7.0-8.9  (High)     → Fix in 1 week
CVSS 4.0-6.9  (Medium)   → Fix in 2-4 weeks
CVSS 0.1-3.9  (Low)      → Fix in 30 days
```

---

## 💡 TIPS

✅ Run scans regularly (not just on push)
✅ Document exceptions with reasons
✅ Update tools monthly: `pip install --upgrade pip-audit safety bandit`
✅ Review GitHub advisories: https://github.com/advisories
✅ Check CVSS score: https://nvd.nist.gov/ - higher = more urgent

❌ Don't skip pre-commit hooks
❌ Don't commit with `--no-verify` (security bypass)
❌ Don't hardcode secrets or API keys
❌ Don't ignore all vulnerabilities
❌ Don't wait to fix critical vulnerabilities

---

## 📞 QUICK HELP

```bash
# List all available hooks
pre-commit run --all-files --list

# Update all tools
pip install --upgrade pip pip-audit safety bandit pre-commit

# Clear cache
pre-commit clean

# See full help
pip-audit --help
safety check --help
bandit --help
pre-commit --help
```

---

## Status

✅ All tools installed
✅ Pre-commit hooks active
✅ GitHub Actions running
✅ Reports being generated
✅ Your code is secure! 🔐

---

**Print this card and keep at your desk! 📋**

---

Last Updated: February 4, 2026
