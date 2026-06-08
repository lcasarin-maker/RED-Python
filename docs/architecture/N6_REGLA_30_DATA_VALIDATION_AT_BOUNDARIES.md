# REGLA #30 — DATA VALIDATION AT BOUNDARIES

**Origen:** DEEPDIVE_DEPRECATED_FINDINGS.md (TIER 2 — Importantes)
**Adopción:** 2026-05-17 FASE 9 (enforcement tier 1 — prose-enforced)

---

## QUÉ ES

Validar **TODOS** los inputs en los límites del sistema (user input, API calls, file uploads, external data sources). Rechazar datos malformados en frontera, no adentro del código.

**Por qué:** El 70% de las vulnerabilidades (OWASP Top 10: injection, XXS, deserialization) ocurren porque sistemas asumen que inputs están "bien formados". Validar en frontera es defensa de primera línea.

---

## PRINCIPIOS

### 1. Frontera = Sistema Boundary
**Validar aquí:**
- ✅ User input (formularios, CLI args, API requests)
- ✅ File uploads (mimetype, size, content inspection)
- ✅ External API responses (schema mismatch, unexpected types)
- ✅ Environment variables (missing required, invalid values)
- ✅ Database queries (parameterized, no raw SQL)

**NO validar aquí (confía en código interno):**
- ❌ Entre funciones del mismo módulo
- ❌ Valores que ya pasaron validación frontera
- ❌ Estado interno (en memoria) sin fuentes externas

### 2. Validación DEBE ser exhaustiva
**No hacer:**
```python
# ❌ INCORRECTO: Asume email está bien formado
email = request.form.get('email')
user = User.create(email)  # Qué si email = None? SQL injection?
```

**Hacer:**
```python
# ✅ CORRECTO: Valida ANTES de usar
email = request.form.get('email', '').strip()
if not email or '@' not in email or len(email) > 255:
  raise ValueError(f"Invalid email: {email}")
user = User.create(email)  # Seguro, validado
```

### 3. Validación DEBE rechazar, no coercionar
**No hacer:**
```python
# ❌ INCORRECTO: Intenta "arreglarlo"
status = request.args.get('status', 'PENDING')
if status not in ['PENDING', 'DONE']:
  status = 'PENDING'  # Asume valor por defecto — silencia error
```

**Hacer:**
```python
# ✅ CORRECTO: Rechaza entrada inválida
status = request.args.get('status')
if status not in ['PENDING', 'DONE']:
  raise ValueError(f"Invalid status: {status}. Must be PENDING or DONE.")
```

---

## CHECKLIST: Qué Validar

### User Input (Forms, CLI)
- [ ] Presente (no None, no empty string)
- [ ] Tipo correcto (string, int, date, etc.)
- [ ] Longitud (min/max)
- [ ] Formato (email, URL, regex pattern)
- [ ] Valores permitidos (enum/whitelist, no blacklist)
- [ ] Encoding (UTF-8, no control characters)

**Ejemplo:**
```python
def validate_username(username):
  if not username:
    raise ValueError("Username required")
  if len(username) < 3 or len(username) > 50:
    raise ValueError(f"Username must be 3-50 chars, got {len(username)}")
  if not username.isalnum():
    raise ValueError(f"Username must be alphanumeric, got '{username}'")
  return username
```

### File Uploads
- [ ] Tipo MIME validado (no confiar en extensión)
- [ ] Tamaño dentro de límite
- [ ] Contenido inspeccionado (header bytes, no solo extensión)
- [ ] Nombre sanitizado (sin path traversal: ../, ~, etc.)
- [ ] Metadata extraída de forma segura

**Ejemplo:**
```python
ALLOWED_MIMES = ['image/png', 'image/jpeg']
MAX_SIZE = 5_000_000  # 5 MB

def validate_upload(file):
  if not file:
    raise ValueError("File required")
  if file.size > MAX_SIZE:
    raise ValueError(f"File too large: {file.size} > {MAX_SIZE}")
  if file.content_type not in ALLOWED_MIMES:
    raise ValueError(f"Invalid type: {file.content_type}")

  # Inspect first bytes (magic number)
  file.seek(0)
  header = file.read(4)
  if not is_valid_png_or_jpeg(header):
    raise ValueError("File content doesn't match MIME type")

  # Sanitize filename
  safe_name = secure_filename(file.filename)
  return safe_name
```

