class Weapon:
    def __init__(self, name, sprayPattern, rateOfFire):
        self.name = name
        self.sprayPattern = sprayPattern
        self.rateOfFire = 1000 / rateOfFire

    def get_correction_by_shots(self, shotNum):
        if shotNum >= len(self.sprayPattern):
            shotNum = len(self.sprayPattern) - 1

        return self.sprayPattern[shotNum]


# WEAPONS #
NoWeapon = Weapon('NoWeapon', [(0, 0)], rateOfFire=10)
Vandal = Weapon('Vandal',
                [(0, 0), (6, -1), (7, -1), (20, -4), (28, -3), (40, -1), (60, 0), (60, -4), (60, -11), (0, 0)],
                rateOfFire=9.75)
Phantom = Weapon('Phantom',
                 [(0, 0), (6, -1), (7, -1), (20, -4), (28, -3), (40, -1), (45, 0), (45, -4), (45, -1), (0, 0)],
                 rateOfFire=11)

Spectre = Weapon('Spectre',
                 [(0, 0), (6, -1), (7, -1), (12, -4), (14, -3), (20, -1), (20, 0), (5, -4), (5, -1), (10, -4),
                  (10, 0), (20, 0), (20, 0), (20, -4), (20, -1), (0, 0)], rateOfFire=13.33)
