import json

import pytest
from fastapi import HTTPException

from interfaces.api.middleware.error_handler import http_exception_handler


@pytest.mark.asyncio
async def test_http_exception_handler_preserves_structured_detail():
    detail = {
        "status": "failed",
        "message": "No verified data",
        "errors": {"source": "HTTP 404"},
    }

    response = await http_exception_handler(
        None,
        HTTPException(status_code=502, detail=detail),
    )
    body = json.loads(response.body)

    assert body["message"] == "No verified data"
    assert body["detail"] == detail
    assert body["details"] == detail


@pytest.mark.asyncio
async def test_http_exception_handler_keeps_string_detail_contract():
    response = await http_exception_handler(
        None,
        HTTPException(status_code=404, detail="Not found"),
    )
    body = json.loads(response.body)

    assert body["message"] == "Not found"
    assert body["detail"] == "Not found"
    assert body["details"] is None
