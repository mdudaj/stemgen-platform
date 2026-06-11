# Evaluator Channel Model

## Purpose

Evaluator communication should support web, email, and optional WhatsApp while preserving the web platform as the canonical evaluation interface.

## Channels

- `web`: canonical review interface.
- `email`: default invitation and fallback channel.
- `whatsapp`: optional secondary channel for invitations, reminders, acknowledgements, short comments, and support messages.

## Channel Fields

- `preferred_channel`
- `channel_status`
- `opt_in_status`
- `contact_address`
- `last_message_at`
- `delivery_status`

## Suggested Entities

| Entity | Purpose | Key fields |
| --- | --- | --- |
| EvaluatorContact | Stores contact methods and consent state. | evaluator_id, channel, contact_address, opt_in_status, verified_at. |
| EvaluationInvitation | Links evaluator, artifact set, review token, and due date. | invitation_id, evaluator_id, review_url_token, status, expires_at. |
| EvaluationChannelPreference | Stores preferred and fallback channels. | evaluator_id, preferred_channel, fallback_channel, updated_at. |
| WhatsAppMessageTemplate | Versioned message templates. | template_id, purpose, version, locale, approved_at. |
| WhatsAppMessageLog | Delivery and acknowledgement evidence. | message_id, provider_id, template_id, payload_hash, delivery_status. |
| WhatsAppWebhookEvent | Raw provider event envelope with redaction. | event_id, provider_id, event_type, received_at, payload_hash. |

## Canonical Record Rule

Review scores, final comments, artifact inspection, and submitted evaluation data must be recorded through the web platform. WhatsApp messages may link to or remind about the review; they do not replace the canonical review record.
