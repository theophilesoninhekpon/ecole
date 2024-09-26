import asyncio
import os
from ecole.settings import *
from android_sms_gateway import client, domain, Encryptor

class SMSClient:
    login = ANDROID_SMS_GATEWAY_LOGIN
    password = ANDROID_SMS_GATEWAY_PASSWORD
    encryptor = Encryptor('passphrase') # for end-to-end encryption, see https://sms.capcom.me/privacy/encryption/


    async def send_message(self, message:str, phone_number:str):
        message = domain.Message(
            message,
            [phone_number],
        )
        async with client.AsyncAPIClient(
            self.login, 
            self.password,
            encryptor=self.encryptor,
        ) as c:
            state = await c.send(message)
            print(state)

            state = await c.get_state(state.id)
            print(state)
