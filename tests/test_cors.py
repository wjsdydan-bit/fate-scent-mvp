import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def parse_cors_origins(env_value: str) -> list[str]:
    if not env_value:
        return ["http://localhost:3000", "https://perfumance-kappa.vercel.app"]
    
    origins = [url.strip() for url in env_value.split(",") if url.strip()]
    if not origins:
        return ["http://localhost:3000", "https://perfumance-kappa.vercel.app"]
    return origins

def test_cors_parsing_empty():
    assert parse_cors_origins("") == ["http://localhost:3000", "https://perfumance-kappa.vercel.app"]

def test_cors_parsing_spaces():
    env_val = "  http://localhost:3000 , https://perfumance-kappa.vercel.app  ,  "
    assert parse_cors_origins(env_val) == ["http://localhost:3000", "https://perfumance-kappa.vercel.app"]

def test_cors_parsing_single():
    env_val = "https://perfumance-kappa.vercel.app"
    assert parse_cors_origins(env_val) == ["https://perfumance-kappa.vercel.app"]

def test_cors_parsing_wildcard():
    env_val = "*"
    assert parse_cors_origins(env_val) == ["*"]
