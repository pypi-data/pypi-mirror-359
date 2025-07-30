import turtle
import random

pen = turtle.Turtle()
pen.speed(10)


def polygon(sides,size=50):
    # direction = random.choice([pen.right,pen.left])
    direction = pen.left
    for i in range(sides):
        pen.forward(size)
        direction(360/sides)

def stickman(size):
    # head
    polygon(random.randint(3,11), size)
    pen.forward(size/2)
    pen.right(90)

    # body
    pen.forward(200)
    pen.backward(150)

    # left arm
    pen.right(30)
    pen.forward(50)
    pen.backward(50)
    pen.left(30)

    # right arm
    pen.left(30)
    pen.forward(50)
    pen.backward(50)
    pen.right(30)
    
    pen.forward(150)

    # left leg
    pen.right(30)
    pen.forward(50)
    pen.backward(50)
    pen.left(30)

    # right leg
    pen.left(30)
    pen.forward(50)
    pen.backward(50)
    pen.right(30)


def main():
    for i in range(random.randint(1, 10)):
        size = random.randint(30, 50)
        stickman(size)

        pen.up()
        pen.home()
        pen.right(random.randint(0, 360))
        pen.forward((2.5 + i )* size)
        # pen.setheading(0)
        pen.down()

    turtle.done()


if __name__ == "__main__":
    main()
