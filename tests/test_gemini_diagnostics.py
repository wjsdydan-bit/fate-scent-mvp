import asyncio
import os
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

os.environ["GEMINI_API_KEY"] = "fake_key"
import backend.main as main
from backend.main import _log_gemini_result

def test_missing_key(capsys):
    _log_gemini_result("test", Exception("missing_key"))
    captured = capsys.readouterr()
    assert "reason=unknown_error" in captured.out or "reason=missing_key" in captured.out

def test_authentication_error(capsys):
    _log_gemini_result("test", Exception("401 Unauthenticated"))
    captured = capsys.readouterr()
    assert "reason=authentication_error" in captured.out

def test_permission_error(capsys):
    _log_gemini_result("test", Exception("403 Permission denied"))
    captured = capsys.readouterr()
    assert "reason=permission_error" in captured.out

def test_rate_limit(capsys):
    _log_gemini_result("test", Exception("429 Too many requests"))
    captured = capsys.readouterr()
    assert "reason=rate_limit" in captured.out

def test_timeout(capsys):
    _log_gemini_result("test", asyncio.TimeoutError("timeout"))
    captured = capsys.readouterr()
    assert "reason=timeout" in captured.out

def test_invalid_json(capsys):
    _log_gemini_result("test", json.JSONDecodeError("Expecting value", "", 0))
    captured = capsys.readouterr()
    assert "reason=invalid_json" in captured.out

def test_success(capsys):
    _log_gemini_result("test", None)
    captured = capsys.readouterr()
    assert "reason=Gemini generation success" in captured.out

if __name__ == "__main__":
    pytest.main(["-v", __file__])
