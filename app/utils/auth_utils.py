import hashlib

def verify_user_credentials(user, password):
    hash_value = hashlib.sha256(password.encode()).hexdigest()
    return user.password_hash == hash_value
