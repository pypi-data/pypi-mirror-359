from __future__ import annotations

import base64
import json
import sys
from abc import ABC, abstractmethod
from collections.abc import Mapping, MutableMapping, Sequence
from contextlib import AbstractAsyncContextManager
from dataclasses import asdict, dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Literal, Optional, TypedDict, Union, cast
from urllib.parse import urlsplit, urlunsplit

import aiohttp
from typing_extensions import NotRequired

JSON = Union[
    MutableMapping[str, "JSON"], Sequence["JSON"], str, int, float, bool, None
]


class JsonDoc(MutableMapping[str, JSON]):
    def __init__(self, doc):
        self._doc = doc

    def __delitem__(self, key):
        del self._doc[key]

    def __getitem__(self, key: str) -> JSON:
        return self._doc[key]

    def __iter__(self):
        return iter(self._doc)

    def __len__(self):
        return len(self._doc)

    def __repr__(self):
        return repr(self._doc)

    def __setitem__(self, key, value):
        self._doc[key] = value

    @property
    def underlying(self) -> MutableMapping[str, JSON]:
        return self._doc

    def int(self, key: str) -> int:
        value = self[key]
        if isinstance(value, int):
            return value
        raise KeyError()

    def str(self, key: str) -> str:
        value = self[key]
        if isinstance(value, str):
            return value
        raise KeyError()

    def float(self, key: str) -> float:
        value = self[key]
        if isinstance(value, float):
            return value
        raise KeyError()

    def bool(self, key: str) -> bool:
        value = self[key]
        if isinstance(value, bool):
            return value
        raise KeyError()

    def list(self, key: str) -> list[JSON]:
        value = self[key]
        if isinstance(value, list):
            return value
        raise KeyError()

    def dict(self, key: str) -> JsonDoc:
        value = self[key]
        if isinstance(value, dict):
            return JsonDoc(value)
        raise KeyError()

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        value = self.get(key, default)
        if value is None or isinstance(value, int):
            return value
        raise KeyError()

    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        value = self.get(key, default)
        if value is None or isinstance(value, str):
            return value
        raise KeyError()

    def get_float(
        self, key: str, default: Optional[float] = None
    ) -> Optional[float]:
        value = self.get(key, default)
        if value is None or isinstance(value, float):
            return value
        raise KeyError()

    def get_bool(
        self, key: str, default: Optional[bool] = None
    ) -> Optional[bool]:
        value = self.get(key, default)
        if value is None or isinstance(value, bool):
            return value
        raise KeyError()

    def get_list(
        self,
        key: str,
        default: Optional[list[JSON]] = None,
    ) -> Optional[list[JSON]]:
        value = self.get(key, default)
        if value is None or isinstance(value, list):
            return value
        raise KeyError()

    def get_dict(
        self,
        key: str,
        default: Optional[MutableMapping[str, JSON]] = None,
    ) -> Optional[JsonDoc]:
        value = self.get(key, default)
        if value is None or isinstance(value, dict):
            return JsonDoc(value)
        raise KeyError()


def mapping_to_JSON(d: Mapping[str, Any]) -> JSON:
    return cast(JSON, d)


class Status(Enum):
    CLOSED = "closed"
    OPENED = "opened"
    UNOPENED = "unopened"


def is_empty_or_none(*strs: str | int | None):
    return any(map(lambda s: s is None or (type(s) is str and s == ""), strs))


class _DummyConnector(aiohttp.BaseConnector):
    async def _create_connection(self, req, traces, timeout):  # pragma: nocover
        msg = "You must open the connection before using it"
        raise NotImplementedError(msg)


class Connection(AbstractAsyncContextManager):
    @abstractmethod
    async def close(self) -> Connection: ...

    @abstractmethod
    async def open(self) -> Connection: ...

    @abstractmethod
    def as_admin(self, username: str, password: str) -> AdminSession: ...

    @abstractmethod
    def with_login(
        self,
        username: str,
        password: str,
    ) -> AuthenticatedSession: ...

    @abstractmethod
    def with_token(self, token: str) -> AuthenticatedSession: ...


