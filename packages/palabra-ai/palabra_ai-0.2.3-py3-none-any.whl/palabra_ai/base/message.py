import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Union

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from palabra_ai.exc import ApiError, ApiValidationError
from palabra_ai.lang import Language
from palabra_ai.util.logger import debug


class KnownRawType(StrEnum):
    null = "null"
    binary = "binary"
    string = "string"
    json = "json"
    unknown = "unknown"


@dataclass
class KnownRaw:
    type: KnownRawType
    data: str | bytes | dict | None
    exc: Exception | None = None


class Message(BaseModel):
    """Base class for all message types"""

    type_: "Message.Type" = Field(alias="message_type")
    _known_raw: KnownRaw | None = PrivateAttr(default=None)

    class Type(StrEnum):
        PARTIAL_TRANSCRIPTION = "partial_transcription"
        TRANSLATED_TRANSCRIPTION = "translated_transcription"
        VALIDATED_TRANSCRIPTION = "validated_transcription"
        PARTIAL_TRANSLATED_TRANSCRIPTION = "partial_translated_transcription"
        PIPELINE_TIMINGS = "pipeline_timings"
        ERROR = "error"  # For error messages
        _QUEUE_LEVEL = "queue_level"
        _EMPTY = "empty"  # For empty {} messages
        _UNKNOWN = "unknown"  # For unrecognized message formats

    TRANSCRIPTION_TYPES: ClassVar[set[Type]] = {
        Type.PARTIAL_TRANSCRIPTION,
        Type.TRANSLATED_TRANSCRIPTION,
        Type.VALIDATED_TRANSCRIPTION,
        Type.PARTIAL_TRANSLATED_TRANSCRIPTION,
    }

    IN_PROCESS_TYPES: ClassVar[set[Type]] = TRANSCRIPTION_TYPES

    ALLOWED_TYPES: ClassVar[set[Type]] = {Type.PIPELINE_TIMINGS} | TRANSCRIPTION_TYPES

    STR_TRANSCRIPTION_TYPES: ClassVar[set[str]] = {
        mt.value for mt in TRANSCRIPTION_TYPES
    }

    @classmethod
    def get_transcription_message_types(cls) -> set["Message.Type"]:
        """Get set of all transcription message types"""
        return {
            Message.Type.PARTIAL_TRANSCRIPTION,
            Message.Type.TRANSLATED_TRANSCRIPTION,
            Message.Type.VALIDATED_TRANSCRIPTION,
            Message.Type.PARTIAL_TRANSLATED_TRANSCRIPTION,
        }

    @classmethod
    def get_allowed_message_types(cls) -> set["Message.Type"]:
        return {Message.Type.PIPELINE_TIMINGS} | cls.get_transcription_message_types()

    @classmethod
    def from_detected(
        cls, known_raw: KnownRaw
    ) -> Union[
        "EmptyMessage",
        "QueueStatusMessage",
        "PipelineTimingsMessage",
        "TranscriptionMessage",
        "UnknownMessage",
        "ErrorMessage",
    ]:
        """Factory method to create appropriate message type using pattern matching"""
        data = known_raw.data
        try:
            # Parse nested JSON in 'data' field if present
            if (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], str)
            ):
                try:
                    data["data"] = json.loads(data["data"])
                except json.JSONDecodeError:
                    debug("Failed to decode nested JSON in 'data' field")

            match data:
                # Empty message first - exactly empty dict
                case dict() if len(data) == 0:
                    return EmptyMessage.create(known_raw)

                # TranscriptionMessage messages
                case {"message_type": msg_type, "data": {"transcription": _}} if (
                    msg_type in cls.STR_TRANSCRIPTION_TYPES
                ):
                    return TranscriptionMessage.create(known_raw)

                # Error
                case {"message_type": Message.Type.ERROR.value, "data": _}:
                    return ErrorMessage.create(known_raw)

                # Pipeline timings
                case {"message_type": Message.Type.PIPELINE_TIMINGS.value, "data": _}:
                    return PipelineTimingsMessage.create(known_raw)

                # Queue status: non-empty dict without message_type
                case dict() as d if d and "message_type" not in d and len(d) == 1:
                    [(lang, val)] = d.items()
                    match val:
                        case {
                            "current_queue_level_ms": int() as current,  # noqa: F841
                            "max_queue_level_ms": int() as max_,  # noqa: F841
                        } if len(val) == 2:
                            return QueueStatusMessage.create(known_raw)
                        case _:
                            debug(
                                f"Invalid queue status format. Expected {{current_queue_level_ms: int, max_queue_level_ms: int}}. Got: {val}"
                            )
                            return UnknownMessage.create(known_raw)

                # Unknown format
                case _:
                    debug(f"Unknown message format: {known_raw}")
                    return UnknownMessage.create(known_raw)

        except Exception as e:
            debug(f"Failed to parse message: {e}. Data: {known_raw}")
            return UnknownMessage.create(known_raw)

    @classmethod
    def create(cls, known_raw: KnownRaw) -> "Message":
        """Create a message instance from KnownRaw"""
        obj = cls.model_validate(known_raw.data)
        obj._known_raw = known_raw
        return obj

    @classmethod
    def detect(cls, raw_msg: str | bytes | None) -> KnownRaw:
        match raw_msg:
            case None:
                return KnownRaw(KnownRawType.null, None)

            case bytes() as b if b.startswith(b"{") and b.endswith(b"}"):
                try:
                    return KnownRaw(KnownRawType.json, json.loads(b.decode("utf-8")))
                except Exception as e:
                    return KnownRaw(KnownRawType.binary, b, e)

            case str() as s if s.startswith("{") and s.endswith("}"):
                try:
                    return KnownRaw(KnownRawType.json, json.loads(s))
                except Exception as e:
                    return KnownRaw(KnownRawType.string, s, e)

            case _:
                return KnownRaw(KnownRawType.unknown, raw_msg)
        return KnownRaw(KnownRawType.unknown, raw_msg)

    @classmethod
    def decode(cls, raw_msg: str | bytes | None) -> "Message":
        # debug(raw_msg)
        known_msg = cls.detect(raw_msg)
        # debug(known_msg)
        if known_msg.type == KnownRawType.json:
            return cls.from_detected(known_msg)
        else:
            return UnknownMessage.create(known_msg)


