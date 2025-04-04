import secrets
import string


def generate_api_key(length=32):
    characters = string.ascii_letters + string.digits
    api_key = "".join(secrets.choice(characters) for _ in range(length))
    return api_key


print(generate_api_key())  # contoh output: 'Y8fH2lK7x9P0qLwBvN1uA3zX5cR7TdUe'
