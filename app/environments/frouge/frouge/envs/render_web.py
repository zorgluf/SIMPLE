from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .frouge import FlammeRougeEnv

from nicegui import ui
import threading

from .classes import *

STOP_STEP_MODE = True

model_data = {
    "game_env": None
}

def _get_player_color(n: int):
    if n == 1:
        return "red-10"
    if n == 2:
        return "blue-10"
    if n == 3:
        return "green-10"
    if n == 4:
        return "yellow-10"
    if n == 5:
        return "purple-10"
    
def _get_rider_color(board, c, r):
    r = _get_rider(board, c, r)
    if r != "-":
        return _get_player_color(int(r[0]))
    return ""

def _get_rider(board, c, r):
    rider = board.get_cell_display(c,r)
    if rider == "":
        rider = "-"
    return rider

def _on_select_sprinteur_deck():
    action = model_data["game_env"].ACTION_SELECT_SPRINTEUR_DECK
    model_data["game_env"]._interactive_action_result = action

def _on_select_rouleur_deck():
    action = model_data["game_env"].ACTION_SELECT_ROULEUR_DECK
    model_data["game_env"]._interactive_action_result = action

def _on_card_selected(card):
    action = ALL_CARDS.index(card)
    model_data["game_env"]._interactive_action_result = action

def _on_click_cell_listener(c, r):
    if model_data["game_env"].phase == 0:
        if model_data["game_env"].board.get_cell(c,r) == CS:
            if model_data["game_env"].board.get_cell_display(c,r) == "":
                action = c*3 + r + len(ALL_CARDS) + 2
                model_data["game_env"]._interactive_action_result = action

@ui.refreshable
def _gui_board(board: Board):
    if board != None:
        cell_per_line = 40
        for i in range(3):
            with ui.grid(rows=3, columns=cell_per_line).classes("gap-0"):
                for r in range(3):
                    for c in range(cell_per_line):
                        cell = board.get_cell(c+cell_per_line*i,r)
                        if cell == CV:
                            bg_c = "transparent"
                        if cell == CC: # climb
                            bg_c = "red" # light red
                        if cell == CD: # descent
                            bg_c = "blue" # blue
                        if cell == CP: # paved
                            bg_c = "yellow" # yellow
                        if cell == CSU: # supply cell
                            bg_c = "cyan" # cyan
                        if cell == CS: # start
                            bg_c = "grey-6" # gray
                        if cell == CF: # finish
                            bg_c = "grey-6" # gray
                        if cell == CN: #normal
                            bg_c = "grey-4" # black
                        rider = _get_rider(board,c+cell_per_line*i,r)
                        if model_data["game_env"].phase == 0 and cell == CS and rider == "-":
                            ui.button("-", on_click=lambda x=(c+cell_per_line*i,r): _on_click_cell_listener(x[0],x[1]))
                        else:
                            ui.label(rider).classes("border text-center self-center").tailwind.background_color(bg_c).margin("0").width("10").text_color(_get_rider_color(board,c,r))
            #blank line
            ui.label("_")

@ui.refreshable
def _gui_players(env: FlammeRougeEnv):
    with ui.row():
        ui.label("Last played cards")
        with ui.grid(columns=6):
            ui.label("-")
            for p in env.board.players:
                ui.label(f"Player {p.name}").tailwind.text_color(_get_player_color(p.n))
            ui.label("Rouleur")
            for p in env.board.players:
                card = env.last_played_cards[(p,"r")]
                if card != None:
                    ui.label(card.name).tailwind.text_color(_get_player_color(p.n))
                else:
                    ui.label("-")
            ui.label("Sprinter")
            for p in env.board.players:
                card = env.last_played_cards[(p,"s")]
                if card != None:
                    ui.label(card.name).tailwind.text_color(_get_player_color(p.n))
                else:
                    ui.label("-")
    pass

@ui.refreshable
def _gui_human_actions(env: FlammeRougeEnv):
    with ui.row().bind_visibility_from(env, '_interactive_action_on'):
        with ui.column():
            ui.label("").bind_text_from(env,"current_player_num",backward=lambda x: f"Human player {x+1} turn")
            ui.label("").bind_visibility_from(env,"phase",backward=lambda x: x == 0).bind_text_from(env.current_player.s_position,"col",backward=lambda x:  "Place your Sprinteur (click on a starting cell)" if x == -1 else "Place your Rouleur (click on a starting cell)")
            with ui.row().bind_visibility_from(env,"phase",backward=lambda p: p==1):
                ui.button("Choose Sprinter deck", on_click=_on_select_sprinteur_deck)
                ui.button("Choose Rouleur deck", on_click=_on_select_rouleur_deck)
            with ui.row().bind_visibility_from(env,"phase",backward=lambda p: p==2):
                if env.current_player.hand_order[env.hand_number] == 'r':
                    ui.label("Choose Rouleur card")
                    hand_cards = env.current_player.r_hand
                else:
                    ui.label("Choose Sprinter card")
                    hand_cards = env.current_player.s_hand
                for c in hand_cards.cards:
                    ui.button(f"{c.name}", on_click=lambda c=c: _on_card_selected(c))
    

def render_web(env: FlammeRougeEnv):

    if env._web_thread == None:
        #TODO : to remove
        global model_data
        model_data["game_env"] = env

        _gui_board(env.board)
        with ui.row():
            ui.label("").bind_text_from(env, "turns_taken", backward=lambda x: f"Turn : {x}")
            ui.label("").bind_text_from(env, "phase", backward=lambda x: "Rider placement" if x == 0 else "Deck choice" if x == 1 else "Card choice")
        _gui_players(env)
        _gui_human_actions(env)

        env._web_thread = threading.Thread(target=lambda: ui.run(reload=False))
        env._web_thread.daemon = True
        env._web_thread.start()
    else:
        _gui_board.refresh(env.board)
        _gui_human_actions.refresh(env)
        _gui_players.refresh(env)
    

    

    
