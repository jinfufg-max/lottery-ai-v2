import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV")

if not ECPAY_MERCHANT_ID:
    raise ValueError("ECPAY_MERCHANT_ID 未設定")

if not ECPAY_HASH_KEY:
    raise ValueError("ECPAY_HASH_KEY 未設定")

if not ECPAY_HASH_IV:
    raise ValueError("ECPAY_HASH_IV 未設定")

print("✅ ECPAY ENV OK")
