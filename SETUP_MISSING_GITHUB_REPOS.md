# 📦 Setup — Missing GitHub Repos

**Projects without a remote:** 2  
**Date:** 2026-06-02

---

## 1️⃣ Salary Calculator

### Step 1: Create the GitHub repo

```bash
# Option A: Web (GitHub UI)
# 1. Go to https://github.com/new
# 2. Name: calculadora-sueldos
# 3. Description: Payroll calculator suite (Excel: salaries, bonuses, severance, IMSS)
# 4. Visibility: Public
# 5. Do NOT initialize with a README
# 6. Create the repo

# Option B: CLI (gh)
gh repo create calculadora-sueldos \
  --public \
  --description "Payroll calculator suite (salaries, bonuses, severance, IMSS)" \
  --source=/d/AI/Calculadora\ de\ sueldos
```

### Step 2: Push the local branch

```bash
cd /d/AI/Calculadora\ de\ sueldos
git push -u origin master --no-verify
```

### Expected result
```
Total X objects, Y insertions, Z deletions
master -> master
branch 'master' set up to track 'origin/master'
✅ Salary calculator pushed
```

---

## 2️⃣ Homeopathy Kit

### Step 1: Create the GitHub repo

```bash
# Option A: Web (GitHub UI)
# 1. Go to https://github.com/new
# 2. Name: maletin-homeopatia
# 3. Description: Homeopathic remedy organization and planning system (catalog, treatments, tracking)
# 4. Visibility: Public
# 5. Do NOT initialize with a README
# 6. Create the repo

# Option B: CLI (gh)
gh repo create maletin-homeopatia \
  --public \
  --description "Homeopathic remedy organization and planning system (catalog, treatments, tracking)" \
  --source=/d/AI/Maletin\ Homeopatia
```

### Step 2: Push the local branch

```bash
cd /d/AI/Maletin\ Homeopatia
git push -u origin master --no-verify
```

### Expected result
```
Total X objects, Y insertions, Z deletions
master -> master
branch 'master' set up to track 'origin/master'
✅ Homeopathy kit pushed
```

---

## ✅ Final verification

Una vez creados ambos repos, ejecutar:

```bash
# Verify Salary Calculator
cd /d/AI/Calculadora\ de\ sueldos
git remote -v
# Should show:
# origin	https://github.com/lcasarin-maker/calculadora-sueldos.git (fetch)
# origin	https://github.com/lcasarin-maker/calculadora-sueldos.git (push)

# Verify Homeopathy Kit
cd /d/AI/Maletin\ Homeopatia
git remote -v
# Should show:
# origin	https://github.com/lcasarin-maker/maletin-homeopatia.git (fetch)
# origin	https://github.com/lcasarin-maker/maletin-homeopatia.git (push)
```

---

## 📋 Checklist

- [ ] Repo **calculadora-sueldos** created on GitHub
- [ ] Successful push of Salary Calculator
- [ ] Repo **maletin-homeopatia** created on GitHub
- [ ] Successful push of Homeopathy Kit
- [ ] Remote verification completed

---

**Once complete, all 17 projects will be on GitHub with Cycle 3 commits.**

*Instructions: 2026-06-02 | CoderCerberus v0.5*
