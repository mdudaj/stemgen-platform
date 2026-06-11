import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parent.parent
PATHS = [
    ROOT / "feature_list.json",
]

EXAMPLE_SCHEMA_MAP = {
    ROOT / "fixtures/examples/source_registry.example.json": ROOT / "schemas/curriculum/source_registry.schema.json",
    ROOT / "fixtures/examples/curriculum_snapshot_manifest.example.json": ROOT / "schemas/curriculum/curriculum_snapshot_manifest.schema.json",
    ROOT / "fixtures/examples/curriculum_item.example.json": ROOT / "schemas/curriculum/curriculum_item.schema.json",
    ROOT / "fixtures/examples/candidate_topic_review_distribution.example.json": ROOT / "schemas/curriculum/candidate_topic_review_distribution.schema.json",
    ROOT / "fixtures/examples/topic_selection_decisions.example.json": ROOT / "schemas/curriculum/topic_selection_decisions.schema.json",
    ROOT / "fixtures/examples/research_workflow_definition.example.json": ROOT / "schemas/workflows/research_workflow_definition.schema.json",
}


def main() -> None:
    for path in PATHS:
        load_json(path)
        print(f"valid json: {path.relative_to(ROOT)}")
    for schema_path in sorted((ROOT / "schemas").rglob("*.schema.json")):
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        print(f"valid schema: {schema_path.relative_to(ROOT)}")
    for example_path, schema_path in EXAMPLE_SCHEMA_MAP.items():
        instance = load_json(example_path)
        schema = load_json(schema_path)
        Draft202012Validator(schema).validate(instance)
        print(f"valid example: {example_path.relative_to(ROOT)} against {schema_path.relative_to(ROOT)}")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


if __name__ == "__main__":
    main()
