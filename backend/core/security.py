from datetime import datetime,timedelta,timezone
from core.config import settings
#from typing import Optional
from jose import jwt



def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHM)
    return encoded_jwt


 