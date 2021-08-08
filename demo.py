from cell import Grid1DFactory, Grid2DFactory
from ruleset import Ruleset1DFactory, Ruleset2DFactory


def demo_wolfram():
    r = Ruleset1DFactory.wolfram(18)
    print(r)

    g = Grid1DFactory.random(200)
    print(g)

    for _ in range(200):
        g = r.process_grid(g)
        print(g)


def demo_ruleset_string():
    r = Ruleset1DFactory.date_palm()
    print(r)

    g = Grid1DFactory.random(200)
    print(g)

    for _ in range(200):
        g = r.process_grid(g)
        print(g)


def demo_game_of_life():
    r = Ruleset2DFactory.game_of_life()
    print(r)

    g = Grid2DFactory.random(50, 50)
    print(g)

    for _ in range(100):
        g = r.process_grid(g)
        print("\n", "=" * 100, "\n")
        print(g)


if __name__ == '__main__':
    # demo_wolfram()
    # demo_ruleset_string()
    demo_game_of_life()
