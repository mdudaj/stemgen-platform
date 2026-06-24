# WhatsApp Evaluator Channel

## Purpose

WhatsApp is an optional secondary evaluator communication channel. It supports evaluator coordination but does not replace web review.

## Supported Uses

- invitation delivery;
- review link delivery;
- review reminders;
- acknowledgement capture;
- short comment capture if appropriate;
- status notifications;
- support/clarification messages.

## Integration Design

- Provider abstraction: hide provider-specific API details behind a local service interface.
- Message templates: versioned, reviewed, and approved before use.
- Webhook receiver: records provider delivery and inbound acknowledgement events.
- Message log: stores provider IDs, template IDs, delivery states, redacted payload hashes, and timestamps.
- Delivery status tracking: pending, sent, delivered, read, failed, opted_out.
- Review invitation link tokens: secure, expiring links to the web interface.
- Privacy constraints: minimal content; no sensitive data or full unpublished bundles.
- Failure fallback: email/web remains available when WhatsApp fails or opt-in is absent.

## Safety Rules

- Do not send sensitive participant data over WhatsApp.
- Do not send full unpublished artifact bundles over WhatsApp.
- Send secure review links instead.
- Require evaluator opt-in before WhatsApp use.
- Log provider message IDs and redacted payload hashes.
- Never store raw provider secrets in logs.
- Do not require WhatsApp credentials for local development, tests, or documentation milestones.
- Do not send live WhatsApp messages unless an explicit future implementation command requires it.

## Template Examples

Templates should include only:

- study/platform identity;
- evaluator task type;
- secure review link;
- due date or reminder text;
- support contact.

They should not include private artifact files, raw prompts, evaluator-sensitive details, or credentials.
