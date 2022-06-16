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
                 [(0, 0), (0, -1), (0, -1), (30, -1), (28, 0), (30, -1), (28, 0), (25, -4), (25, 0), (25, 0)],
                 rateOfFire=11)