class EmptyMessage(Message):
    """Empty message"""

    type_: Message.Type = Field(default=Message.Type._EMPTY, alias="message_type")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        return {}

    def __str__(self) -> str:
        return "⚪"


class QueueStatusMessage(Message):
    """Queue status message with language-specific queue data"""

    type_: Message.Type = Field(default=Message.Type._QUEUE_LEVEL, alias="message_type")
    language: Language
    current_queue_level_ms: int
    max_queue_level_ms: int

    def model_dump(self, **kwargs) -> dict[str, Any]:
        return {
            self.language.code: {
                "current_queue_level_ms": self.current_queue_level_ms,
                "max_queue_level_ms": self.max_queue_level_ms,
            }
        }

    @classmethod
    def create(cls, known_raw: KnownRaw) -> "QueueStatusMessage":
        """Create QueueStatusMessage from KnownRaw with proper data conversion"""
        if not isinstance(known_raw.data, dict):
            raise ValueError("QueueStatusMessage requires a dictionary data format")

        lang_code, queue_data = next(iter(known_raw.data.items()))
        obj = cls.model_validate(
            {
                "language": Language.get_or_create(lang_code),
                "current_queue_level_ms": queue_data["current_queue_level_ms"],
                "max_queue_level_ms": queue_data["max_queue_level_ms"],
            }
        )
        obj._known_raw = known_raw
        return obj

    def __str__(self) -> str:
        return (
            f"📊[{self.language.code}]: "
            f"cur={self.current_queue_level_ms}ms, "
            f"max={self.max_queue_level_ms}ms"
        )


