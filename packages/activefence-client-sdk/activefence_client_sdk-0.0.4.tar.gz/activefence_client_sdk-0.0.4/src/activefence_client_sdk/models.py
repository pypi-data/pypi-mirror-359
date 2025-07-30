from dataclasses import dataclass


@dataclass(frozen=True)
class GuardedResult:
    blocked: bool
    reason: str
    final_response: str

@dataclass(frozen=True)
class AnalysisContext:
    session_id: str | None = None
    user_id: str | None = None
    provider: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    platform: str | None = None

@dataclass(frozen=True)
class CustomField:
    name: str
    value: str | int | float | bool | list[str]

    def __hash__(self) -> int:
        """Custom hash method that handles unhashable values by converting them to strings."""
        # Convert the value to a string representation for hashing
        # this is a workaround to handle unhashable values like lists and dicts
        value_str = str(self.value)
        return hash((self.name, value_str))

    def to_dict(self) -> dict[str, str | int | float | bool | list[str]]:
        return {self.name: self.value}
