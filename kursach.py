import math
import json

class XY:
    def __init__(self, x, y):
        self.x = x; self.y = y

class Team:
    def __init__(self, name):
        self.name = name; self.players = []
    def get_player(self, number):
        for p in self.players:
            if p.number == number: return p
        return None

class Field:
    def __init__(self, length, width):
        self.length = length; self.width = width

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.__width = 7.32
        self.post1 = y + self.__width / 2
        self.post2 = y - self.__width / 2

class PenaltyArea:
    def __init__(self, x0, y_center):
        self.x0 = x0; self.__y_center = y_center; self.__length = 16; self.__width = 40
        if self.x0 == 0:
            self.x1 = self.x0 + self.__length
            self.y0 = self.__y_center - self.__width / 2
            self.y1 = self.__y_center + self.__width / 2
        else:
            self.x1 = self.x0
            self.x0 = self.x0 - self.__length
            self.y0 = self.__y_center - self.__width / 2
            self.y1 = self.__y_center + self.__width / 2
    def is_inside(self, fouled: Footballer):
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
        self.position = XY(x, y); self.__rimradius = 0.225

class ThreePtLine:
    def __init__(self, basket: Basket, radius=6.75):
        self.__position = basket.position; self.radius = radius
    def is_threept(self, shooter):
        return math.hypot(shooter.position.x - self.__position.x, shooter.position.y - self.__position.y) > self.radius

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
        self.position = XY(x, y); self.owner = None
    def move(self, x, y):
        self.position = XY(x, y)

class Player:
    def __init__(self, x, y, team, number):
        self.position = XY(x, y); self.team = team; self.number = number
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
        self.fouls = {"P": 0, "T": 0}

class Scoreboard:
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1; self.team2 = team2; self.score = {"team1": 0, "team2": 0}
    def display(self):
        print(f"--- СЧЕТ: {self.team1} [{self.score['team1']}] : [{self.score['team2']}] {self.team2} ---")

class SRS:
    def __init__(self, field, tablo):
        self.field = field; self.tablo = tablo
    def check_out(self, ball: Ball):
        if ball.position.x < 0 or ball.position.x > self.field.length \
                or ball.position.y < 0 or ball.position.y > self.field.width:
            print(">>> СУДЬЯ: Аут!")
        else:
            print(">>> СУДЬЯ: Мяч в поле.")

class FRS(SRS):
    def foul(self, fouler: Footballer, fouled: Footballer):
        if fouled.team.name == self.tablo.team1:
            if self.field.penalty2.is_inside(fouled):
                print(">>> СУДЬЯ: ПЕНАЛЬТИ!")
            else:
                print(">>> СУДЬЯ: Свободный удар.")
        else:
            if self.field.penalty1.is_inside(fouled):
                print(">>> СУДЬЯ: ПЕНАЛЬТИ!")
            else:
                print(">>> СУДЬЯ: Свободный удар.")
    def booking(self, fouler: Footballer):
        fouler.cards["Y"] += 1
        print(f">>> СУДЬЯ: Желтая карточка игроку {fouler.number} ({fouler.team.name})")
        if fouler.cards["Y"] > 1: self.ejection(fouler)
    def ejection(self, fouler: Footballer):
        fouler.cards["R"] += 1; print(f">>> СУДЬЯ: КРАСНАЯ! Игрок {fouler.number} удален.")
    def check_score(self, ball: Ball):
        left = self.field.goal1; right = self.field.goal2
        if ball.position.x > right.x and right.post1 > ball.position.y > right.post2:
            self.tablo.score["team1"] += 1; print(f">>> ГОЛ {self.tablo.team1}!")
        elif ball.position.x < left.x and left.post1 > ball.position.y > left.post2:
            self.tablo.score["team2"] += 1; print(f">>> ГОЛ {self.tablo.team2}!")
        else:
            print(">>> СУДЬЯ: Нет гола.")
    def check_offside(self, ball: Ball, attacker: Footballer, defend: Team):
        if attacker.team.name == self.tablo.team1:
            defenders = sorted(defend.players, key=lambda p: p.position.x, reverse=True)
            last_def = defenders[1]

            if (attacker.position.x > last_def.position.x and
                    attacker.position.x > ball.position.x and
                    attacker.position.x > self.field.length / 2):
                print(">>> СУДЬЯ: Офсайд")
            else: print(">>> СУДЬЯ: Игрок в правильном положении")
        else:
            defenders = sorted(defend.players, key=lambda p: p.position.x)
            last_def = defenders[1]

            if (attacker.position.x < last_def.position.x and
                    attacker.position.x < ball.position.x and
                    attacker.position.x < self.field.length / 2):
                print(">>> СУДЬЯ: Офсайд")
            else: print(">>> СУДЬЯ: Игрок в правильном положении")

