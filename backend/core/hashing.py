from passlib.context import CryptContext


pwd_context=CryptContext(schemes=["argon2"],deprecated="auto")


class Hasher:
    @staticmethod
    def verify_password(plain_password,hashed_password):
        return pwd_context.verify(plain_password,hashed_password)
    

    @staticmethod
    def get_password(plain_password):
        return pwd_context.hash(plain_password)
