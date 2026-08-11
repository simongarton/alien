from alien_generator import generate_alien
from image_painter import paint_image

if __name__ == "__main__":
    alien = generate_alien()
    path = paint_image(data=alien, filename="alien.png", scale=20)
    print(f"Alien generator: wrote {path}")
