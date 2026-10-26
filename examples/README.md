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
python examples/typed_string_usage.py
python examples/typed_int_usage.py
python examples/typed_float_usage.py
python examples/deferred_usage.py
python examples/deferred_ci_build.py
```

## Recommended usage

`deferred_usage.py` opts into deferred DTO/document construction and shows first
use, inherited configuration, and an explicit eager override.
`deferred_ci_build.py` builds an explicit list of application-owned models after
defining their references, so application CI can catch delayed schema errors.

Use `MutableDTO` for command/request objects that can be enriched or normalized before
a use case is executed.

Use `ImmutableDTO` for read models, API response DTOs, query results, and stable
application snapshots.

Use `BaseDocument` for normal persisted documents that need `created_at`,
`updated_at`, and `schema_version`.

Use `PersistentDocument` plus timestamp/version mixins when a document needs custom
metadata layout or a different timestamp precision.

The typed primitive examples place ordinary and constrained variants side by side:

- `typed_string_usage.py` uses `BaseTypedString` and
  `BaseConstrainedTypedString`.
- `typed_int_usage.py` uses `BaseTypedInt` and `BaseConstrainedTypedInt`.
- `typed_float_usage.py` uses `BaseTypedFloat` and `BaseConstrainedTypedFloat`.

All variants preserve their exact domain subtype inside validated DTOs and documents
and serialize to plain JSON scalar values.

Use `ArbitraryMutableDTO` only at runtime boundaries where the DTO must carry
objects that Pydantic cannot fully model as data, such as iterators, callbacks,
clients, transactions, framework objects, or adapters.
