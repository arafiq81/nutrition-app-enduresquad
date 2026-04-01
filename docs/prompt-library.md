# Prompt Library

A curated set of user prompts that have been tested against the Ironman Nutrition Bot chatbot, along with notes on what context Claude needs and how responses should be evaluated.

The system prompt injects the athlete's profile, today's training, and today's TDEE targets before every message. See [claude.md](../claude.md) for the full system prompt specification.

---

## Pre-Workout Nutrition

### Prompt
> What should I eat 2 hours before my long ride tomorrow?

**Context required:** training phase, tomorrow's session type (if logged).  
**Expected elements in response:** specific carbohydrate amounts, timing advice, suggested foods, fluid recommendations.

---

### Prompt
> I have a 90-minute swim in 45 minutes. What can I eat right now?

**Context required:** weight (for portion sizing), today's TDEE, any logged sessions.  
**Expected elements:** low-fibre carb snack suggestions, portion sizes in grams, hydration reminder.

---

## Post-Workout Recovery

### Prompt
> I just finished a 3-hour brick session. My legs are cooked. What do I eat now?

**Context required:** today's training load score, total training kcal, protein target.  
**Expected elements:** 3:1 or 4:1 carb:protein ratio mention, recovery window (within 30–60 min), specific food examples.

---

### Prompt
> My training load today was really high and I feel depleted. Help me hit my carb targets tonight.

**Context required:** `daily_training_load_score`, `target_carbs_g`, `consumed_carbs_g` (if available).  
**Expected elements:** remaining carb deficit calculation, high-carb meal/snack ideas, timing.

---

## Race-Week Nutrition

### Prompt
> I'm 5 days out from Ironman. How should I adjust my eating this week?

**Context required:** `training_phase == 'race'`, current macro targets.  
**Expected elements:** carbohydrate loading protocol, sodium/electrolyte guidance, gut-training advice, race-morning meal recommendation.

---

### Prompt
> What should I eat on the bike during a long ride to maintain energy?

**Context required:** athlete weight, duration (from training session), training phase.  
**Expected elements:** 60–90 g/hr carb target, gel/chew/real food examples, sodium needs.

---

## General Coaching

### Prompt
> I've been feeling heavy during my runs. Could it be my diet?

**Context required:** training phase, macro targets, activity level.  
**Expected elements:** carbohydrate timing discussion, iron levels mention, hydration check, suggestion to track meals.

---

### Prompt
> My protein target is really high. Do I really need that much?

**Context required:** `target_protein_g`, athlete weight, training phase.  
**Expected elements:** explanation of 1.6–2.2 g/kg for endurance athletes, specifics tied to athlete's weight and target.

---

### Prompt
> What are the best foods to hit my fat targets without feeling heavy before training?

**Context required:** `target_fat_g`, training schedule timing.  
**Expected elements:** unsaturated fat sources, timing guidance (avoid high fat pre-workout), portion examples.

---

## Hydration

### Prompt
> My hydration target is really high today. How do I actually drink that much?

**Context required:** `target_fluids_ml`, today's training sessions (sport and duration).  
**Expected elements:** per-hour target breakdown, electrolyte inclusion, spread throughout the day.

---

## Evaluating Response Quality

Good responses should:

1. Reference the athlete's **actual numbers** (not generic advice).
2. Be **specific** about portions (grams or millilitres, not "a handful").
3. Stay within **2–3 paragraphs** (not essay-length).
4. Be **actionable** — the athlete can do something immediately.
5. Avoid disclaimers like "consult a dietitian" in every response (once is fine, not every time).

Red flags:
- Generic advice without any reference to the athlete's data
- Recommending supplements without mentioning food-first approach
- Calorie counts that contradict the calculated TDEE
