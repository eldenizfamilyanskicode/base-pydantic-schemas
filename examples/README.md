# base-pydantic-schemas examples

These examples show common backend usage patterns.

## Run

```bash
python examples/mutable_dto_usage.py
python examples/immutable_dto_usage.py
python examples/base_document.py
python examples/custom_document.py
python examples/arbitrary_dto_usage.py
python examples/dependency_injection_usage.py
```

## Recommended usage

Use `MutableDTO` for command/request objects that can be enriched or normalized before
a use case is executed.

Use `ImmutableDTO` for read models, API response DTOs, query results, and stable
application snapshots.

Use `BaseDocument` for normal persisted documents that need `created_at`,
`updated_at`, and `schema_version`.

Use `PersistentDocument` plus timestamp/version mixins when a document needs custom
metadata layout or a different timestamp precision.

Use `ArbitraryMutableDTO` only at runtime boundaries where the DTO must carry
objects that Pydantic cannot fully model as data, such as iterators, callbacks,
clients, transactions, framework objects, or adapters.