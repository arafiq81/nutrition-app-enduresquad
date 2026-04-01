# Claude AI Integration

This document covers the design decisions, system prompt architecture, and usage patterns for the Anthropic Claude integration in the Ironman Nutrition Bot.

---

## Overview

The app uses the [Anthropic Python SDK](https://github.com/anthropic/anthropic-sdk-python) to power an on-demand nutrition coaching chatbot. Each message exchange is **stateless** (no multi-turn conversation history) but contextualised with the athlete's live data.

**Model in use:** `claude-sonnet-4-20250514`  
**Daily message limit:** 3 messages per user (configurable via `NutritionChatBot.DAILY_MESSAGE_LIMIT`)  
**Max tokens per response:** 1 000

---

## Rate Limiting

Rate limiting is enforced at the database level, not the API level:

```python
# chat.py — NutritionChatBot.check_rate_limit()
today_start = datetime.combine(date.today(), datetime.min.time())
messages_today = ChatMessage.query.filter(
    ChatMessage.user_id == self.user.id,
    ChatMessage.created_at >= today_start
).count()
```

Every successful exchange is persisted to the `chat_messages` table, including `tokens_used` for cost monitoring. The limit resets at midnight local server time.

To change the limit, update `DAILY_MESSAGE_LIMIT` in `app/chat.py` or expose it via `.env`:

```python
DAILY_MESSAGE_LIMIT = int(os.getenv('CHAT_DAILY_LIMIT', 3))
```

---

## System Prompt Design

The system prompt is built dynamically in `NutritionChatBot.get_system_prompt()`. It injects the athlete's live context so Claude can give personalised, data-driven advice without needing multi-turn memory.

### Structure

```
[Role definition]
ATHLETE PROFILE:        ← static physical data from User model
TODAY'S TRAINING:       ← real-time from TrainingSession query
TODAY'S NUTRITION TARGETS: ← real-time from DailyNutrition record
[Behavioural instructions]
```

### Current System Prompt Template

```
You are an expert Ironman triathlon nutrition coach. You provide personalised, actionable nutrition advice.

ATHLETE PROFILE:
- Name: {user.name}
- Age: {user.age}, Sex: {user.sex}
- Weight: {user.weight_kg}kg, Height: {user.height_cm}cm
[- Body Fat: {user.body_fat_percentage}%]         ← injected only if set
[- Lean Mass: {user.lean_body_mass_kg:.1f}kg]
- Training Phase: {user.training_phase}
- Activity Level: {user.activity_level}

TODAY'S TRAINING:
- {sport}: {duration} min, {energy} kcal, Load: {load}

TODAY'S NUTRITION TARGETS:
- Total Energy: {tdee} kcal
- Carbs: {carbs}g  |  Protein: {protein}g  |  Fat: {fat}g
- Hydration: {fluids}L
- Training Load: {load}

Your role:
- Provide specific, actionable nutrition advice
- Reference the athlete's actual data in your responses
- Keep responses concise (2–3 paragraphs max)
- Focus on practical meal/snack suggestions
- Consider training timing and demands
- Be encouraging and supportive
```

---

## Prompt Library

See [docs/prompt-library.md](docs/prompt-library.md) for a library of tested user-facing prompts and the expected coaching responses.

---

## Extending the Chatbot

### Adding conversation history (multi-turn)

To support multi-turn conversations, retrieve recent messages and pass them to the API:

```python
history = self.get_recent_messages(limit=5)
messages = []
for msg in reversed(history):
    messages.append({"role": "user",    "content": msg.user_message})
    messages.append({"role": "assistant", "content": msg.bot_response})
messages.append({"role": "user", "content": user_message})

response = self.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    system=self.get_system_prompt(),
    messages=messages
)
```

### Switching models

Change the model string in `chat.py`:

```python
response = self.client.messages.create(
    model="claude-opus-4-20250514",   # More capable, higher cost
    ...
)
```

Refer to the [Anthropic model docs](https://docs.anthropic.com/en/docs/about-claude/models) for available model IDs and pricing.

### Streaming responses

For a better UX with long answers, use `client.messages.stream()` and push chunks via Server-Sent Events:

```python
with self.client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    system=self.get_system_prompt(),
    messages=[{"role": "user", "content": user_message}]
) as stream:
    for text in stream.text_stream:
        yield text
```

---

## Cost Monitoring

Every API call records `tokens_used` in the `chat_messages` table. To query total usage:

```python
from app.models import ChatMessage
from sqlalchemy import func

total_tokens = db.session.query(func.sum(ChatMessage.tokens_used)).scalar()
```

Typical cost per message exchange with `claude-sonnet-4-20250514`:
- Input: ~500–800 tokens (system prompt + user message)
- Output: ~300–500 tokens
- Approximate cost: $0.003–0.008 per exchange (check current Anthropic pricing)

---

## Security Considerations

- The `ANTHROPIC_API_KEY` is loaded exclusively from environment variables via `python-dotenv`. It is never embedded in source code or templates.
- User messages are **not** sanitised for prompt injection before being sent to Claude. Consider adding input validation if the app is exposed to untrusted users.
- Bot responses are rendered with Jinja2's auto-escaping enabled — XSS from Claude output is mitigated at the template layer.
