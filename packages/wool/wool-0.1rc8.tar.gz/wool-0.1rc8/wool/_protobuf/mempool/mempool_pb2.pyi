from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SessionResponse(_message.Message):
    __slots__ = ("session", "event")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    session: Session
    event: Event
    def __init__(self, session: _Optional[_Union[Session, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ...) -> None: ...

class AcquireRequest(_message.Message):
    __slots__ = ("reference", "session")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    reference: Reference
    session: Session
    def __init__(self, reference: _Optional[_Union[Reference, _Mapping]] = ..., session: _Optional[_Union[Session, _Mapping]] = ...) -> None: ...

class AcquireResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PutRequest(_message.Message):
    __slots__ = ("session", "mutable", "dump")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    MUTABLE_FIELD_NUMBER: _ClassVar[int]
    DUMP_FIELD_NUMBER: _ClassVar[int]
    session: Session
    mutable: bool
    dump: bytes
    def __init__(self, session: _Optional[_Union[Session, _Mapping]] = ..., mutable: bool = ..., dump: _Optional[bytes] = ...) -> None: ...

class PutResponse(_message.Message):
    __slots__ = ("reference",)
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    reference: Reference
    def __init__(self, reference: _Optional[_Union[Reference, _Mapping]] = ...) -> None: ...

class PostRequest(_message.Message):
    __slots__ = ("session", "reference", "dump")
    SESSION_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    DUMP_FIELD_NUMBER: _ClassVar[int]
    session: Session
    reference: Reference
    dump: bytes
    def __init__(self, session: _Optional[_Union[Session, _Mapping]] = ..., reference: _Optional[_Union[Reference, _Mapping]] = ..., dump: _Optional[bytes] = ...) -> None: ...

class PostResponse(_message.Message):
    __slots__ = ("updated",)
    UPDATED_FIELD_NUMBER: _ClassVar[int]
    updated: bool
    def __init__(self, updated: bool = ...) -> None: ...

class GetRequest(_message.Message):
    __slots__ = ("reference", "session")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    reference: Reference
    session: Session
    def __init__(self, reference: _Optional[_Union[Reference, _Mapping]] = ..., session: _Optional[_Union[Session, _Mapping]] = ...) -> None: ...

class GetResponse(_message.Message):
    __slots__ = ("dump",)
    DUMP_FIELD_NUMBER: _ClassVar[int]
    dump: bytes
    def __init__(self, dump: _Optional[bytes] = ...) -> None: ...

class ReleaseRequest(_message.Message):
    __slots__ = ("reference", "session")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SESSION_FIELD_NUMBER: _ClassVar[int]
    reference: Reference
    session: Session
    def __init__(self, reference: _Optional[_Union[Reference, _Mapping]] = ..., session: _Optional[_Union[Session, _Mapping]] = ...) -> None: ...

class ReleaseResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Reference(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Session(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("reference", "event_type")
    REFERENCE_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    reference: Reference
    event_type: str
    def __init__(self, reference: _Optional[_Union[Reference, _Mapping]] = ..., event_type: _Optional[str] = ...) -> None: ...
