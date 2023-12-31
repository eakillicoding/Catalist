from fastapi import (
    APIRouter,
    Depends,
    status,
    Response,
    HTTPException,
    Request
)
from jwtdown_fastapi.authentication import Token
from authenticator import authenticator
from pydantic import BaseModel
from models.errors import DuplicateAccountError
from queries.accounts import (
    AccountIn,
    AccountOut,
    AccountOutWithPassword,
    AccountQueries,
)
router = APIRouter()


class AccountForm(BaseModel):
    username: str
    password: str


class AccountToken(Token):
    account: AccountOut


class HttpError(BaseModel):
    detail: str


@router.get("/token", response_model=AccountToken)
async def get_token(
    request: Request,
    account: AccountOutWithPassword = Depends(
        authenticator.try_get_current_account_data
    ),
) -> AccountToken | None:
    if authenticator.cookie_name in request.cookies:
        return {
            "access_token": request.cookies[authenticator.cookie_name],
            "type": "Bearer",
            "account": account,
        }


@router.get(
    "/api/accounts/{username}/", tags=["accounts"], response_model=AccountOut
)
async def get_account(
    username: str,
    accounts: AccountQueries = Depends(),
):
    return accounts.get(username)


@router.post("/api/accounts", response_model=AccountToken | HttpError)
async def create_account(
    info: AccountIn,
    request: Request,
    response: Response,
    accounts: AccountQueries = Depends(),
):
    hashed_password = authenticator.hash_password(info.password)
    try:
        account = accounts.create(info, hashed_password)
    except DuplicateAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an account with those credentials",
        )
    form = AccountForm(username=info.username, password=info.password)
    token = await authenticator.login(response, request, form, accounts)
    return AccountToken(account=account, **token.dict())