class ErrorMessage(Message):
    raw: Any
    data: dict
    _exc: ApiError | None = PrivateAttr(default=None)

    @classmethod
    def create(cls, known_raw: KnownRaw) -> "ErrorMessage":
        """Create ErrorMessage from KnownRaw with proper data conversion"""
        obj = cls(
            message_type=Message.Type.ERROR, raw=known_raw, data={"raw": known_raw}
        )
        obj._known_raw = known_raw
        match known_raw.data:
            case {"data": {"code": "VALIDATION_ERROR", "desc": desc}}:
                obj._exc = ApiValidationError(str(desc))
                obj.data = known_raw.data
            case _:
                obj._exc = ApiError(str(known_raw.data))
                print(f"Not a dict: {type(known_raw).__name__}")
        return obj

    def raise_(self):
        raise self._exc or ApiError("Unknown error occurred")


class UnknownMessage(Message):
    """Unknown/unrecognized message format"""

    raw_type: KnownRawType
    raw_data: str | dict | None  # Already processed data
    error_info: dict[str, Any] | None = None

    @classmethod
    def create(cls, known_raw: KnownRaw) -> "UnknownMessage":
        """Create UnknownMessage from KnownRaw with proper data conversion"""
        # Handle bytes data
        data = known_raw.data
        if isinstance(data, bytes):
            try:
                # Try to decode as UTF-8 string first
                data = data.decode("utf-8")
            except UnicodeDecodeError:
                # If fails, encode as hex
                data = data.hex()

        # Handle exception
        error_info = None
        if known_raw.exc is not None:
            error_info = {
                "type": type(known_raw.exc).__name__,
                "message": str(known_raw.exc),
                "args": known_raw.exc.args,
            }

        obj = cls(
            message_type=Message.Type._UNKNOWN,
            raw_type=known_raw.type,
            raw_data=data,
            error_info=error_info,
        )
        obj._known_raw = known_raw
        return obj

    def model_dump(self, **kwargs) -> Any:
        return self.raw_data

    def __str__(self) -> str:
        return f"⚠️[{self.raw_type},{len(self.raw_data)}]: {str(self.raw_data)[:100]}{self.error_info}"


class PipelineTimingsMessage(Message):
    """Pipeline timing information"""

    type_: Message.Type = Message.Type.PIPELINE_TIMINGS
    transcription_id: str
    timings: dict[str, float]

    @model_validator(mode="before")
    @classmethod
    def extract_from_nested(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "data" in values and "message_type" in values:
            data = values["data"]
            return {
                "message_type": values["message_type"],
                "transcription_id": data["transcription_id"],
                "timings": data["timings"],
            }
        return values

    def model_dump(self, **kwargs) -> dict[str, Any]:
        return {
            "message_type": self.type_.value,
            "data": {
                "transcription_id": self.transcription_id,
                "timings": self.timings,
            },
        }


class TranscriptionSegment(BaseModel):
    text: str
    start: float
    end: float
    start_timestamp: float
    end_timestamp: float | None = None


class TranscriptionMessage(Message):
    """Transcription message"""

    type_: Message.Type = Field(alias="message_type")
    id_: str = Field(alias="transcription_id")
    text: str
    language: Language
    segments: list[TranscriptionSegment]

    model_config = ConfigDict(populate_by_name=True)

    @property
    def dedup(self) -> str:
        """Deduplication key for this message"""
        return f"{self.id_} {repr(self)}"

    @model_validator(mode="before")
    @classmethod
    def extract_from_nested(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Extract data from nested API structure"""
        if "data" in values and "message_type" in values:
            # Extract transcription data
            transcription = values["data"]["transcription"]
            # Convert language string to Language object
            lang_code = transcription["language"]
            return {
                "message_type": values["message_type"],
                "transcription_id": transcription["transcription_id"],
                "language": Language.get_or_create(lang_code),
                "segments": transcription["segments"],
                "text": transcription["text"],
            }
        return values

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Dump to nested API format"""
        segments_data = [seg.model_dump() for seg in self.segments]

        return {
            "message_type": self.type_.value,
            "data": {
                "transcription": {
                    "transcription_id": self.id_,
                    "language": self.language.code,
                    "text": self.text,
                    "segments": segments_data,
                }
            },
        }

    def __repr__(self) -> str:
        return f"{self.language.flag}{self.language.code} [{self.type_}]: {self.text}"

    def __str__(self) -> str:
        return self.text
