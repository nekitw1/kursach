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

class Court(Field):
    def __init__(self, length, width):
        super().__init__(length, width)
        self.__backboard = 1.575
        self.basket1 = Basket(0 + self.__backboard, self.width / 2)
        self.basket2 = Basket(self.length - self.__backboard, self.width / 2)

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
    def __init__(self, field):
        self.field = field
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
    def __init__(self, field):
        super().__init__(field)
    def booking(self, fouler: Footballer):
        fouler.cards["Y"] += 1
        print("Предупреждение игроку")
        if fouler.cards["Y"] > 1:
            self.send_off(fouler)
    def send_off(self, fouler: Footballer):
        fouler.cards["R"] += 1
        print("Игрок должен покинуть поле")
    def check_score(self, ball: Ball, tablo: Scoreboard):
        left = self.field.goal1
        right = self.field.goal2
        if (
            ball.position.x > right.x and
            ball.position.y < right.post1 and
            ball.position.y > right.post2
        ):
            tablo.score["team1"] += 1
        elif (
            ball.position.x < left.x and
            ball.position.y < left.post1 and
            ball.position.y > left.post2
        ):
            tablo.score["team2"] += 1
        else:
            print("Нет гола")

# #BRS - Basketball Refereeing System (футбольчик)
# class BRS(SRS):

### Инициализация пока что такая
pole = Pitch(105, 68)
# kort = Court(28, 15)
ref = FRS(pole)
liver = Team("Liverpool")
tablo = Scoreboard(liver.name, "team2")
vvd = Footballer(20, 30, liver, 4)

### Система определения голов работает
# football = Ball(0, 34)
# ref.check_score(football, tablo)
# football.move(105.1, 34)
# ref.check_score(football, tablo)
# tablo.display()

### Карточки выдаются правильно
# ref.booking(vvd)
# ref.booking(vvd)
# ref.send_off(vvd)

print('чек')
