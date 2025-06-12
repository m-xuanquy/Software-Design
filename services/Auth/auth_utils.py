import random
import string
from services import get_user_by_username
def generate_password()->str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(alphabet) for i in range(16))

async def generate_username(email:str)->str:
    base_username = email.split("@")[0].lower()
    base_username = "".join(c for c in base_username if c.isalnum() or c == "_")
    if len(base_username) < 3:
        base_username = f"user_{base_username}"
    count =1
    username = base_username
    while True:
        existing=await get_user_by_username(username)
        if not existing:
            break
        username = f"{base_username}_{count}"
        count += 1
    return username