class connect(Connection):
    def __init__(self, url: str | None = None):
        if url is None:
            url = "http://localhost:5984"
        parts = urlsplit(url)
        if is_empty_or_none(parts.scheme, parts.hostname, parts.port):
            msg = f"{url} needs a scheme, host, and port"
            raise ValueError(msg)
        self._scheme = parts.scheme
        self._host = parts.hostname or ""
        self._port = parts.port
        self._connector = _DummyConnector()

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port or 5984

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def status(self) -> Status:
        if type(self._connector) is _DummyConnector:
            return Status.UNOPENED
        return Status.CLOSED if self._connector.closed else Status.OPENED

    @property
    def url(self) -> str:
        url_t = (self._scheme, f"{self._host}:{self._port}", "", "", "")
        return urlunsplit(url_t)

    def as_admin(self, username: str, password: str) -> AdminSession:
        return _AdminSession(username, password, self)

    async def close(self) -> connect:
        await self.__aexit__(None, None, None)
        return self

    async def open(self) -> connect:
        await self.__aenter__()
        return self

    def with_login(self, username: str, password: str) -> AuthenticatedSession:
        return _CredentialsSession(username, password, self)

    def with_token(self, token: str) -> AuthenticatedSession:
        return _BearerSession(token, self)

    async def __aenter__(self):
        if type(self._connector) is _DummyConnector:
            enable_cleanup_closed = False
            _, minor, micro, *_ = sys.version_info
            if (
                minor < 12
                or (minor == 12 and micro < 7)
                or (minor == 14 and micro == 0)
            ):
                enable_cleanup_closed = True
            self._connector = aiohttp.TCPConnector(
                enable_cleanup_closed=enable_cleanup_closed
            )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._connector is not None:
            await self._connector.close()


@dataclass(frozen=True)
class DocOptions:
    attachment_encoding: bool = False
    attachments: bool = False
    attachments_since: list[str] = field(default_factory=list)
    conflicts: bool = False
    deleted_conflicts: bool = False
    latest: bool = False
    local_sequence: bool = False
    metadata: bool = False
    revision_ids: bool = False
    revisions_info: bool = False

    def for_query(self):
        d = {
            "attachment_encoding": "att_encoding_info",
            "attachments_since": "atts_since",
            "local_sequence": "local_seq",
            "metadata": "meta",
            "revision_ids": "revs",
            "revisions_info": "revs_info",
        }
        return {d.get(k, k): v for k, v in asdict(self).items() if v}


@dataclass
class AttachmentMetadata:
    name: str
    content_type: str
    digest: str
    length: int
    revision: int
    encoded_length: Optional[int] = None
    encoding: Optional[str] = None


@dataclass
class RevisionMetadata:
    rev: str
    status: Optional[Literal["available", "missing", "deleted"]]


class _AttachmentMetadata(TypedDict):
    content_type: str
    digest: str
    encoded_length: NotRequired[int]
    encoding: NotRequired[str]
    length: int
    revpos: int


class _RevisionHistory(TypedDict):
    start: int
    ids: list[str]


class _RevisionWithStatus(TypedDict):
    rev: str
    status: Optional[Literal["available", "missing", "deleted"]]


class _CouchResponse(TypedDict):
    _id: str
    _rev: str
    _deleted: NotRequired[bool]
    _local_seq: NotRequired[int]
    _attachments: Mapping[str, _AttachmentMetadata]
    _revs_info: NotRequired[list[_RevisionWithStatus]]
    _revisions: NotRequired[_RevisionHistory]


@dataclass
class CouchViewRow:
    key: JSON
    value: JSON
    doc: Optional[RetrievedCouchDocument] = None
    id: Optional[str] = None

    @classmethod
    def from_json(cls, json: _CouchViewRow) -> CouchViewRow:
        return cls(
            id=json.get("id"),
            key=json["key"],
            value=json["value"],
            doc=RetrievedCouchDocument.from_json(json["doc"])
            if "doc" in json
            else None,
        )