class BRS(SRS):
    def ejection(self, fouler: Basketballer):
        if fouler.fouls["P"] > 5:
            print(f">>> СУДЬЯ: Удаление за перебор фолов.")
        elif fouler.fouls["T"] > 1:
            print(f">>> СУДЬЯ: Удаление за перебор технических фолов.")
    def foul(self, fouler: Basketballer):
        fouler.fouls["P"] += 1; print(f">>> СУДЬЯ: Персональный фол игроку {fouler.number}")
        self.ejection(fouler)
    def technical_foul(self, fouler: Basketballer):
        fouler.fouls["T"] += 1; print(f">>> СУДЬЯ: Технический фол игроку {fouler.number}")
        self.ejection(fouler)
    def shooting_foul(self, fouler: Basketballer, fouled: Basketballer):
        fouler.fouls["P"] += 1; print(f">>> СУДЬЯ: Бросковый фол на игроке {fouled.number}")
        self.ejection(fouler)
        if self.calculate_points(fouled) == 3:
            print(f">>> СУДЬЯ: При промахе {fouled.number} должен бросить 3 штрафных броска")
        else:
            print(f">>> СУДЬЯ: При промахе {fouled.number} должен бросить 2 штрафных броска")
    def calculate_points(self, shooter: Basketballer):
        line = self.field.threept2 if shooter.team.name == self.tablo.team1 else self.field.threept1
        return 3 if line.is_threept(shooter) else 2
    def check_score(self, shooter: Basketballer):
        points = self.calculate_points(shooter)
        if shooter.team.name == self.tablo.team1:
            self.tablo.score["team1"] += points
        else:
            self.tablo.score["team2"] += points
        print(f">>> СУДЬЯ: +{points} очков команде {shooter.team.name}!")

class GameRules:
    def create_field(self): raise NotImplementedError
    def create_referee(self, field, tablo): raise NotImplementedError
    def create_player(self, x, y, team, number): raise NotImplementedError
    def get_initial_ball_pos(self): raise NotImplementedError
    def handle_score(self, referee, ball, teams, **kwargs): raise NotImplementedError
    def handle_foul(self, referee, teams, **kwargs): raise NotImplementedError

class FootballRules(GameRules):
    def create_field(self):
        return Pitch(105, 68)
    def create_referee(self, field, tablo):
        return FRS(field, tablo)
    def create_player(self, x, y, team, number):
        return Footballer(x, y, team, number)
    def get_initial_ball_pos(self):
        return 52.5, 34
    def handle_score(self, referee: FRS, ball: Ball, teams, **kwargs):
        referee.check_score(ball)
    def handle_foul(self, referee: FRS, teams, **kwargs):
        fouler = kwargs.get("fouler")
        fouled = kwargs.get("fouled")
        if fouler and fouled:
            referee.foul(fouler, fouled)
    def handle_offside(self, referee: FRS, ball: Ball, **kwargs):
        attacker = kwargs.get("attacker")
        defend = kwargs.get("defend")
        referee.check_offside(ball, attacker, defend)

class BasketballRules(GameRules):
    def create_field(self):
        return Court(28, 15)
    def create_referee(self, field, tablo):
        return BRS(field, tablo)
    def create_player(self, x, y, team, number):
        return Basketballer(x, y, team, number)
    def get_initial_ball_pos(self):
        return (14, 7.5)
    def handle_score(self, referee: BRS, ball, teams, **kwargs):
        shooter = kwargs.get("shooter")
        if shooter:
            referee.check_score(shooter)
    def handle_foul(self, referee: BRS, teams, **kwargs):
        foul_type = kwargs.get("type")
        fouler = kwargs.get("fouler")
        fouled = kwargs.get("fouled")
        if foul_type == "technical":
            referee.technical_foul(fouler)
        elif foul_type == "shooting":
            referee.shooting_foul(fouler, fouled)
        else:
            referee.foul(fouler)

