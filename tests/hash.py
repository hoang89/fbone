from SimpleAES import SimpleAES
import time
SECRET_KEY = "the social secret"

aes = SimpleAES(SECRET_KEY)

encoded_text = aes.encrypt("client_key" +":"+ str(int(time.time())))

print encoded_text

plaintext = aes.decrypt(encoded_text)

print plaintext.split(":")[0]
print plaintext.split(":")[1]