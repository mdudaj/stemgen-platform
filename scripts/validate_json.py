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
    ROOT / "fixtures/examples/curriculum_item_dataset.example.json": ROOT / "schemas/curriculum/curriculum_item_dataset.schema.json",
    ROOT / "fixtures/examples/candidate_topic_dataset.example.json": ROOT / "schemas/curriculum/candidate_topic_dataset.schema.json",
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
    for artifact_path, schema_path in snapshot_artifact_schema_pairs():
        instance = load_json(artifact_path)
        schema = load_json(schema_path)
        Draft202012Validator(schema).validate(instance)
        print(f"valid snapshot artifact: {artifact_path.relative_to(ROOT)} against {schema_path.relative_to(ROOT)}")
    for artifact_path, schema_path in extraction_artifact_schema_pairs():
        instance = load_json(artifact_path)
        schema = load_json(schema_path)
        Draft202012Validator(schema).validate(instance)
        print(f"valid extraction artifact: {artifact_path.relative_to(ROOT)} against {schema_path.relative_to(ROOT)}")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def snapshot_artifact_schema_pairs():
    snapshot_root = ROOT / "artifacts/curriculum-snapshots"
    if not snapshot_root.exists():
        return []
    schema_map = {
        "source_registry.json": ROOT / "schemas/curriculum/source_registry.schema.json",
        "fetch_manifest.json": ROOT / "schemas/curriculum/fetch_manifest.schema.json",
        "curriculum_snapshot_manifest.json": ROOT / "schemas/curriculum/curriculum_snapshot_manifest.schema.json",
    }
    pairs = []
    for snapshot_dir in sorted(path for path in snapshot_root.iterdir() if path.is_dir()):
        for artifact_name, schema_path in schema_map.items():
            artifact_path = snapshot_dir / artifact_name
            if artifact_path.exists():
                pairs.append((artifact_path, schema_path))
    return pairs


def extraction_artifact_schema_pairs():
    extraction_root = ROOT / "artifacts/curriculum-extractions"
    if not extraction_root.exists():
        return []
    schema_map = {
        "curriculum_items.json": ROOT / "schemas/curriculum/curriculum_item_dataset.schema.json",
        "candidate_topics.json": ROOT / "schemas/curriculum/candidate_topic_dataset.schema.json",
    }
    pairs = []
    for extraction_dir in sorted(path for path in extraction_root.iterdir() if path.is_dir()):
        for artifact_name, schema_path in schema_map.items():
            artifact_path = extraction_dir / artifact_name
            if artifact_path.exists():
                pairs.append((artifact_path, schema_path))
    return pairs


if __name__ == "__main__":
    main()