@dataclass
class CouchViewResult:
    total_rows: Optional[int]
    offset: Optional[int]
    rows: list[CouchViewRow]
    update_sequence: Optional[str]

    @classmethod
    def from_json(cls, json: _CouchView) -> CouchViewResult:
        return cls(
            total_rows=json.get("total_rows"),
            offset=json.get("offset"),
            update_sequence=json.get("update_seq"),
            rows=[CouchViewRow.from_json(x) for x in json["rows"]],
        )


class _CouchViewRow(TypedDict):
    id: NotRequired[str]
    key: JSON
    value: JSON
    doc: NotRequired[JsonDoc]


class _CouchView(TypedDict):
    total_rows: int
    offset: int
    rows: list[_CouchViewRow]
    update_seq: NotRequired[str]


class _CouchReceipt(TypedDict):
    ok: bool
    id: str
    rev: str


@dataclass
class CouchReceipt:
    ok: bool
    id: str
    rev: str


@dataclass
class NewCouchDocument:
    id: str
    content: Mapping[str, JSON]


@dataclass
class ExistingCouchDocument:
    id: str
    revision: str
    content: JsonDoc

    @classmethod
    def from_doc(cls, doc: dict[str, Any]):
        return cls(
            id=doc["_id"],
            revision=doc["_rev"],
            content=JsonDoc(
                {k: v for k, v in doc.items() if not k.startswith("_")}
            ),
        )


@dataclass
class RetrievedCouchDocument(ExistingCouchDocument):
    deleted: bool
    attachment_metadata: Sequence[AttachmentMetadata]
    conflicts: Optional[list[str]]
    deleted_conflicts: Optional[list[str]]
    local_sequence: Optional[int]
    revisions: Optional[list[RevisionMetadata]]

    @classmethod
    def from_json(cls, json: Mapping[str, JSON]) -> RetrievedCouchDocument:
        meta = cast(_CouchResponse, json)
        attachment_metadata = []
        for key, value in meta.get("_attachments", {}).items():
            attachment_metadata.append(
                AttachmentMetadata(
                    name=key,
                    content_type=value["content_type"],
                    digest=value["digest"],
                    length=value["length"],
                    revision=value["revpos"],
                    encoded_length=value.get("encoded_length"),
                    encoding=value.get("encoding"),
                )
            )
        revisions = None
        if "_revs_info" in meta:
            revisions = [
                RevisionMetadata(**info) for info in meta.get("_revs_info", [])
            ]
        elif "_revisions" in meta:
            revs = meta.get("_revisions", {"start": -1, "ids": []})
            revisions = [
                RevisionMetadata(f"{revs['start'] - index}-{hash}", None)
                for index, hash in enumerate(revs["ids"])
            ]
        return cls(
            id=meta["_id"],
            revision=meta["_rev"],
            deleted=bool(meta.get("_deleted")),
            attachment_metadata=attachment_metadata,
            conflicts=meta.get("_conflicts"),
            deleted_conflicts=meta.get("_deleted_conflicts"),
            local_sequence=meta.get("_local_seq"),
            revisions=revisions,
            content=JsonDoc(
                {k: v for k, v in json.items() if not k.startswith("_")}
            ),
        )


class BulkGetSpec(TypedDict):
    id: str
    revision: str


@dataclass
class BulkGetResponse:
    found: list[RetrievedCouchDocument]
    deleted: list[BulkGetSpec]
    not_found: list[str | BulkGetSpec]


