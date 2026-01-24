from random import randint


def create_random_color_hex():
    r = randint(1, 255)
    g = randint(1, 255)
    b = randint(1, 255)
    return f"#{r:02x}{g:02x}{b:02x}"
