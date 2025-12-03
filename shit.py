import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from rnet import (
    Client,
    TlsOptions,
    TlsVersion,
    Http2Options,
    Http1Options,
    Method,
    ExtensionType,
    AlpnProtocol,
    SettingId,
    SettingsOrder,
    PseudoId,
    PseudoOrder,
    Priority,
    Priorities,
    StreamId,
    StreamDependency,
    Proxy,
    Response,
)


SAFARI_FINGERPRINT: Dict[str, Any] = {
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "ja4": "t13d2014h2_a09f3c656075_14788d8d241b",
    "ja4_r": "t13d2014h2_000a,002f,0035,009c,009d,1301,1302,1303,c008,c009,c00a,c012,c013,c014,c02b,c02c,c02f,c030,cca8,cca9_0005,000a,000b,000d,0012,0015,0017,001b,002b,002d,0033,ff01_0403,0804,0401,0503,0203,0805,0805,0501,0806,0601,0201",
    "ja4_o": "t13d2014h2_de3eb69493ac_65135c5c1a6b",
    "ja4_ro": "t13d2014h2_1301,1302,1303,c02c,c02b,cca9,c030,c02f,cca8,c00a,c009,c014,c013,009d,009c,0035,002f,c008,c012,000a_0000,0017,ff01,000a,000b,0010,0005,000d,0012,0033,002d,002b,001b,0015_0403,0804,0401,0503,0203,0805,0805,0501,0806,0601,0201",
    "ja3_hash": "773906b0efdefa24a7f2b8eb6985bf37",
    "ja3_text": "771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49162-49161-49172-49171-157-156-53-47-49160-49170-10,0-23-65281-10-11-16-5-13-18-51-45-43-27-21,29-23-24-25,0",
    "ja3n_hash": "44f7ed5185d22c92b96da72dbe68d307",
    "ja3n_text": "771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49162-49161-49172-49171-157-156-53-47-49160-49170-10,0-5-10-11-13-16-18-21-23-27-43-45-51-65281,29-23-24-25,0",
    "akamai_hash": "959a7e813b79b909a1a0b00a38e8bba3",
    "akamai_text": "2:0;4:4194304;3:100|10485760|0|m,s,p,a",
    "tls": {
        "ech": {"ech_success": False, "outer_sni": "tls.browserleaks.com"},
        "cipher_suite": {"id": 4865, "name": "TLS_AES_128_GCM_SHA256"},
        "key_exchange": {"id": 29, "name": "x25519"},
        "signature_algorithm": {"id": 1027, "name": "ecdsa_secp256r1_sha256"},
        "selected_version": {"id": 772, "name": "TLS 1.3"},
        "record_version": {"id": 769, "name": "TLS 1.0"},
        "handshake_version": {"id": 771, "name": "TLS 1.2"},
        "random": "dea04764907f7a116d0e7d54c184ceecbc3cce4e8956e2ff0cf8a46678293340",
        "session_id": "c35d77674c6fc27148cd093ab1d342a9e7e24e7892fb475def1de47f364d3ed6",
        "cipher_suites": [
            {"id": 64250, "name": "GREASE"},
            {"id": 4865, "name": "TLS_AES_128_GCM_SHA256"},
            {"id": 4866, "name": "TLS_AES_256_GCM_SHA384"},
            {"id": 4867, "name": "TLS_CHACHA20_POLY1305_SHA256"},
            {"id": 49196, "name": "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"},
            {"id": 49195, "name": "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"},
            {"id": 52393, "name": "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"},
            {"id": 49200, "name": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"},
            {"id": 49199, "name": "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"},
            {"id": 52392, "name": "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"},
            {"id": 49162, "name": "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA"},
            {"id": 49161, "name": "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA"},
            {"id": 49172, "name": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"},
            {"id": 49171, "name": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA"},
            {"id": 157, "name": "TLS_RSA_WITH_AES_256_GCM_SHA384"},
            {"id": 156, "name": "TLS_RSA_WITH_AES_128_GCM_SHA256"},
            {"id": 53, "name": "TLS_RSA_WITH_AES_256_CBC_SHA"},
            {"id": 47, "name": "TLS_RSA_WITH_AES_128_CBC_SHA"},
            {"id": 49160, "name": "TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA"},
            {"id": 49170, "name": "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA"},
            {"id": 10, "name": "TLS_RSA_WITH_3DES_EDE_CBC_SHA"},
        ],
        "extensions": [
            {"id": 31354, "name": "GREASE"},
            {
                "id": 0,
                "name": "server_name",
                "data": {"server_name": "tls.browserleaks.com"},
            },
            {"id": 23, "name": "extended_main_secret"},
            {"id": 65281, "name": "renegotiation_info"},
            {
                "id": 10,
                "name": "supported_groups",
                "data": {
                    "named_group_list": [
                        {"id": 27242, "name": "GREASE"},
                        {"id": 29, "name": "x25519"},
                        {"id": 23, "name": "secp256r1"},
                        {"id": 24, "name": "secp384r1"},
                        {"id": 25, "name": "secp521r1"},
                    ]
                },
            },
            {
                "id": 11,
                "name": "ec_point_formats",
                "data": {"ec_point_format_list": [{"id": 0, "name": "uncompressed"}]},
            },
            {
                "id": 16,
                "name": "application_layer_protocol_negotiation",
                "data": {"protocol_name_list": ["h2", "http/1.1"]},
            },
            {
                "id": 5,
                "name": "status_request",
                "data": {
                    "status_type": [{"id": 1, "name": "ocsp"}],
                    "responder_id_list": 0,
                    "request_extensions": 0,
                },
            },
            {
                "id": 13,
                "name": "signature_algorithms",
                "data": {
                    "supported_signature_algorithms": [
                        {"id": 1027, "name": "ecdsa_secp256r1_sha256"},
                        {"id": 2052, "name": "rsa_pss_rsae_sha256"},
                        {"id": 1025, "name": "rsa_pkcs1_sha256"},
                        {"id": 1283, "name": "ecdsa_secp384r1_sha384"},
                        {"id": 515, "name": "ecdsa_sha1"},
                        {"id": 2053, "name": "rsa_pss_rsae_sha384"},
                        {"id": 2053, "name": "rsa_pss_rsae_sha384"},
                        {"id": 1281, "name": "rsa_pkcs1_sha384"},
                        {"id": 2054, "name": "rsa_pss_rsae_sha512"},
                        {"id": 1537, "name": "rsa_pkcs1_sha512"},
                        {"id": 513, "name": "rsa_pkcs1_sha1"},
                    ]
                },
            },
            {"id": 18, "name": "signed_certificate_timestamp"},
            {
                "id": 51,
                "name": "key_share",
                "data": {
                    "client_shares": [
                        {"group": {"id": 27242, "name": "GREASE"}, "key_exchange_length": 1},
                        {"group": {"id": 29, "name": "x25519"}, "key_exchange_length": 32},
                    ]
                },
            },
            {"id": 45, "name": "psk_key_exchange_modes", "data": {"ke_modes": [{"id": 1, "name": "psk_dhe_ke"}]}},
            {
                "id": 43,
                "name": "supported_versions",
                "data": {
                    "versions": [
                        {"id": 35466, "name": "GREASE"},
                        {"id": 772, "name": "TLS 1.3"},
                        {"id": 771, "name": "TLS 1.2"},
                        {"id": 770, "name": "TLS 1.1"},
                        {"id": 769, "name": "TLS 1.0"},
                    ]
                },
            },
            {"id": 27, "name": "compress_certificate", "data": {"algorithms": [{"id": 1, "name": "zlib"}]}},
            {"id": 64250, "name": "GREASE"},
            {"id": 21, "name": "padding", "data": {"padding_data_length": 186}},
        ],
    },
    "http2": [
        {
            "id": 4,
            "name": "SETTINGS",
            "stream_id": 0,
            "length": 18,
            "settings": [
                {"id": 2, "name": "SETTINGS_ENABLE_PUSH", "value": 0},
                {"id": 4, "name": "SETTINGS_INITIAL_WINDOW_SIZE", "value": 4194304},
                {"id": 3, "name": "SETTINGS_MAX_CONCURRENT_STREAMS", "value": 100},
            ],
        },
        {"id": 8, "name": "WINDOW_UPDATE", "stream_id": 0, "length": 4, "window_size_increment": 10485760},
        {"id": 4, "name": "SETTINGS", "stream_id": 0, "length": 0, "flags_raw": 1, "flags": [{"id": 1, "name": "ACK"}]},
        {
            "id": 1,
            "name": "HEADERS",
            "stream_id": 1,
            "length": 249,
            "headers": {
                ":method": "GET",
                ":scheme": "https",
                ":path": "/",
                ":authority": "tls.browserleaks.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "sec-fetch-site": "none",
                "accept-encoding": "gzip, deflate, br",
                "sec-fetch-mode": "navigate",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
                "accept-language": "de-DE,de;q=0.9",
                "sec-fetch-dest": "document",
            },
            "flags_raw": 37,
            "flags": [
                {"id": 1, "name": "END_STREAM"},
                {"id": 4, "name": "END_HEADERS"},
                {"id": 32, "name": "PRIORITY"},
            ],
            "priority": {"weight": 255, "stream_dependency": 0, "exclusive": 0},
        },
    ],
}


@dataclass
class SafariTlsConfig:
    min_tls_version: TlsVersion = field(default_factory=lambda: TlsVersion.TLS_1_0)
    max_tls_version: TlsVersion = field(default_factory=lambda: TlsVersion.TLS_1_3)
    cipher_list: str = (
        "TLS_AES_128_GCM_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:"
        "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:"
        "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:"
        "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:"
        "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:"
        "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:"
        "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:"
        "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:"
        "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:"
        "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:"
        "TLS_RSA_WITH_AES_256_GCM_SHA384:"
        "TLS_RSA_WITH_AES_128_GCM_SHA256:"
        "TLS_RSA_WITH_AES_256_CBC_SHA:"
        "TLS_RSA_WITH_AES_128_CBC_SHA:"
        "TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA:"
        "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA:"
        "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
    )
    alpn_protocols: List[AlpnProtocol] = field(default_factory=lambda: [AlpnProtocol.HTTP2, AlpnProtocol.HTTP1])
    extension_permutation: List[ExtensionType] = field(
        default_factory=lambda: [
            ExtensionType.SERVER_NAME,
            ExtensionType.EXTENDED_MASTER_SECRET,
            ExtensionType.RENEGOTIATE,
            ExtensionType.SUPPORTED_GROUPS,
            ExtensionType.EC_POINT_FORMATS,
            ExtensionType.APPLICATION_LAYER_PROTOCOL_NEGOTIATION,
            ExtensionType.STATUS_REQUEST,
            ExtensionType.SIGNATURE_ALGORITHMS,
            ExtensionType.CERTIFICATE_TIMESTAMP,
            ExtensionType.KEY_SHARE,
            ExtensionType.PSK_KEY_EXCHANGE_MODES,
            ExtensionType.SUPPORTED_VERSIONS,
            ExtensionType.CERT_COMPRESSION,
            ExtensionType.PADDING,
        ]
    )
    signature_algorithms: List[int] = field(
        default_factory=lambda: [0x0403, 0x0804, 0x0401, 0x0503, 0x0203, 0x0805, 0x0805, 0x0501, 0x0806, 0x0601, 0x0201]
    )
    supported_groups: List[str] = field(default_factory=lambda: ["GREASE", "X25519", "secp256r1", "secp384r1", "secp521r1"])
    enable_grease: bool = True
    permute_extensions: bool = True
    enable_ech_grease: bool = False


@dataclass
class SafariHttp2Config:
    initial_stream_window_size: int = 4194304
    initial_connection_window_size: int = 10485760
    initial_stream_id: int = 1
    max_concurrent_streams: int = 100
    max_header_list_size: Optional[int] = None
    header_table_size: int = 4096
    enable_push: bool = False
    settings_order: SettingsOrder = field(
        default_factory=lambda: SettingsOrder(
            SettingId.ENABLE_PUSH,
            SettingId.INITIAL_WINDOW_SIZE,
            SettingId.MAX_CONCURRENT_STREAMS,
        )
    )
    pseudo_order: PseudoOrder = field(
        default_factory=lambda: PseudoOrder(
            PseudoId.METHOD,
            PseudoId.SCHEME,
            PseudoId.PATH,
            PseudoId.AUTHORITY,
        )
    )
    priorities: Optional[Priorities] = None


class RnetAsyncClient:
    def __init__(
        self,
        *,
        use_custom_safari_config: bool = True,
        tls_config: Optional[SafariTlsConfig] = None,
        http2_config: Optional[SafariHttp2Config] = None,
        user_agent: Optional[str] = None,
        timeout: Optional[float] = 30.0,
        allow_redirects: bool = True,
        max_redirects: int = 10,
        cookie_store: bool = True,
        verify: bool = True,
        proxies: Optional[List[Proxy]] = None,
        headers: Optional[Dict[str, str]] = None,
        http1_options: Optional[Http1Options] = None,
        referer: Optional[str] = None,
        **kwargs: Any,
    ):
        self.use_custom_safari_config = use_custom_safari_config
        self.tls_config = tls_config or SafariTlsConfig()
        self.http2_config = http2_config or SafariHttp2Config()
        self.user_agent = user_agent or SAFARI_FINGERPRINT["user_agent"]
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.max_redirects = max_redirects
        self.cookie_store = cookie_store
        self.verify = verify
        self.proxies = proxies or []
        self.default_headers = headers or {}
        self.http1_options = http1_options
        self.referer = referer
        self.extra_kwargs = kwargs
        self._client: Optional[Client] = None
        self._session_active = False

    def _create_tls_options(self) -> TlsOptions:
        cfg = self.tls_config
        return TlsOptions(
            min_tls_version=cfg.min_tls_version,
            max_tls_version=cfg.max_tls_version,
            cipher_list=cfg.cipher_list,
            alpn_protocols=cfg.alpn_protocols,
            extension_permutation=cfg.extension_permutation if cfg.permute_extensions else None,
            permute_extensions=cfg.permute_extensions,
            enable_grease=cfg.enable_grease,
            enable_ech_grease=cfg.enable_ech_grease,
        )

    def _create_http2_options(self) -> Http2Options:
        cfg = self.http2_config
        opts_kwargs: Dict[str, Any] = {
            "initial_stream_window_size": cfg.initial_stream_window_size,
            "initial_connection_window_size": cfg.initial_connection_window_size,
            "initial_stream_id": cfg.initial_stream_id,
            "max_concurrent_streams": cfg.max_concurrent_streams,
            "header_table_size": cfg.header_table_size,
            "enable_push": cfg.enable_push,
            "settings_order": cfg.settings_order,
            "pseudo_order": cfg.pseudo_order,
        }
        if cfg.max_header_list_size is not None:
            opts_kwargs["max_header_list_size"] = cfg.max_header_list_size
        if cfg.priorities is not None:
            opts_kwargs["priorities"] = cfg.priorities
        return Http2Options(**opts_kwargs)

    async def __aenter__(self) -> "RnetAsyncClient":
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def start_session(self) -> None:
        if self._session_active:
            return
        client_kwargs: Dict[str, Any] = {
            "user_agent": self.user_agent,
            "allow_redirects": self.allow_redirects,
            "max_redirects": self.max_redirects,
            "cookie_store": self.cookie_store,
            "verify": self.verify,
            "headers": self.default_headers,
            **self.extra_kwargs,
        }
        if self.timeout is not None:
            client_kwargs["timeout"] = int(self.timeout)
        if self.use_custom_safari_config:
            client_kwargs["tls_options"] = self._create_tls_options()
            client_kwargs["http2_options"] = self._create_http2_options()
        if self.http1_options:
            client_kwargs["http1_options"] = self.http1_options
        if self.proxies:
            client_kwargs["proxies"] = self.proxies
        if self.referer:
            if "headers" not in client_kwargs or client_kwargs["headers"] is None:
                client_kwargs["headers"] = {}
            client_kwargs["headers"]["Referer"] = self.referer
        self._client = Client(**client_kwargs)
        self._session_active = True

    async def close(self) -> None:
        if self._client:
            self._client = None
            self._session_active = False

    def _ensure_session(self) -> None:
        if not self._session_active or self._client is None:
            raise RuntimeError("Session not started. Use 'async with RnetAsyncClient() as client:' or call 'await client.start_session()' first.")

    async def get(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.get(url, **request_kwargs)

    async def post(
        self,
        url: str,
        *,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "json": json,
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        if isinstance(data, dict):
            request_kwargs["form"] = data
        elif data is not None:
            request_kwargs["body"] = data
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.post(url, **request_kwargs)

    async def put(
        self,
        url: str,
        *,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "json": json,
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        if isinstance(data, dict):
            request_kwargs["form"] = data
        elif data is not None:
            request_kwargs["body"] = data
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.put(url, **request_kwargs)

    async def delete(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.delete(url, **request_kwargs)

    async def head(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.head(url, **request_kwargs)

    async def patch(
        self,
        url: str,
        *,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "json": json,
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        if isinstance(data, dict):
            request_kwargs["form"] = data
        elif data is not None:
            request_kwargs["body"] = data
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.patch(url, **request_kwargs)

    async def options(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        proxy: Optional[Proxy] = None,
        **kwargs: Any,
    ) -> Response:
        self._ensure_session()
        request_kwargs: Dict[str, Any] = {
            "headers": headers,
            "cookies": cookies,
            **kwargs,
        }
        if params is not None:
            request_kwargs["query"] = params
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            request_kwargs["timeout"] = int(effective_timeout)
        if proxy:
            request_kwargs["proxy"] = proxy
        return await self._client.options(url, **request_kwargs)

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        self._ensure_session()
        try:
            method_enum = Method[method.upper()]
        except KeyError:
            raise ValueError(f"Unsupported HTTP method: {method}") from None
        return await self._client.request(method_enum, url, **kwargs)


async def example_usage() -> None:
    async with RnetAsyncClient() as client:
        response = await client.get("https://tls.peet.ws/api/all")
        print("Status:", response.status)
        print("Response:", await response.text())
    custom_tls = SafariTlsConfig(enable_grease=True, enable_ech_grease=False)
    custom_http2 = SafariHttp2Config(initial_stream_window_size=8388608, max_concurrent_streams=200)
    async with RnetAsyncClient(tls_config=custom_tls, http2_config=custom_http2, timeout=60.0, headers={"X-Custom-Header": "value"}) as client:
        response = await client.get("https://httpbin.org/get")
        data = await response.json()
        print("Custom config response:", data)
    async with RnetAsyncClient() as client:
        response = await client.post("https://httpbin.org/post", json={"key": "value", "test": "data"})
        print("POST response:", await response.json())
    client = RnetAsyncClient()
    await client.start_session()
    try:
        response = await client.get("https://httpbin.org/headers")
        print("Headers:", await response.json())
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
