# Route Reference (API)

All routes are registered under the `main` Blueprint. The app renders server-side HTML — there is no JSON REST API. Routes that accept `POST` read from `request.form`.

---

## Authentication

### `GET /login`
Render the login form.

### `POST /login`
Authenticate a user.

**Form fields:**

| Field | Type | Required |
|-------|------|----------|
| `email` | string | Yes |
| `password` | string | Yes |

**Behaviour:**
- Rejects unapproved accounts with an info flash message.
- Redirects to `/setup-profile` if `profile_complete=False`.
- Redirects to `next` query param or `/` on success.

---

### `GET /register`
Render the registration form.

### `POST /register`
Create a new (unapproved) account.

**Form fields:**

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | Required, non-empty |
| `email` | string | Required, unique |
| `password` | string | Required, ≥ 8 chars |
| `confirm_password` | string | Must match `password` |

**Behaviour:**
New accounts have `approved=False`. They cannot log in until approved by admin.

---

### `GET /logout`
Log out the current user. Requires authentication.

---

## Profile

### `GET /profile`
View the current user's athlete profile. Requires authentication.

### `GET /setup-profile`
Render the profile setup form (first-login wizard). Requires authentication.

### `POST /setup-profile`
Save athlete physical data and HR zones. Requires authentication.

**Form fields:**

| Field | Type | Required |
|-------|------|----------|
| `age` | int | Yes |
| `sex` | `male` \| `female` | Yes |
| `weight` | float (kg) | Yes |
| `height` | float (cm) | Yes |
| `body_fat` | float (%) | No |
| `activity_level` | `sedentary` \| `light` \| `moderate` \| `very_active` | No |
| `training_phase` | `base` \| `build` \| `peak` \| `race` \| `recovery` | No |
| `hr_max`, `hr_zone1`–`hr_zone4` | int (bpm) | No |

---

## Dashboard

### `GET /`
Dashboard showing today's training sessions and daily nutrition summary. Requires authentication.

---

## Training

### `GET /training/log`
Render single-session logging form. Requires authentication.

### `POST /training/log`
Log one training session. Requires authentication.

**Form fields:**

| Field | Type | Notes |
|-------|------|-------|
| `date` | `YYYY-MM-DD` | Required |
| `sport` | string | `swim`, `bike`, `run`, `strength_core`, `strength_functional`, `strength_power`, `strength_mobility`, `strength_heavy` |
| `session_type` | `planned` \| `actual` | Required |
| `duration` | int (minutes) | Required |
| `zone1`–`zone5` | float (%) | Sum should be ~100 |
| `power` | int (watts) | Optional; enables power-based calculation for `bike` |
| `description` | string | Optional |

Redirects to `/nutrition/calculate?date=<date>` after saving.

---

### `GET /training/log-multi`
Render multi-session form (log an entire training day). Requires authentication.

### `POST /training/log-multi`
Log multiple sessions in one submission. Requires authentication.

Fields are numbered: `sport_1`, `zone1_1`, `sport_2`, `zone1_2`, etc.

---

## Nutrition

### `GET /nutrition/calculate`
Calculate and save nutrition targets for a given date. Requires authentication.

**Query parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `date` | today | `YYYY-MM-DD` |

Returns HTML page with TDEE breakdown, macro targets, and hydration goal.

---

## History

### `GET /history/training`
View all training sessions grouped by date (newest first). Requires authentication.

### `GET /history/nutrition`
View daily nutrition summaries (newest first). Requires authentication.

---

## Chat

### `GET /chat`
Render the AI coaching chat interface. Requires authentication.

### `POST /chat`
Send a message to Claude and receive a coaching response. Requires authentication.

**Form fields:**

| Field | Type |
|-------|------|
| `message` | string (user question) |

**Response:** Renders chat page with bot response inline. Rate-limited to 3 messages per user per day.

---

## Admin

All admin routes require `current_user.id == 1`.

### `GET /admin/pending-users`
View pending and approved users.

### `GET /admin/approve-user/<user_id>`
Approve a pending user. Sets `approved=True`, `approved_at`, `approved_by`.

### `GET /admin/reject-user/<user_id>`
Delete a pending user. Cannot delete the admin account itself.