### External API Responses
- [ ] Status code esperado (200, 201, etc.)
- [ ] Schema válido (expected fields present)
- [ ] Tipos correctos (número vs string)
- [ ] Valores en rango esperado (no negativos si esperado positivo)
- [ ] Encoding correcto (no garbage characters)

**Ejemplo:**
```python
def call_external_api(user_id):
  response = requests.get(f"https://api.example.com/users/{user_id}")
  if response.status_code != 200:
    raise ValueError(f"API error: {response.status_code}")

  data = response.json()

  # Validate schema
  required = ['id', 'name', 'email']
  for field in required:
    if field not in data:
      raise ValueError(f"Missing field: {field}")

  # Validate types
  if not isinstance(data['id'], int):
    raise ValueError(f"Field 'id' must be int, got {type(data['id'])}")
  if not isinstance(data['email'], str):
    raise ValueError(f"Field 'email' must be string, got {type(data['email'])}")

  # Validate values
  if data['id'] < 0:
    raise ValueError(f"Field 'id' must be positive, got {data['id']}")
  if len(data['email']) > 255:
    raise ValueError(f"Field 'email' too long: {len(data['email'])}")

  return data
```

### Database Queries
- [ ] Usar parameterized queries (?, :param, etc.)
- [ ] NUNCA concatenar user input en SQL
- [ ] Validar tipos antes de query
- [ ] Limitar resultados (LIMIT clause)

**Ejemplo:**
```python
# ❌ VULNERABLE: SQL injection
def get_user(user_id):
  return db.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ SAFE: Parameterized
def get_user(user_id):
  if not isinstance(user_id, int) or user_id < 0:
    raise ValueError(f"Invalid user_id: {user_id}")
  return db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

---

## INTEGRACIÓN: Cuándo Validar

**En CLI:**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--email', required=True, type=str)
args = parser.parse_args()

# Validar args en frontera
if '@' not in args.email:
  raise ValueError(f"Invalid email: {args.email}")
```

**En API (Flask/FastAPI):**
```python
# FastAPI: Pydantic automáticamente valida
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  email: EmailStr  # Automáticamente validado
  name: str  # Non-empty
  age: int  # Must be int, optional pero validado si presente

@app.post("/users")
def create_user(user: UserCreate):
  # user ya está validado en frontera
  return user
```

**En archivo upload:**
```python
@app.post("/upload")
def upload_file(file: UploadFile):
  safe_name = validate_upload(file)  # Frontera
  save_file(file, safe_name)  # Código interno
```

---

## ENFORCEMENT: Pre-Commit Hook

**Locación:** `.git/hooks/pre-commit`

**Lógica:**
```bash
#!/bin/bash

# Detectar patrones de validación faltante
# 1. Uso de f-string en SQL (f"SELECT ... {var}")
# 2. form.get() sin validación posterior
# 3. json.loads() sin try-except
# 4. os.system() con variables sin sanitization

files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|go)$')

for file in $files; do
  # Check: f-strings in SQL
  if grep -E 'f"SELECT|f".*\{.*\}' "$file" | grep -q 'SELECT\|INSERT\|UPDATE'; then
    echo "WARNING: Potential SQL injection in $file (f-string in SQL)"
  fi

  # Check: json.loads() without try-except
  if grep -q 'json\.loads' "$file"; then
    if ! grep -B2 'json\.loads' "$file" | grep -q 'try:'; then
      echo "WARNING: json.loads without error handling in $file"
    fi
  fi
done

exit 0
```

---

## ESPÍRITU DE REGLA #30

✅ **Exhaustiva** — Validar TODOS los inputs en frontera
✅ **Rechazar no coercionar** — Malformed data → error, no default
✅ **En frontera** — No en código interno
✅ **Documentada** — Schema/validación rules claras
✅ **Testeable** — Casos de test: valid, invalid, edge cases

---

**Diferencia vs prácticas estándar:** La mayoría confía que "si llega acá, alguien ya lo validó". Nosotros validamos AQUÍ, en frontera, sin asumir.
