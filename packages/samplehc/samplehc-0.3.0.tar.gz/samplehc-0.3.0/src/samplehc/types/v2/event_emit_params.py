# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EventEmitParams"]


class EventEmitParams(TypedDict, total=False):
    name: Required[str]
    """The name of the event to create."""

    payload: object
    """The payload data for the event."""
