# SPEC_FEATURES — Template para New Features (5-10 minutos)

**Cómo usar:** Rellena este template con tu feature, ejecuta:
```bash
python scripts/spec_executor.py SPEC_FEATURES.md
```

---

## Feature: [Nombre de la feature]

**Descripción (2-3 líneas):**
[Qué hace la feature y por qué es importante]

---

### Ubicación (dónde va)
```
Module: [module_name]
Directory: [src/path]
Related files: [archivo1.py, archivo2.py]
```

Ejemplo:
```
Module: auth
Directory: src/auth/
Related files: models.py, routes.py
```

---

### Requerimientos (qué construir)

- [ ] Requirement 1: Description
- [ ] Requirement 2: Description
- [ ] Requirement 3: Description

**Ejemplo (Dark Mode):**
- [ ] Add user preference field to User model (users table, dark_mode column)
- [ ] Create API endpoint: POST /api/preferences/theme (value: "light"/"dark")
- [ ] Create frontend toggle: Settings page → Theme dropdown
- [ ] Store preference in browser localStorage (client-side)
- [ ] Load preference on app startup (fetch from DB)
- [ ] Apply CSS classes: .dark-mode { background: #1a1a1a; color: #fff; }
- [ ] Persist across browser sessions and logout/login

---

### Restricciones (qué NO hacer)

- [Constraint 1]
- [Constraint 2]

**Ejemplo:**
- Cannot modify database primary schema (backward compatibility)
- Must work with existing auth system (no changes to login flow)
- CSS variables only (no hardcoded colors)
- No external theme libraries (pure CSS)

---

### Aceptación (Qué prueba que funciona)

- [x] Feature criterion 1
- [x] Feature criterion 2
- [x] Edge case 1
- [x] Performance metric

**Ejemplo (Dark Mode):**
- [x] User can toggle theme in Settings page
- [x] Theme persists across page reloads
- [x] All UI colors change (background, text, buttons)
- [x] Existing 15 tests pass (no regression)
- [x] New test: test_dark_mode_toggle() included
- [x] Performance: theme loads in <50ms on startup

---

### API / Database Changes (if any)

**Database:**
```sql
-- New column
ALTER TABLE users ADD COLUMN dark_mode BOOLEAN DEFAULT FALSE;

-- New endpoint
POST /api/preferences/theme
Body: { "theme": "light" | "dark" }
Response: { "success": true, "theme": "dark" }
```

---

### User Flow (optional, helps AI understand)

```
1. User logs in
2. App loads user preferences (dark_mode = true/false)
3. User clicks Settings
4. Settings page shows Theme dropdown (Light/Dark)
5. User selects "Dark"
6. POST /api/preferences/theme sent
7. CSS class .dark-mode applied
8. All colors flip instantly
9. Preference saved to DB + localStorage
10. Next login: theme remembered automatically
```

---

## NOTAS

- **Tiempo en SPEC:** 5-10 minutos
- **Tiempo AI ejecuta:** 5-10 minutos (design + code + tests)
- **Total ahorro:** 70% (vs manual 30-60 min)

---

## Ejemplo Real: User Notifications Feature

```markdown
## Feature: Real-time user notifications

Descripción: Users should receive notifications when important events happen (new message, property inquiry). Currently notifications only work on page refresh.

### Ubicación
Module: notifications
Directory: src/notifications/
Related: WebSocket handler, User model, API routes

### Requerimientos
- [ ] Add notification table to schema (id, user_id, type, message, is_read, created_at)
- [ ] Create WebSocket handler: /ws/notifications/{user_id}
- [ ] Frontend: Listen to WebSocket, update notification badge count
- [ ] New endpoint: GET /api/notifications?limit=20 (fetch unread)
- [ ] Mark as read: POST /api/notifications/{id}/read
- [ ] Notification types: message, inquiry, system (enum in DB)
- [ ] No external WebSocket library (use built-in websockets)

### Restricciones
- Cannot break existing REST API (keep all endpoints)
- No database schema breaking changes
- Must work with current auth system
- WebSocket auth via existing JWT tokens

### Aceptación
- [x] WebSocket connects when user logs in
- [x] Notification badge updates in <100ms
- [x] Unread count accurate (matches DB)
- [x] Mark-as-read persists across sessions
- [x] All 15 existing tests pass
- [x] New test: test_notification_websocket() included
- [x] Load test: 100 concurrent users, stable performance

### User Flow
1. User logs in
2. Frontend connects to /ws/notifications/{user_id}
3. Someone sends a message → DB insert → WebSocket push
4. Frontend receives notification event
5. Badge updates to "1 unread"
6. User clicks notification
7. Frontend sends POST /api/notifications/{id}/read
8. Badge updates to "0 unread"
9. Refresh page → same state (persistent)
```

---

## Tips

1. **User flow helps** → AI generates better code
2. **DB changes explicit** → no surprises
3. **Aceptación específica** → testing más fácil
4. **Restricciones claras** → AI respeta limitaciones