class GameController:
    def __init__(self):
        self.rules = None
        self.field = None
        self.referee = None
        self.ball = None
        self.teams = {}
        self.tablo = None

    def load_actions(self, filename="actions.json"):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def setup_game(self, game_type, team1, team2):
        if game_type == "football":
            self.rules = FootballRules()
        elif game_type == "basketball":
            self.rules = BasketballRules()
        else:
            raise ValueError("Неизвестный тип игры")
        self.teams[team1] = Team(team1)
        self.teams[team2] = Team(team2)
        self.field = self.rules.create_field()
        self.tablo = Scoreboard(team1, team2)
        self.referee = self.rules.create_referee(self.field, self.tablo)
        bx, by = self.rules.get_initial_ball_pos()
        self.ball = Ball(bx, by)
        print(f">>> Игра создана: {game_type.upper()}, {team1} vs {team2}")

    def add_player(self, team, number, x, y):
        self.rules.create_player(x, y, self.teams[team], number)
        print(f">>> Добавлен игрок {number} в команду {team}")

    def move_ball(self, x, y):
        self.ball.move(x, y)
        print(f">>> Мяч перемещён в ({x}, {y})")

    def process_actions(self, actions):
        for act in actions:
            if act["action"] == "setup":
                self.setup_game(act["type"], act["team1"], act["team2"])

            elif act["action"] == "add_player":
                self.add_player(act["team"], act["number"], act["x"], act["y"])

            elif act["action"] == "move_ball":
                self.move_ball(act["x"], act["y"])

            elif act["action"] == "check_score":
                if isinstance(self.referee, FRS):
                    self.rules.handle_score(self.referee, self.ball, self.teams)
                else:
                    shooter_team = act.get("team")
                    shooter_number = act.get("number")
                    shooter = self.teams[shooter_team].get_player(shooter_number)
                    self.rules.handle_score(self.referee, self.ball, self.teams, shooter=shooter)

                self.tablo.display()

            elif act["action"] == "check_out":
                self.referee.check_out(self.ball)

            elif act["action"] == "foul":
                fouler = self.teams[act["team_fouler"]].get_player(act["fouler"])
                fouled = self.teams[act["team_fouled"]].get_player(act["fouled"])

                self.rules.handle_foul(
                    self.referee,
                    self.teams,
                    fouler=fouler,
                    fouled=fouled,
                    type="personal"
                )

            elif act["action"] == "technical_foul":
                fouler = self.teams[act["team"]].get_player(act["number"])
                self.rules.handle_foul(
                    self.referee,
                    self.teams,
                    type="technical",
                    fouler=fouler
                )

            elif act["action"] == "shooting_foul":
                fouler = self.teams[act["team_fouler"]].get_player(act["fouler"])
                fouled = self.teams[act["team_fouled"]].get_player(act["fouled"])
                self.rules.handle_foul(
                    self.referee,
                    self.teams,
                    type="shooting",
                    fouler=fouler,
                    fouled=fouled
                )

            elif act["action"] == "booking":
                fouler = self.teams[act["team"]].get_player(act["number"])
                self.referee.booking(fouler)

            elif act["action"] == "ejection":
                fouler = self.teams[act["team"]].get_player(act["number"])
                self.referee.ejection(fouler)

            elif act["action"] == "check_offside":
                attacker = self.teams[act["team"]].get_player(act["number"])
                defend = self.teams[act["defend"]]
                self.rules.handle_offside(self.referee, self.ball, attacker=attacker, defend=defend)

    def console_menu(self):
        while True:
            print("\n=== ГЛАВНОЕ МЕНЮ ===")
            print("1 - Загрузить полный матч")
            print("2 - Запустить эпизод (ручной режим)")
            print("0 - Выход")
            cmd = input("> ")

            if cmd == "0":
                return

            if cmd == "1":
                filename = input("Введите имя JSON файла (Enter = actions.json): ")
                if filename.strip() == "":
                    filename = "actions.json"
                actions = self.load_actions(filename)
                print("\n>>> ЗАГРУЗКА ПОЛНОГО МАТЧА...\n")
                self.process_actions(actions)
                print("\n>>> ПОЛНЫЙ МАТЧ ЗАКОНЧЕН. Возврат в главное меню.\n")
                continue

            elif cmd == "2":
                print("\n=== РЕЖИМ ЭПИЗОДОВ ===")
                filename = input("Введите имя JSON файла (Enter = actions.json): ")
                if filename.strip() == "":
                    filename = "actions.json"
                actions = self.load_actions(filename)
                print("\n>>> ЗАГРУЗКА ЭПИЗОДА...\n")
                self.process_actions(actions)
                while True:
                    print("\nВыберите действие:")
                    print("1 - check_score")
                    print("2 - check_out")
                    if isinstance(self.referee, FRS):
                        print("3 - foul")
                        print("4 - offside")
                    else:
                        print("3 - shooting_foul")
                    print("0 - назад")
                    sub = input("> ")

                    if sub == "0":
                        break

                    if sub == "1":
                        if isinstance(self.referee, FRS):
                            self.rules.handle_score(self.referee, self.ball, self.teams)
                        else:
                            print("Введите данные бросающего игрока:")
                            team_name = input("Команда: ")
                            if team_name not in self.teams:
                                print("Нет такой команды.")
                                continue
                            try:
                                number = int(input("Номер игрока: "))
                            except:
                                print("Некорректный номер.")
                                continue
                            shooter = self.teams[team_name].get_player(number)
                            if not shooter:
                                print("Нет такого игрока.")
                                continue
                            self.rules.handle_score(self.referee, self.ball, self.teams, shooter=shooter)

                    elif sub == "2":
                        self.referee.check_out(self.ball)

                    elif sub == "3":
                        team_name = input("Команда нарушителя: ")
                        if team_name not in self.teams:
                            print("Нет такой команды.")
                            continue
                        try:
                            num_fouler = int(input("Номер нарушителя: "))
                        except:
                            print("Некорректный номер.")
                            continue
                        fouler = self.teams[team_name].get_player(num_fouler)
                        if not fouler:
                            print("Нет такого игрока.")
                            continue
                        if isinstance(fouler, Footballer):
                            team_fouled = input("Команда пострадавшего: ")
                            try:
                                num_fouled = int(input("Номер пострадавшего: "))
                            except:
                                print("Некорректный номер.")
                                continue
                            fouled_team = self.teams.get(team_fouled)
                            fouled = fouled_team.get_player(num_fouled) if fouled_team else None
                            if not fouled:
                                print("Нет такого игрока.")
                                continue
                            print("Футбольный фол:")
                            self.rules.handle_foul(self.referee, self.teams,
                                                   fouler=fouler, fouled=fouled)
                        else:
                            print("Бросковый фол:")
                            team_fouled = input("Команда пострадавшего: ")
                            try:
                                num_fouled = int(input("Номер пострадавшего: "))
                            except:
                                print("Некорректный номер.")
                                continue
                            fouled_team = self.teams.get(team_fouled)
                            fouled = fouled_team.get_player(num_fouled) if fouled_team else None
                            if not fouled:
                                print("Нет такого игрока.")
                                continue
                            self.rules.handle_foul(self.referee, self.teams,
                                                   type="shooting", fouler=fouler, fouled=fouled)

                    elif sub == "4":
                        print("Проверка на офсайд:")
                        team_attacker = input("Команда нападающего: ")
                        try:
                            num_attacker = int(input("Номер нападающего: "))
                        except:
                            print("Некорректный номер.")
                            continue
                        attacker_team = self.teams.get(team_attacker)
                        attacker = attacker_team.get_player(num_attacker) if attacker_team else None
                        if not attacker:
                            print("Нет такого игрока.")
                            continue
                        team_defend = input("Защищающаяся команда: ")
                        if team_defend not in self.teams:
                            print("Нет такой команды.")
                            continue
                        defend = self.teams.get(team_defend)
                        self.rules.handle_offside(self.referee, self.ball, attacker=attacker, defend=defend)
            else:
                print("Неизвестная команда")

def main():
    controller = GameController()
    controller.console_menu()

if __name__ == "__main__":
    main()
