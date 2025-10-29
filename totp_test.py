import pyotp

secret = "JQSR5NZEFQYPDMUSHXV4WBF5CBHTBI34"  # el secret que te devolvió /2fa/generate
totp = pyotp.TOTP(secret)
print(totp.now())  # código actual de 6 dígitos
