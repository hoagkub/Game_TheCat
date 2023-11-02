import random
from pygase import GameState, Backend
import socket


### SETUP ###

WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

# Khoi tao trang thai game.
initial_game_state = GameState(
    players={},  # dictionary voi phan tu la `player_id: player_dict`
    TheCat_id=None,  # id cua mouser
    protection=None,  # wether protection from the mouser is active
    countdown=0.0,  # khoang thoi gian mouser duoc protect sau khi replay
)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        print("Server ip: ", s.getsockname()[0])
        s.close()
    backend.run(hostname="0.0.0.0", port=int(input('Port (You choose. Example: 4004): ')))

# Define game loop
# Game loop 
def time_step(game_state, dt):
    # Truoc luc nguoi choi tham gia, cap nhat game state la k can thiet.
    if game_state.TheCat_id is None:
        return {}
    # Neu dang o che do bao ve, tat ca nguoi choi se an toan.
    if game_state.protection:
        new_countdown = game_state.countdown - dt
        return {"countdown": new_countdown, "protection": True if new_countdown >= 0.0 else False}
    
    
    # Kiem tra xem TheCat co bat duoc ai khong.
    mouser = game_state.players[game_state.TheCat_id]
    for player_id, player in game_state.players.items():
        if not player_id == game_state.TheCat_id:
            dx = player["position"][0] - mouser["position"][0]
            dy = player["position"][1] - mouser["position"][1]
            distance_squared = dx * dx + dy * dy
            # Tat ca nguoi choi sau khi co nguoi bi bat se an toan trong 5s.
            if distance_squared == 0:
                print(f"{player['name']} has been caught")
                return {"TheCat_id": player_id, "protection": True, "countdown": 5.0}
    return {}


# "MOVE" event handler
def on_move(player_id, new_position, **kwargs):
    return {"players": {player_id: {"position": new_position}}}


# Khoi tao backend.
backend = Backend(initial_game_state, time_step, event_handlers={"MOVE": on_move})

# "JOIN" event handler
def on_join(player_name, game_state, client_address, **kwargs):
    print(f"{player_name} joined.")
    player_id = len(game_state.players)
    # Bao cho client biet la player da gia nhap game thanh cong.
    backend.server.dispatch_event("PLAYER_CREATED", player_id, target_client=client_address)
    return {
        # Tao player
        "players": {player_id: {"name": player_name, "position": (random.randrange(0, WINDOWWIDTH, CELLSIZE), random.randrange(0, WINDOWWIDTH, CELLSIZE))}},
        # Player nao vao tro choi dau tien se la TheCat
        "TheCat_id": player_id if game_state.TheCat_id is None else game_state.TheCat_id,
    }


# Register the "JOIN" handler.
backend.game_state_machine.register_event_handler("JOIN", on_join)

### MAIN PROCESS ###

if __name__ == "__main__":
    main()
    