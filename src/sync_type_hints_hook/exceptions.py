# Copyright (c) 2025-2026 Benjamin Mummery

"""Exceptions raised by the sync-type-hints hook."""


class TypeClashError(Exception):
    """Raised when docstring and signature type information disagree."""

    def __init__(
        self,
        file: str,
        qualified_name: str,
        parameter: str,
        docstring_type: str,
        signature_type: str,
    ) -> None:
        self.file = file
        self.qualified_name = qualified_name
        self.parameter = parameter
        self.docstring_type = docstring_type
        self.signature_type = signature_type
        super().__init__(
            f"{file}: {qualified_name}: type clash for '{parameter}': "
            f"docstring has '{docstring_type}', signature has '{signature_type}'",
        )
