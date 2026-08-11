import random

from alien_generator import generate_alien
from alien_json_to_text import alien_json_to_text

if __name__ == "__main__":
    palette = random.choice(["green", "blue", "red", "cga", "full"])
    width = random.randint(8, 32)
    height = width
    background = random.choice(["#ffffff", "#000000"])
    eyes = random.randint(1, 4)
    bigeyes = random.choice([True, False])
    legs = random.randint(1, 4)
    arms = random.randint(1, 4)

    alien = generate_alien(
        width=width,
        height=height,
        background=background,
        palette=palette,
        eyes=eyes,
        bigeyes=bigeyes,
        legs=legs,
        arms=arms,
    )

    lines = alien_json_to_text(alien)
    with open("alien.txt", "w") as f:
        f.write("\n".join(lines) + "\n")

    print("Alien generator: wrote alien.txt")
