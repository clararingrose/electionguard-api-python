from typing import Any
from base64 import b64encode, b16decode
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from electionguard.serializable import write_json_object

from electionguard.group import rand_q

from app.api.v1.models.user import (
    CreateUserResponse,
    UserQueryRequest,
    UserQueryResponse,
)

from .auth import ScopedTo

from ..models import (
    AuthenticationCredential,
    UserInfo,
    UserScope,
)

from ....core import (
    AuthenticationContext,
    get_user_info,
    set_user_info,
    filter_user_info,
    get_auth_credential,
    set_auth_credential,
    update_auth_credential,
)

from ..tags import USER

router = APIRouter()


@router.post(
    "/find",
    response_model=UserQueryResponse,
    dependencies=[ScopedTo([UserScope.admin])],
    tags=[USER],
)
async def find_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    data: UserQueryRequest = Body(...),
) -> UserQueryResponse:
    """
    Find users.

    Search the repository for users that match the filter criteria specified in the request body.
    If no filter criteria is specified the API will return all users.
    """
    filter = write_json_object(data.filter) if data.filter else {}
    users = filter_user_info(filter, skip, limit, request.app.state.settings)
    return UserQueryResponse(users=users)


scoped_to_any = ScopedTo(
    [UserScope.admin, UserScope.auditor, UserScope.guardian, UserScope.voter]
)


@router.get(
    "/me",
    response_model=UserInfo,
    dependencies=[
        ScopedTo(
            [UserScope.admin, UserScope.auditor, UserScope.guardian, UserScope.voter]
        )
    ],
    tags=[USER],
)
async def me(
    request: Request, token_data: ScopedTo = Depends(scoped_to_any)
) -> UserInfo:
    """
    Get user info for the current logged in user.
    """

    if token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not specified"
        )

    current_user = get_user_info(token_data.username, request.app.state.settings)

    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


@router.put(
    "",
    response_model=CreateUserResponse,
    dependencies=[ScopedTo([UserScope.admin])],
    tags=[USER],
)
def create_user(
    request: Request,
    user_info: UserInfo = Body(...),
) -> CreateUserResponse:
    """Create a new user."""

    if any(
        filter_user_info(
            filter={"username": user_info.username},
            skip=0,
            limit=1,
            settings=request.app.state.settings,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    # TODO: generate passwords differently
    new_password = b64encode(b16decode(rand_q().to_hex()[0:16]))
    # new_password = b64encode(b16decode('password'))
    hashed_password = AuthenticationContext(
        request.app.state.settings
    ).get_password_hash(new_password)
    credential = AuthenticationCredential(
        username=user_info.username, hashed_password=hashed_password
    )

    # testing: enable user to input password
    # hashed_password = AuthenticationContext(
    #     request.app.state.settings
    # ).get_password_hash(user_info.password)
    # credential = AuthenticationCredential(
    #     username=user_info.username, hashed_password=hashed_password
    # )

    set_auth_credential(credential, request.app.state.settings)
    set_user_info(user_info, request.app.state.settings)

    return CreateUserResponse(user_info=user_info, password=new_password)


@router.post(
    "/reset_password",
    dependencies=[ScopedTo([UserScope.admin])],
    tags=[USER],
)
async def reset_password(request: Request, username: str, password: str) -> Any:
    """Reset a user's password."""

    credential = get_auth_credential(
        username,
        settings=request.app.state.settings,
    )

    # TODO: generate passwords differently
    # new_password = b64encode(b16decode(rand_q().to_hex()[0:16]))
    credential.hashed_password = AuthenticationContext(
        request.app.state.settings
    ).get_password_hash(password)

    update_auth_credential(credential, request.app.state.settings)

    return {"username": username, "password": password}
