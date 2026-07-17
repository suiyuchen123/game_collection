class GameState:
    MENU = "menu"
    PLAYING = "playing"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    TITLE_VIEW = "title_view"

    def __init__(self):
        self.current_state = self.MENU
        self.current_game = None
        self.current_level = None
        self.game_result = None


class GameResult:
    WIN = "win"
    LOSE = "lose"

    def __init__(self, result, score=0):
        self.result = result
        self.score = score