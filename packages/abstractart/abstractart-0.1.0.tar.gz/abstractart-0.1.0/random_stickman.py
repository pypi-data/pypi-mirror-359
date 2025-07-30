import turtle
import random

pen = turtle.Turtle()
pen.speed(random.randint(1, 10))


def polygon(sides, size=random.randint(1, 50)):
    # direction = random.choice([pen.right,pen.left])
    direction = pen.left
    for i in range(sides):
        pen.forward(size)
        direction(random.randint(1, 360) / sides)


def stickman(size):
    # head
    polygon(random.randint(random.randint(1, 3), random.randint(3, 11)), size)
    pen.forward(size / random.randint(1, 2))
    pen.right(random.randint(1, 90))

    # body
    pen.forward(random.randint(1, 200))
    pen.backward(random.randint(1, 150))

    # left arm
    pen.right(random.randint(1, 30))
    pen.forward(random.randint(1, 50))
    pen.backward(random.randint(1, 50))
    pen.left(random.randint(1, 30))

    # right arm
    pen.left(random.randint(1, 30))
    pen.forward(random.randint(1, 50))
    pen.backward(random.randint(1, 50))
    pen.right(random.randint(1, 30))

    pen.forward(random.randint(1, 150))

    # left leg
    pen.right(random.randint(1, 30))
    pen.forward(random.randint(1, 50))
    pen.backward(random.randint(1, 50))
    pen.left(random.randint(1, 30))

    # right leg
    pen.left(random.randint(1, 30))
    pen.forward(random.randint(1, 50))
    pen.backward(random.randint(1, 50))
    pen.right(random.randint(1, 30))


def main():
    for i in range(random.randint(random.randint(1, 1), random.randint(1, 10))):
        size = random.randint(random.randint(1, 30), random.randint(30, 50))
        stickman(size)

        pen.up()
        pen.home()
        pen.right(random.randint(random.randint(0, 1), random.randint(1, 360)))
        pen.forward((random.randint(1, 3) + i) * size)
        pen.setheading(random.randint(0, 360))
        pen.down()

    turtle.done()


if __name__ == "__main__":
    main()
