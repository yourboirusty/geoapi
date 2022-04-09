from encodings.utf_8 import encode
import pytest
from .utils import AsyncMock
from authentication.middleware import JWTAuthMiddleware


@pytest.mark.asyncio
async def test_auth_middleware_valid_token(
    db, mocker, geodata_user, geodata_user_token_pair
):
    mock_app = AsyncMock()
    middleware = JWTAuthMiddleware(app=mock_app)
    scope = {"query_string": encode(f"token={geodata_user_token_pair[1]}")[0]}
    result = await middleware(scope, None, None)
    user = mock_app.call_args.args[0].get("user")
    assert user
    assert user["slug"] == geodata_user.slug


@pytest.mark.asyncio
async def test_auth_middleware_invalid_token(db, mocker):
    mock_app = AsyncMock()
    middleware = JWTAuthMiddleware(app=mock_app)
    scope = {"query_string": encode("token=invalid")[0]}
    result = await middleware(scope, None, None)
    user = mock_app.call_args.args[0].get("user")
    assert not user
