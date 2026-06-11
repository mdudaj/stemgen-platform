# Verification

## Current Baseline

```bash
./init.sh
python3 scripts/validate_json.py
```

`./init.sh` remains the baseline bootstrap gate. `python3 scripts/validate_json.py` is the offline schema and fixture validation gate.

## Schema Validation

The JSON validation command checks:

- JSON syntax for tracked JSON files
- JSON Schema Draft 2020-12 validity for `schemas/**/*.schema.json`
- curriculum source registry validation
- snapshot manifest validation
- curriculum item validation
- automated review distribution validation
- topic selection decision validation
- research workflow definition validation

The command must not require network access, live TIE downloads, live LLM calls, WhatsApp credentials, or generated evaluation data.

## Planned Future Checks

- workflow definition schema validation
- workflow manifest validation
- candidate topic dataset validation
- candidate topic review distribution validation
- topic selection decision validation
- evidence projection validation
- WhatsApp message-template validation
- push-safety verification

Live LLM calls, WhatsApp credentials, live WhatsApp messages, deployment, and live TIE downloads are not required for Milestone 22.5 verification.
