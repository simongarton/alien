import json
import random

from alien_generator import generate_alien

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

    with open("alien.json", "w") as f:
        json.dump(alien, f, indent=2)

    print("Alien generator: wrote alien.json")
