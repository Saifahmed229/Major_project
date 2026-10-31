import base64
from pathlib import Path
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from py_vapid import Vapid

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Generate VAPID keys
vapid = Vapid()
vapid.generate_keys()

# Save private key
vapid.save_key(str(BASE_DIR / "private_key.pem"))

# Convert public key into browser-compatible Base64 format
public_key_bytes = vapid.public_key.public_bytes(
    encoding=Encoding.X962,
    format=PublicFormat.UncompressedPoint
)

public_key = base64.urlsafe_b64encode(public_key_bytes).rstrip(b"=").decode("utf-8")

# Save public key
with open(BASE_DIR / "vapid_public.txt", "w") as file:
    file.write(public_key)

print("VAPID keys generated successfully!")
print("Private key:", BASE_DIR / "private_key.pem")
print("Public key:", BASE_DIR / "vapid_public.txt")