import random
from alien_generator import generate_alien
from image_painter import paint_image

if __name__ == "__main__":

    count = int(input("How many aliens would you like to generate? "))

    palette = random.choice(["green", "blue", "red", "cga", "full"])
    width = 16 # random.randint(16, 32)
    height = width # random.randint(16, 32)
    background = "#ffffff"

    for i in range(count):
        eyes = random.randint(1, 4)
        bigeyes = random.choice(["true", "false"])
        legs = random.randint(1, 4)
        arms = random.randint(1, 4)
        shape = None
        alien = generate_alien(width=width, height=height, background=background, eyes=eyes, bigeyes=bigeyes, legs=legs, arms=arms, shape=shape, palette=palette)
        path = paint_image(data=alien, filename=f"../aliens/alien_{i}.png", scale=20)

    print(f"Alien generator: wrote {count} to ../aliens/")
