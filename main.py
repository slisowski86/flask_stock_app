import os
from cryptography.fernet import Fernet
import base64

key=Fernet.generate_key()
print(key)
for x in os.environ:
    print((x, os.getenv(x)))


basedir=os.path.abspath(os.path.dirname(__file__))
print(basedir)
environment=os.environ.get('PWD')
print(environment)