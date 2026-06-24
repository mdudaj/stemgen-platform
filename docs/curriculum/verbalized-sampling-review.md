# Verbalized-Sampling-Inspired Review

## Purpose

This design adapts the idea from "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity" as an inference-time review pattern. Instead of asking a model for one best suitability judgment, the platform asks for a distribution of plausible judgments with rationales and uncertainty flags.

## Design Rule

Do not ask an LLM for one best curriculum judgment. Ask for a distribution of plausible judgments, rationales, and uncertainty flags.

## Review Artifact

`candidate_topic_review_distribution.json`:

```json
{
  "topic_id": "",
  "source_item_ids": [],
  "review_method": "verbalized_sampling",
  "provider": "",
  "model": "",
  "prompt_template_id": "",
  "input_hash": "",
  "source_snapshot_id": "",
  "judgments": [
    {
      "label": "highly_suitable",
      "probability": 0.0,
      "rationale": "",
      "criteria": {
        "process_or_sequence": 0.0,
        "change_over_time": 0.0,
        "cause_effect": 0.0,
        "visualizability": 0.0,
        "primary_level_fit": 0.0,
        "curriculum_alignment_risk": 0.0
      }
    }
  ],
  "uncertainty_flags": [],
  "human_review_required": true
}
```

## Suggested Labels

- `highly_suitable`
- `suitable_with_minor_review`
- `uncertain`
- `low_suitability`
- `reject_for_scope`

## Prompt Contract

The prompt should include deterministic source references and screened candidate data. It should explicitly forbid adding curriculum facts not present in the source. It should ask for multiple plausible judgments, probabilities that sum to 1.0, concise rationales, and uncertainty flags.

## Human Review Use

Human reviewers inspect the distribution, not just the top label. High entropy, close probabilities, or conflicting rationales should increase review attention. The artifact supports review triage but cannot accept or reject topics by itself.
