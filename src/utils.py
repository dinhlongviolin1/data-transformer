from fastapi import Request


def get_db(request: Request):
    return request.app.state.db


def get_registry(request: Request):
    return request.app.state.registry
