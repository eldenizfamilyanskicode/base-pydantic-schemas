from base_typed_float import BaseConstrainedTypedFloat, BaseTypedFloat

from base_pydantic_schemas import BaseDocument, MutableDTO


class TemperatureCelsius(BaseTypedFloat):
    """Finite temperature measured in degrees Celsius."""


class CompletionRatio(BaseConstrainedTypedFloat):
    """Completion ratio in the inclusive range from zero to one."""

    ge = 0.0
    le = 1.0


class UpdateMeasurementCommand(MutableDTO):
    """Mutable command with branded and constrained float fields."""

    temperature_celsius: TemperatureCelsius
    completion_ratio: CompletionRatio


class MeasurementDocument(BaseDocument):
    """Persisted measurement with typed float fields."""

    temperature_celsius: TemperatureCelsius
    completion_ratio: CompletionRatio


def main() -> None:
    command: UpdateMeasurementCommand = UpdateMeasurementCommand.model_validate(
        {
            "temperature_celsius": 21.5,
            "completion_ratio": 0.75,
        },
    )

    command.completion_ratio = CompletionRatio(0.8)

    assert type(command.temperature_celsius) is TemperatureCelsius
    assert type(command.completion_ratio) is CompletionRatio

    document: MeasurementDocument = MeasurementDocument(
        temperature_celsius=command.temperature_celsius,
        completion_ratio=command.completion_ratio,
    )

    print(command.model_dump(mode="json"))
    print(document.model_dump(mode="json"))


if __name__ == "__main__":
    main()
