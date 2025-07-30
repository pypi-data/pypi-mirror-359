from typing import Dict
import jwt
from datetime import datetime, timezone, timedelta
from Osdental.Handlers.DBconnectionQuery import DBConnectionQuery
from Osdental.Shared.Message import Message
from Osdental.Exception.ControlledException import MissingFieldException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class CData:
    @staticmethod
    async def generate_token_initial():    
        return await CData.__generate_jwt(None)

    @staticmethod
    async def generate_token_account(sub_account: str = None):    
        return await CData.__generate_jwt(sub_account)

    @staticmethod
    async def __generate_jwt(sub_account: str = None) -> Dict[str, str]:        
        if sub_account is None or sub_account != '':                        
            now = datetime.now(timezone.utc)            
            iat = int(now.timestamp())                        
            cdata = await DBConnectionQuery.get_cdata_integration_data()                 
            exp = int((now + timedelta(minutes=cdata.exp_token)).timestamp())            
            catalog = await DBConnectionQuery.get_cdata_integration_catalog_data()            
            payload = {
                'tokenType': catalog.token_type,
                'iss': catalog.iss,
                'iat': iat,
                'exp': exp
            }            
            if sub_account:
                payload['sub'] = sub_account                                                                                
            private_key = CData.generate_private_key(cdata.key_private)            
            token = jwt.encode(payload, private_key, algorithm='RS256')                                                                    
            return token
        else:             
            raise MissingFieldException(message=Message.SUB_ACCOUNT_REQUIRED)

    @staticmethod
    def generate_private_key(private_rsa: str):                  
        private_key = serialization.load_pem_private_key(
            private_rsa.encode(),
            password=None,
            backend=default_backend()
        )
        return private_key