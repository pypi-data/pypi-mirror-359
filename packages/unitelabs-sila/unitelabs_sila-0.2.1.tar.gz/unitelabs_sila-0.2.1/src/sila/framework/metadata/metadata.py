import collections.abc
import dataclasses
import functools
import weakref

import typing_extensions as typing

from ..data_types import Any, Convertable, Native
from ..errors import InvalidMetadata
from ..fdl import Serializable
from ..identifiers import MetadataIdentifier
from ..protobuf import ConversionError, DecodeError, Message
from ..validators import check_display_name, check_identifier

if typing.TYPE_CHECKING:
    from ..common import Feature, Handler
    from ..data_types import DataType
    from ..errors import DefinedExecutionError
    from ..fdl import Deserializer, Serializer

T = typing.TypeVar("T", bound=Native)


@dataclasses.dataclass
class Metadata(Message, Serializable, Convertable[T], typing.Generic[T]):
    """Aditional information the server expects to receive from a client."""

    identifier: typing.ClassVar[str] = ""
    display_name: typing.ClassVar[str] = ""
    description: typing.ClassVar[str] = ""
    data_type: typing.ClassVar[type["DataType"]] = Any
    errors: typing.ClassVar[dict[str, type["DefinedExecutionError"]]] = {}
    affects: typing.ClassVar[collections.abc.Sequence[str]] = []
    feature: typing.ClassVar[typing.Optional["Feature"]] = None

    value: "DataType" = dataclasses.field(default_factory=Any)

    @classmethod
    async def from_buffer(
        cls, context: "Handler", metadata: typing.Optional[dict[str, bytes]] = None, /
    ) -> typing.Self:
        """
        Convert a native Python value to its corresponding SiLA data type.

        Args:
          context: The context in which the conversion is performed.
          metadata: The received metadata dictionary.

        Returns:
          An instance of the corresponding SiLA metadata.

        Raises:
          ConversionError: If the provided native value cannot be
            converted to the SiLA metadata.
        """

        assert context.feature

        metadata = metadata or {}
        rpc_header = cls.rpc_header()

        if rpc_header not in metadata or not (metadatum := metadata[rpc_header]):
            msg = f"Missing matadata '{cls.identifier}' in {context.__class__.__name__} '{context.identifier}'."
            raise InvalidMetadata(msg)

        try:
            return cls.decode(metadatum)
        except DecodeError as error:
            msg = (
                f"Unable to decode matadata '{cls.identifier}' in "
                f"{context.__class__.__name__} '{context.identifier}': {error.message}"
            )
            raise InvalidMetadata(msg) from None

    @typing.override
    async def to_native(self, context: "Handler", /) -> T:
        assert context.feature

        try:
            return await self.value.to_native(context.feature.context)
        except ConversionError as error:
            msg = (
                f"Unable to decode matadata '{self.identifier}' in "
                f"{context.__class__.__name__} '{context.identifier}': {error.message}"
            )
            raise InvalidMetadata(msg) from None

    @classmethod
    @functools.cache
    def fully_qualified_identifier(cls) -> MetadataIdentifier:
        """Uniquely identifies the metadata."""

        if cls.feature is None:
            msg = (
                f"Unable to access fully qualified identifier of unregistered Metadata "
                f"'{cls.identifier}'. Add it to a feature first."
            )
            raise RuntimeError(msg)

        return MetadataIdentifier.create(**cls.feature.fully_qualified_identifier._data, metadata=cls.identifier)

    @classmethod
    @functools.cache
    def rpc_header(cls) -> str:
        """Get the gRPC header specifier used to identify metadata."""

        return f"sila-{cls.fully_qualified_identifier().lower().replace('/', '-')}-bin"

    @typing.override
    @classmethod
    def serialize(cls, serializer: "Serializer") -> None:
        serializer.start_element("Metadata")
        serializer.write_str("Identifier", cls.identifier)
        serializer.write_str("DisplayName", cls.display_name)
        serializer.write_str("Description", cls.description)
        cls.data_type.serialize(serializer)
        if cls.errors:
            serializer.start_element("DefinedExecutionErrors")
            for Error in cls.errors.values():
                serializer.write_str("Identifier", Error.identifier)
            serializer.end_element("DefinedExecutionErrors")
        serializer.end_element("Metadata")

    @typing.override
    @classmethod
    def deserialize(cls, deserializer: "Deserializer") -> collections.abc.Generator[None, typing.Any, typing.Self]: ...

    @classmethod
    def add_to_feature(cls, feature: "Feature") -> type[typing.Self]:
        """
        Register this metadata with a feature.

        Args:
          feature: The feature to add this metadata to.

        Returns:
          The class, allowing for method chaining.
        """

        cls.feature = weakref.proxy(feature)
        feature.metadata[cls.identifier] = cls

        return cls

    @classmethod
    def create(
        cls,
        identifier: str,
        display_name: str,
        description: str = "",
        data_type: type["DataType"] = Any,
        errors: typing.Optional[collections.abc.Mapping[str, type["DefinedExecutionError"]]] = None,
        affects: typing.Optional[collections.abc.Sequence[str]] = None,
        feature: typing.Optional["Feature"] = None,
        **kwargs,
    ) -> type[typing.Self]:
        """
        Create a new SiLA `Custom` class with the provided data type.

        Args:
          identifier: Uniquely identifies the custom data type within the
            scope of the same feature.
          display_name: Human readable name of the custom data type.
          description: Describes the use and purpose of the custom data
            type.
          data_type: The SiLA data type for the custom value.
          errors: A list of defined execution errors that can happen when
            accessing this handler.
          affects: A list of handlers affected by this metadata.
          feature: The feature custom data type is assigned to.
          name: An optional name for the new `Custom` class.

        Returns:
          A new `Custom` class with the specified data type.
        """

        check_identifier(identifier)
        check_display_name(display_name)

        metadata: type[typing.Self] = dataclasses.make_dataclass(
            identifier or cls.__name__,
            [("value", data_type, dataclasses.field(default_factory=data_type))],
            bases=(cls,),
            namespace={
                "__doc__": description,
                "identifier": identifier,
                "display_name": display_name,
                "description": description,
                "data_type": data_type,
                "errors": dict(errors or {}),
                "affects": list(affects or []),
                "feature": feature,
                **kwargs,
            },
            eq=False,
        )

        if feature is not None:
            metadata.add_to_feature(feature)

        return metadata

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Metadata):
            return NotImplemented

        return (
            self.identifier == other.identifier
            and self.display_name == other.display_name
            and self.description == other.description
            and self.data_type.__name__ == other.data_type.__name__
            and self.errors == other.errors
            and self.affects == other.affects
            and self.value == other.value
        )
