from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 1000
REFRESH_TOKEN_EXPIRE_MINUTES = 5000
AUTH_TOKEN_TYPE = "bearer"
