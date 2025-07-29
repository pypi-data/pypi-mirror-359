from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationInfoMessage(_message.Message):
    __slots__ = ("id", "name", "descriptions")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    descriptions: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., descriptions: _Optional[str] = ...) -> None: ...

class ConfigurationInfoMessages(_message.Message):
    __slots__ = ("configurations",)
    CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    configurations: _containers.RepeatedCompositeFieldContainer[ConfigurationInfoMessage]
    def __init__(self, configurations: _Optional[_Iterable[_Union[ConfigurationInfoMessage, _Mapping]]] = ...) -> None: ...
