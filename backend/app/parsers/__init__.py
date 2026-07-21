from app.parsers.ssh_auth import SSHAuthParser
from app.parsers.web_access import WebAccessParser
from app.parsers.firewall import FirewallParser
from app.parsers.base import BaseParser

PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "ssh_auth": SSHAuthParser,
    "web_access": WebAccessParser,
    "firewall": FirewallParser,
}


def get_parser(source_type: str) -> BaseParser:
    parser_cls = PARSER_REGISTRY.get(source_type)
    if not parser_cls:
        raise ValueError(
            f"Unsupported source_type '{source_type}'. "
            f"Supported: {list(PARSER_REGISTRY.keys())}"
        )
    return parser_cls()