class Database(AbstractAsyncContextManager):
    @abstractmethod
    async def info(self) -> DatabaseInformation: ...

    @abstractmethod
    async def bulk_get_docs(
        self,
        *,
        ids: list[str] = [],
        ids_with_revs: list[BulkGetSpec] = [],
    ) -> BulkGetResponse: ...

    @abstractmethod
    async def create_doc(self, doc: NewCouchDocument) -> CouchReceipt: ...

    @abstractmethod
    async def delete_doc(self, id: str, rev: str) -> CouchReceipt: ...

    @abstractmethod
    async def get_doc(
        self,
        doc_id: str,
        rev: Optional[str] = None,
    ) -> RetrievedCouchDocument: ...

    @abstractmethod
    async def get_view(
        self,
        doc_name: str,
        view_name: str,
        *,
        descending: bool = False,
        key: Optional[JSON] = None,
        start_key: Optional[JSON] = None,
        end_key: Optional[JSON] = None,
        include_docs: bool = False,
        group_level: Optional[int] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> CouchViewResult: ...

    @abstractmethod
    async def update_doc(self, doc: ExistingCouchDocument) -> CouchReceipt: ...

    async def open(self):
        return await self.__aenter__()

    async def close(self):
        await self.__aexit__(None, None, None)

    @abstractmethod
    async def __aenter__(self) -> Database: ...


class AdminDatabase(Database):
    @abstractmethod
    async def get_design_doc(self, doc_name: str) -> RetrievedCouchDocument: ...


class _Database(Database):
    def __init__(self, name: str, session: Session):
        self._name = name
        self._session = session

    async def bulk_get_docs(
        self,
        *,
        ids: list[str] = [],
        ids_with_revs: list[BulkGetSpec] = [],
    ) -> BulkGetResponse:
        payload = [
            {"id": x["id"], "rev": x["revision"]} for x in ids_with_revs
        ] + [{"id": id} for id in ids]
        response = await self._session._post(
            f"{self._name}/_bulk_get",
            mapping_to_JSON({"docs": payload}),
        )
        result = await response.json()

        return BulkGetResponse(
            found=[
                RetrievedCouchDocument.from_json(doc.get("ok"))
                for o in result.get("results")
                for doc in o.get("docs", [])
                if "ok" in doc and "_deleted" not in doc["ok"]
            ],
            deleted=[
                BulkGetSpec(id=doc["ok"]["_id"], revision=doc["ok"]["_rev"])
                for o in result.get("results")
                for doc in o.get("docs", [])
                if "ok" in doc and "_deleted" in doc["ok"]
            ],
            not_found=[
                str(o.id)
                for o in result.get("results")
                for doc in o.get("docs", [])
                if "error" in doc
            ],
        )

    async def create_doc(self, doc: NewCouchDocument) -> CouchReceipt:
        response = await self._session._put(
            f"{self._name}/{doc.id}",
            mapping_to_JSON(doc.content),
        )
        return CouchReceipt(**await response.json())

    async def delete_doc(self, id: str, rev: str) -> CouchReceipt:
        response = await self._session._delete(f"{self._name}/{id}", rev)
        return CouchReceipt(**await response.json())

    async def get_doc(
        self,
        doc_id: str,
        rev: Optional[str] = None,
    ) -> RetrievedCouchDocument:
        path = f"{self._name}/{doc_id}"
        params = {}
        if rev is not None:
            params["rev"] = rev
        if len(params) == 0:
            params = None
        resp = await self._session._get(path, params)
        json = await resp.json()
        return RetrievedCouchDocument.from_json(json)

    async def get_view(
        self,
        doc_name: str,
        view_name: str,
        *,
        descending: bool = False,
        key: Optional[JSON] = None,
        start_key: Optional[JSON] = None,
        end_key: Optional[JSON] = None,
        include_docs: bool = False,
        group_level: Optional[int] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> CouchViewResult:
        params = {}
        if key is not None:
            params["key"] = key
        if start_key is not None:
            params["start_key"] = start_key
        if end_key is not None:
            params["end_key"] = end_key
        if include_docs is not None:
            params["include_docs"] = include_docs
        if descending:
            params["descending"] = descending
        if group_level is not None:
            params["group_level"] = group_level
        if limit is not None:
            params["limit"] = limit
        if skip is not None:
            params["skip"] = skip
        path = f"{self._name}/_design/{doc_name}/_view/{view_name}"
        resp = await self._session._get(path, params)
        json = await resp.json()
        return CouchViewResult.from_json(json)

    async def info(self) -> DatabaseInformation:
        resp = await self._session._get(self._name)
        json = await resp.json()

        return DatabaseInformation(
            disk_format_version=json["disk_format_version"],
            external_size=json["sizes"]["external"],
            file_size=json["sizes"]["file"],
            instance_start_time=json["instance_start_time"],
            internal_size=json["sizes"]["active"],
            is_compact_running=json["compact_running"],
            is_partitioned=bool(json["props"] and json["props"]["partitioned"]),
            name=json["db_name"],
            num_deleted_docs=json["doc_del_count"],
            num_docs=json["doc_count"],
            num_replicas=json["cluster"]["n"],
            num_shards=json["cluster"]["q"],
            purge_sequence=json["purge_seq"],
            read_quorum=json["cluster"]["r"],
            update_sequence=json["update_seq"],
            write_quorum=json["cluster"]["w"],
        )

    async def update_doc(self, doc: ExistingCouchDocument) -> CouchReceipt:
        response = await self._session._put(
            f"{self._name}/{doc.id}?rev={doc.revision}",
            doc.content.underlying,
        )
        return CouchReceipt(**await response.json())

    async def __aenter__(self):
        await self._session._head(self._name)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


def handle_generic_errors(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        response: aiohttp.ClientResponse = await func(*args, **kwargs)
        if response.status == 400:
            keys = await response.json() or {
                "error": "bad_request",
                "reason": "Your request was malformed.",
            }
            raise BadRequest(**keys)
        if response.status == 401:
            keys = await response.json() or {
                "error": "unauthorized",
                "reason": "You are not authorized to access this resource.",
            }
            raise UnauthorizedError(**keys)
        if response.status == 403:
            keys = await response.json() or {
                "error": "forbidden",
                "reason": "You are not allowed to access this resource.",
            }
            raise ForbiddenError(**keys)
        if response.status == 404:
            keys = await response.json() or {
                "error": "not_found",
                "reason": "That resource does not exist on the server.",
            }
            raise DoesNotExistError(**keys)
        if response.status == 409:
            keys = await response.json() or {
                "error": "conflict",
                "reason": "That update does not have a valid revision.",
            }
            raise ConflictError(**keys)
        return response

    return wrapped


class Session(AbstractAsyncContextManager):
    def __init__(self, cnx: connect, headers: dict[str, str] = {}):
        self._session = aiohttp.ClientSession(
            cnx.url,
            connector=cnx._connector,
            connector_owner=False,
            headers={
                aiohttp.hdrs.ACCEPT: "application/json",
            }
            | headers,
        )

    def db(self, name: str) -> Database:
        return _Database(name, self)

    async def open(self):
        await self.__aenter__()

    async def close(self):
        await self.__aexit__(None, None, None)

    @handle_generic_errors
    async def _delete(self, url: str, rev: str) -> aiohttp.ClientResponse:
        await self.open()
        return await self._session.delete(
            url,
            headers={aiohttp.hdrs.IF_MATCH: rev},
        )

    @handle_generic_errors
    async def _get(
        self,
        url: str,
        params: Optional[Mapping[str, JSON]] = None,
    ) -> aiohttp.ClientResponse:
        await self.open()
        if params is not None:
            params = {
                k: json.dumps(v) if k != "rev" else v for k, v in params.items()
            }
        return await self._session.get(url, params=params)

    @handle_generic_errors
    async def _head(self, url: str) -> aiohttp.ClientResponse:
        await self.open()
        return await self._session.head(url)

    @handle_generic_errors
    async def _post(self, url: str, json: JSON) -> aiohttp.ClientResponse:
        await self.open()
        return await self._session.post(url, json=json)

    @handle_generic_errors
    async def _put(self, url: str, json: JSON) -> aiohttp.ClientResponse:
        await self.open()
        return await self._session.put(url, json=json)

    @abstractmethod
    async def __aenter__(self) -> Session: ...

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.close()


class AdminSession(Session):
    @abstractmethod
    async def create_user(
        self,
        uid: str,
        password: str,
        roles: list[str],
        **properties: JSON,
    ) -> CouchReceipt: ...

    @abstractmethod
    async def delete_user(self, uid: str) -> CouchReceipt: ...

    @abstractmethod
    async def get_user(self, uid: str) -> ExistingCouchDocument: ...

    @abstractmethod
    async def __aenter__(self) -> AdminSession: ...


class AuthenticatedSession(Session, ABC):
    def user_db(self) -> Database:
        db_name = f"userdb-{self._username.encode().hex()}"
        return _Database(db_name, self)

    @property
    @abstractmethod
    def _username(self) -> str: ...


class _CredentialsSession(AuthenticatedSession):
    def __init__(self, username: str, password: str, cnx: connect):
        super().__init__(cnx)
        self._creds = {"name": username, "password": password}
        self._logged_in = False
        self._logging_in = False

    async def _login(self):
        if not self._logging_in:
            self._logging_in = True
            await self._post("_session", json=mapping_to_JSON(self._creds))
            self._logging_in = False
            self._logged_in = True
        return self

    @property
    def _username(self) -> str:
        return self._creds["name"]

    async def __aenter__(self):
        if not self._logged_in:
            return await self._login()
        return self


class _BearerSession(AuthenticatedSession):
    def __init__(self, jwt: str, cnx: connect):
        headers = {"Authorization": f"Bearer {jwt}"}
        super().__init__(cnx, headers)
        payloadB64Encoded = jwt.split(".")[1]
        payloadJsonEncoded = base64.b64decode(f"{payloadB64Encoded}==")
        payload = json.loads(payloadJsonEncoded)
        self._name = payload["sub"]
        self._logged_in = False
        self._logging_in = False

    @property
    def _username(self) -> str:
        return self._name

    async def __aenter__(self):
        if not self._logged_in and not self._logging_in:
            self._logging_in = True
            response = await self._get("_session")
            payload = await response.json()
            if payload["userCtx"]["name"] is None:
                await self.close()
                raise UnauthorizedError("unauthorized", "Token not recognized")
            self._logging_in = False
            self._logged_in = True
        return self


class _AdminSession(_CredentialsSession, AdminSession):
    async def create_user(
        self,
        uid: str,
        password: str,
        roles: list[str],
        **properties: JSON,
    ) -> CouchReceipt:
        url = f"_users/org.couchdb.user:{uid}"
        payload = {
            "name": uid,
            "password": password,
            "roles": roles,
            "type": "user",
        } | properties
        resp = await self._put(url, payload)
        json = cast(_CouchReceipt, await resp.json())
        return CouchReceipt(**json)

    async def delete_user(self, uid: str) -> CouchReceipt:
        url = f"_users/org.couchdb.user:{uid}"
        resp = await self._head(url)
        rev = resp.headers.get(aiohttp.hdrs.ETAG, "")

        resp = await self._delete(url, rev)
        json = cast(_CouchReceipt, await resp.json())
        return CouchReceipt(**json)

    async def get_user(self, uid: str) -> ExistingCouchDocument:
        url = f"_users/org.couchdb.user:{uid}"
        if uid.startswith("org.couchdb.user:"):
            url = f"_users/{uid}"
        resp = await self._get(url)
        json = await resp.json()
        return ExistingCouchDocument.from_doc(json)


@dataclass
class CouchDBError(Exception):
    error: str
    reason: str


@dataclass
class BadRequest(CouchDBError):
    pass


@dataclass
class ConflictError(CouchDBError):
    pass


@dataclass
class DoesNotExistError(CouchDBError):
    pass


@dataclass
class ForbiddenError(CouchDBError):
    pass


@dataclass
class UnauthorizedError(CouchDBError):
    pass


@dataclass
class DatabaseInformation:
    disk_format_version: int
    external_size: int
    file_size: int
    instance_start_time: str
    internal_size: int
    is_compact_running: bool
    is_partitioned: bool
    name: str
    num_deleted_docs: int
    num_docs: int
    num_replicas: int
    num_shards: int
    purge_sequence: str
    read_quorum: int
    update_sequence: str
    write_quorum: int


@dataclass
class Document:
    _id: str
    _rev: str


@dataclass
class UserInfo(Document):
    name: str
    roles: list[str]
    extra: JSON
