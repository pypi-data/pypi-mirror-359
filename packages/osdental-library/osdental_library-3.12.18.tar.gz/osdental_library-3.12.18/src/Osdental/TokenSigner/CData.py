from typing import Dict
import time 
from Osdental.Handlers.DBconnectionQuery import DBConnectionQuery
from Osdental.Encryptor.Jwt import JWT
from Osdental.Shared.Message import Message
from Osdental.Exception.ControlledException import MissingFieldException

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
            iat = int(time.time())                    
            cdata = await DBConnectionQuery.get_cdata_integration_data()        

            catalog = await DBConnectionQuery.get_cdata_integration_catalog_data()            
            payload = {
                'token_type': catalog.token_type,
                'iss': catalog.iss,
                'iat': iat,
                'exp': cdata.exp_token
            }            
            if sub_account:
                payload['sub'] = sub_account                                
            return JWT.generate_token(payload, cdata.key_private)
        else:             
            raise MissingFieldException(message=Message.SUB_ACCOUNT_REQUIRED)
