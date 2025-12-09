import math
import json
import os


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
    def __init__(self, team1, team2):
        self.team1 = team1; self.team2 = team2; self.score = {"team1": 0, "team2": 0}
    def display(self):
        print(f"--- СЧЕТ: {self.team1} [{self.score['team1']}] : [{self.score['team2']}] {self.team2} ---")

# --- СИСТЕМЫ СУДЕЙСТВА (Referees) ---

class SRS:
    def __init__(self, field, tablo):
        self.field = field; self.tablo = tablo
    def check_out(self, ball: Ball):
        out = False
        if ball.position.x < 0 or ball.position.x > self.field.length \
                or ball.position.y < 0 or ball.position.y > self.field.width:
            print(">>> СУДЬЯ: Аут!")
            out = True
        else:
            print(">>> СУДЬЯ: Мяч в поле.")
        if out and ball.owner:
            last_team = ball.owner.team.name
            if last_team == self.tablo.team1:
                receiving = self.tablo.team2
            else:
                receiving = self.tablo.team1
            print(f">>> СУДЬЯ: Право вбрасывания — у команды {receiving}")
        return out

class FRS(SRS):
    def foul(self, fouled: Footballer):
        if fouled.team.name == self.tablo.team1:
            if self.field.penalty2.is_penalty(fouled):
                print(">>> СУДЬЯ: ПЕНАЛЬТИ!")
            else:
                print(">>> СУДЬЯ: Свободный удар.")
        else:
            if self.field.penalty1.is_penalty(fouled):
                print(">>> СУДЬЯ: ПЕНАЛЬТИ!")
            else:
                print(">>> СУДЬЯ: Свободный удар.")
    def booking(self, fouler: Footballer):
        fouler.cards["Y"] += 1
        print(f">>> СУДЬЯ: Желтая карточка игроку {fouler.number} ({fouler.team.name})")
        if fouler.cards["Y"] > 1: self.send_off(fouler)
    def send_off(self, fouler: Footballer):
        fouler.cards["R"] += 1; print(f">>> СУДЬЯ: КРАСНАЯ! Игрок {fouler.number} удален.")
    def check_score(self, ball: Ball):
        left = self.field.goal1; right = self.field.goal2
        if ball.position.x > right.x and right.post1 > ball.position.y > right.post2:
            self.tablo.score["team1"] += 1; print(f">>> ГОЛ {self.tablo.team1}!")
        elif ball.position.x < left.x and left.post1 > ball.position.y > left.post2:
            self.tablo.score["team2"] += 1; print(f">>> ГОЛ {self.tablo.team2}!")
        else:
            print(">>> СУДЬЯ: Нет гола.")

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

# --- ЛОГИКА ИГРЫ (RULES & CONTROLLER) ---

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
        return XY(52.5, 34)
    def handle_score(self, referee, ball, teams, **kwargs):
        referee.check_score(ball)
    def handle_foul(self, referee, teams, **kwargs):
        t1, t2 = teams.get(kwargs.get("fouler_team")), teams.get(kwargs.get("fouled_team"))
        if t1 and t2:
            p1, p2 = t1.get_player(kwargs.get("fouler_num")), t2.get_player(kwargs.get("fouled_num"))
            if p1 and p2:
                referee.foul(p1, p2)
                referee.booking(p1)
            else:
                print("! Игрок не найден")
        else:
            print("! Для футбольного фола нужны две команды")

class BasketballRules(GameRules):
    def create_field(self):
        return Court(28, 15)
    def create_referee(self, field, tablo):
        return BRS(field, tablo)
    def create_player(self, x, y, team, number):
        return Basketballer(x, y, team, number)
    def get_initial_ball_pos(self):
        return XY(14, 7.5)
    def handle_score(self, referee, ball, teams, **kwargs):
        t = teams.get(kwargs.get("team"))
        if t:
            p = t.get_player(kwargs.get("number"))
            if p:
                referee.check_score(p)
            else:
                print("! Игрок не найден")
        else:
            print("! Для баскетбола нужно указать команду бросающего")
    def handle_foul(self, referee, teams, **kwargs):
        t = teams.get(kwargs.get("fouler_team"))
        if t:
            p = t.get_player(kwargs.get("fouler_num"))
            if p:
                referee.foul(p)
            else:
                print("! Игрок не найден")

class GameController:
    def __init__(self):
        self.teams = {}; self.ball = None; self.ref = None
        self.field = None; self.tablo = None; self.rules = None
    def setup_game(self, game_type, team1_name, team2_name):
        rules_map = {"football": FootballRules(), "basketball": BasketballRules()}
        self.rules = rules_map.get(game_type)
        if not self.rules: return print(f"! Неизвестный тип игры: {game_type}")

        self.teams = {team1_name: Team(team1_name), team2_name: Team(team2_name)}
        self.tablo = Scoreboard(team1_name, team2_name)
        self.field = self.rules.create_field()
        self.ref = self.rules.create_referee(self.field, self.tablo)
        pos = self.rules.get_initial_ball_pos()
        self.ball = Ball(pos.x, pos.y)
        print(f"--- Матч {game_type.upper()} начался: {team1_name} vs {team2_name} ---")
    def load_scenario(self, filename):
        if not os.path.exists(filename):
            print(f"! Файл {filename} не найден.")
            return
        print(f"\n--- ЧТЕНИЕ СЦЕНАРИЯ ИЗ {filename} ---")
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.process_json_actions(data)
        print("--- КОНЕЦ СЦЕНАРИЯ ---\n")
    def process_json_actions(self, actions):
        if not isinstance(actions, list): actions = json.loads(actions)
        for act in actions:
            cmd = act.get("action")
            print(f"[Действие]: {cmd}")
            if cmd == "setup":
                self.setup_game(act["type"], act["team1"], act["team2"])
            elif cmd == "add_player":
                if self.rules:
                    team = self.teams.get(act["team"])
                    if team:
                        self.rules.create_player(act["x"], act["y"], team, act["number"])
                        print(f"  + Игрок #{act['number']} в команду {act['team']}")
            elif cmd == "move_ball":
                if self.ball: self.ball.move(act["x"], act["y"])
            elif cmd == "move_player":
                t = self.teams.get(act["team"])
                if t:
                    p = t.get_player(act["number"])
                    if p: p.move(act["x"], act["y"])
            elif cmd == "check_score":
                if self.rules:
                    self.rules.handle_score(self.ref, self.ball, self.teams, **act)
                    self.tablo.display()
            elif cmd == "check_out":
                if self.ref: self.ref.check_out(self.ball)
            elif cmd == "foul":
                if self.rules: self.rules.handle_foul(self.ref, self.teams, **act)

if __name__ == "__main__":
    game = GameController()
    if not os.path.exists("actions.json"):
        with open("actions.json", "w", encoding='utf-8') as f:
            f.write("""[
                {"action": "setup", "type": "football", "team1": "Liverpool", "team2": "ManCity"},
                {"action": "add_player", "team": "Liverpool", "number": 11, "x": 100, "y": 34},
                {"action": "add_player", "team": "ManCity", "number": 3, "x": 102, "y": 34},
                {"action": "move_ball", "x": 106, "y": 34},
                {"action": "check_score"},
                {"action": "foul", "fouler_team": "ManCity", "fouler_num": 3, "fouled_team": "Liverpool", "fouled_num": 11}
            ]""")
    fname = input("Имя файла (default: actions.json): ")
    if not fname: fname = "actions.json"
    game.load_scenario(fname)