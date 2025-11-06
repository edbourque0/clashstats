import random
import string

def generate_key(length):
    """Generates a random string of specified length using letters and digits."""
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string