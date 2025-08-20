from datetime import datetime, timedelta

from decouple import config
from jose import jwt

from applibry_api.domain.entities.user import User


def generate_token(data: User, expires_delta: timedelta, _type: str = "access"):
    encode = {
        "sub": data.username,
        "sid": str(data.id),
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow(),
        "type": _type,
    }
    return jwt.encode(encode, config("SECRET_KEY"), algorithm=config("ALGORITHM"))


def create_access_token(data: User):
    access_token_expires = timedelta(
        minutes=int(config("ACCESS_TOKEN_EXPIRES_IN_MINS"))
    )
    return generate_token(data, expires_delta=access_token_expires)


def create_refresh_token(data: User):
    refresh_token_expires = timedelta(
        minutes=int(config("REFRESH_TOKEN_EXPIRES_IN_MINS"))
    )
    return generate_token(data, expires_delta=refresh_token_expires, _type="refresh") 