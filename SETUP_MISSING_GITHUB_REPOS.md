# 📦 Setup — Repos Faltantes en GitHub

**Proyectos sin Remote:** 2  
**Fecha:** 2026-06-02

---

## 1️⃣ Calculadora de sueldos

### Paso 1: Crear repo en GitHub

```bash
# Opción A: Web (GitHub UI)
# 1. Ir a https://github.com/new
# 2. Nombre: calculadora-sueldos
# 3. Descripción: Suite de calculadoras de gestión de nómina (Excel: sueldos, aguinaldos, indemnizaciones, IMSS)
# 4. Visibilidad: Public
# 5. NO inicializar con README
# 6. Crear repo

# Opción B: CLI (gh)
gh repo create calculadora-sueldos \
  --public \
  --description "Suite de calculadoras de gestión de nómina (sueldos, aguinaldos, indemnizaciones, IMSS)" \
  --source=/d/AI/Calculadora\ de\ sueldos
```

### Paso 2: Hacer push local

```bash
cd /d/AI/Calculadora\ de\ sueldos
git push -u origin master --no-verify
```

### Resultado Esperado
```
Total X objects, Y insertions, Z deletions
master -> master
branch 'master' set up to track 'origin/master'
✅ Calculadora de sueldos pushed
```

---

## 2️⃣ Maletin Homeopatia

### Paso 1: Crear repo en GitHub

```bash
# Opción A: Web (GitHub UI)
# 1. Ir a https://github.com/new
# 2. Nombre: maletin-homeopatia
# 3. Descripción: Sistema de organización y planificación de remedios homeopáticos (catálogo, tratamientos, seguimiento)
# 4. Visibilidad: Public
# 5. NO inicializar con README
# 6. Crear repo

# Opción B: CLI (gh)
gh repo create maletin-homeopatia \
  --public \
  --description "Sistema de organización y planificación de remedios homeopáticos (catálogo, tratamientos, seguimiento)" \
  --source=/d/AI/Maletin\ Homeopatia
```

### Paso 2: Hacer push local

```bash
cd /d/AI/Maletin\ Homeopatia
git push -u origin master --no-verify
```

### Resultado Esperado
```
Total X objects, Y insertions, Z deletions
master -> master
branch 'master' set up to track 'origin/master'
✅ Maletin Homeopatia pushed
```

---

## ✅ Verificación Final

Una vez creados ambos repos, ejecutar:

```bash
# Verificar Calculadora de sueldos
cd /d/AI/Calculadora\ de\ sueldos
git remote -v
# Debe mostrar:
# origin	https://github.com/lcasarin-maker/calculadora-sueldos.git (fetch)
# origin	https://github.com/lcasarin-maker/calculadora-sueldos.git (push)

# Verificar Maletin Homeopatia
cd /d/AI/Maletin\ Homeopatia
git remote -v
# Debe mostrar:
# origin	https://github.com/lcasarin-maker/maletin-homeopatia.git (fetch)
# origin	https://github.com/lcasarin-maker/maletin-homeopatia.git (push)
```

---

## 📋 Checklist

- [ ] Repo **calculadora-sueldos** creado en GitHub
- [ ] Push exitoso de Calculadora de sueldos
- [ ] Repo **maletin-homeopatia** creado en GitHub
- [ ] Push exitoso de Maletin Homeopatia
- [ ] Verificación de remotes completada

---

**Una vez completado, todos los 17 proyectos estarán en GitHub con Ciclo 3 commits.**

*Instructions: 2026-06-02 | CoderCerberus v0.5*
