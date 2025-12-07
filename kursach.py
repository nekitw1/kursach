import math

class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

class Field:
    def __init__(self, length, width):
        self.length = length
        self.width = width

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.__width = 7.32
        self.post1 = y + self.__width / 2
        self.post2 = y - self.__width / 2

class PenaltyArea:
    def __init__(self, x0, y_center):
        self.x0 = x0
        self.__y_center = y_center
        self.__length = 16
        self.__width = 40
        if self.x0 == 0:
            self.x1 = self.x0 + self.__length
            self.y0 = self.__y_center - self.__width / 2
            self.y1 = self.__y_center + self.__width / 2
        else:
            self.x1 = self.x0
            self.x0 = self.x0 - self.__length
            self.y0 = self.__y_center - self.__width / 2
            self.y1 = self.__y_center + self.__width / 2
    def is_penalty(self, fouled: Footballer):
        x_inside = self.x0 <= fouled.position.x <= self.x1
        y_inside = self.y0 <= fouled.position.y <= self.y1
        return x_inside and y_inside

class Pitch(Field):
    def __init__(self, length, width):
        super().__init__(length, width)
        self.goal1 = Goal(0, self.width / 2)
        self.goal2 = Goal(self.length, self.width / 2)
        self.penalty1 = PenaltyArea(0, self.width / 2)
        self.penalty2 = PenaltyArea(self.length, self.width / 2)

class Basket:
    def __init__(self, x, y):
        self.position = XY(x, y)
        self.__rimradius = 0.225

class ThreePtLine:
    def __init__(self, basket: Basket, radius = 6.75):
        self.__position = basket.position
        self.radius = radius
    def is_threept(self, shooter: Basketballer):
        return math.hypot(shooter.position.x - self.__position.x,
                          shooter.position.y - self.__position.y) > self.radius

class Court(Field):
    def __init__(self, length, width):
        super().__init__(length, width)
        self.__backboard = 1.575
        self.basket1 = Basket(0 + self.__backboard, self.width / 2)
        self.basket2 = Basket(self.length - self.__backboard, self.width / 2)
        self.threept1 = ThreePtLine(self.basket1)
        self.threept2 = ThreePtLine(self.basket2)

class Ball:
    def __init__(self, x, y):
        self.position = XY(x, y)
        self.owner = None
    def move(self, x, y):
        self.position = XY(x, y)

class Player:
    def __init__(self, x, y, team, number):
        self.position = XY(x, y)
        self.team = team
        self.number = number
        team.players.append(self)
    def move(self, x, y):
        self.position = XY(x, y)

class Footballer(Player):
    def __init__(self, x, y, team, number):
        super().__init__(x, y, team, number)
        self.cards = {"Y": 0, "R": 0}

class Basketballer(Player):
    def __init__(self, x, y, team, number):
        super().__init__(x, y, team, number)
        self.fouls = 0

class Scoreboard:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.score = {"team1": 0, "team2": 0}
    def display(self):
        print(f"{self.team1} {self.score['team1']} : {self.score['team2']} {self.team2}")

#SRS - Sports Refereeing System (система судйества спортивных игр)
class SRS:
    def __init__(self, field, tablo):
        self.field = field
        self.tablo = tablo
    def check_out(self, ball: Ball):
        if(
            ball.position.x < 0 or
            ball.position.x > self.field.length or
            ball.position.y > self.field.width or
            ball.position.y < 0
        ):
            print("Аут")
            return True
        return False

# FRS - Football Refereeing System (футбольчик)
class FRS(SRS):
    def __init__(self, field, tablo):
        super().__init__(field, tablo)
    def foul(self, fouled: Footballer):
        if fouled.team.name == tablo.team1:
            if self.field.penalty2.is_penalty(fouled):
                print("Фол в пределах штрафной - пенальти")
            else:
                print("Фол. Должен назначить свободный удар")
        else:
            if self.field.penalty1.is_penalty(fouled):
                print("Фол в пределах штрафной - пенальти")
            else:
                print("Фол. Должен назначить свободный удар")
    def booking(self, fouler: Footballer):
        fouler.cards["Y"] += 1
        print("Предупреждение игроку")
        if fouler.cards["Y"] > 1:
            self.send_off(fouler)
    def send_off(self, fouler: Footballer):
        fouler.cards["R"] += 1
        print("Игрок должен покинуть поле")
    def check_score(self, ball: Ball):
        left = self.field.goal1
        right = self.field.goal2
        if ball.position.x > right.x and right.post1 > ball.position.y > right.post2:
            self.tablo.score["team1"] += 1
        elif ball.position.x < left.x and left.post1 > ball.position.y > left.post2:
            self.tablo.score["team2"] += 1
        else:
            print("Нет гола")

# #BRS - Basketball Refereeing System (футбольчик)
class BRS(SRS):
    def __init__(self, field, tablo):
        super().__init__(field, tablo)
    def foul(self, fouler: Basketballer):
        fouler.fouls += 1
        self.check_fouls(fouler)
    def check_fouls(self, fouler: Basketballer):
        if fouler.fouls > 5:
            print("Игрок должен покинуть корт")
    def calculate_points(self, shooter: Basketballer):
        if shooter.team.name == self.tablo.team1:
            threept_line = self.field.threept2
        else:
            threept_line = self.field.threept1
        return 3 if threept_line.is_threept(shooter) else 2
    def shooting_foul(self, fouler: Basketballer, fouled: Basketballer):
        print("Бросковый фол")
        fouler.fouls += 1
        if self.calculate_points(fouled) == 3:
            print("При промахе назначить три штрафных броска")
        else:
            print("При промахе назначить два штрафных броска")
    def check_score(self, shooter: Basketballer):
        if shooter.team.name == self.tablo.team1:
            points = self.calculate_points(shooter)
            self.tablo.score["team1"] += points
        else:
            points = self.calculate_points(shooter)
            self.tablo.score["team2"] += points

# Футбол

pole = Pitch(105, 68)

liver = Team("Liverpool")
city = Team("City")
tablo = Scoreboard(liver.name, city.name)
ref = FRS(pole, tablo)
vvd = Footballer(10, 30, liver, 4)
haaland = Footballer(10, 34, city, 9)

# Система определения голов работает
football = Ball(-0.1, 34)
ref.check_score(football)
football.move(105.1, 34)
ref.check_score(football)
tablo.display()

# Карточки выдаются правильно
# ref.booking(vvd)
# ref.booking(vvd)
# ref.send_off(vvd)
ref.foul(haaland)

# Баскетбол

# kort = Court(28, 15)

# gsw = Team("GSW")
# ptb = Team("PTB")
# tablo = Scoreboard(gsw.name, ptb.name)
# ref = BRS(kort, tablo)
# curry = Basketballer(15, 7, gsw, 30)
# sharpe = Basketballer(15, 7, ptb, 17)

# Определение очков работает правильно
# ref.check_score(curry)
# ref.check_score(sharpe)
# tablo.display()
# curry.move(25, 7)
# sharpe.move(25, 7)
# ref.check_score(curry)
# ref.check_score(sharpe)
# tablo.display()
# curry.move(5, 7)
# sharpe.move(5, 7)
# ref.shooting_foul(curry, sharpe)
# ref.shooting_foul(sharpe, curry)
# ref.check_score(curry)
# ref.check_score(sharpe)
# tablo.display()

print('чек')