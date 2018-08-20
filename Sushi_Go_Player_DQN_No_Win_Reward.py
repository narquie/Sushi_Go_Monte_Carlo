import Sushi_Go_Monte_Carlo_Class as SG
import Sushi_Go_Player_DQN_Agent as Agent
import numpy as np
from collections import defaultdict
import sys
import pickle
import random
import torch
import numpy as np
from collections import deque
import math
import matplotlib.pyplot as plt
# Import file with instructions for AI agents
agent = Agent.Agent(state_size=58, action_size=13, seed=0)
agent.qnetwork_local.load_state_dict(torch.load('checkpoint_no_win_reward_or_discount.pth'))
# Taking an action as a player
def take_action(new_game):
    cards = new_game.players_list[0].player_hand
    # Displays cards in hand
    for i in cards:
        print("Cards in hand:")
        print("Name of Card")
        print(i.name)
        print("Action categorized as")
        print(i.number)
    # Displays the chopstick action if it is in front of you
    if new_game.players_list[0].chopstick:
        print("Chopstick available! Action categorized as:")
        print("13")
    # The board state, with information on all players
    print("Current Board State")
    board_state_raw = new_game.report_board_state()
    print(board_state_raw)
    print(len(board_state_raw))
    count = 0
    i_previous = 0
    # Displays the board state per player (human is player0)
    for i in range(14,len(board_state_raw)+1,14):
        player_board_state = board_state_raw[i_previous:i]
        print("Player "+ str(count)+ " board state:")
        print("Egg, Salmon, Squid Nigiri; Tempura, Sashimi; Dumpling, Chopsticks, Wasabi; Pudding, Maki Roll 1-3; Maki rolls total, score")
        print(player_board_state)
        i_previous = i
        count += 1
    # Takes action inputs for the player
    var = float(input("What is your action?: "))
    if int(math.ceil(var)) == int(var):
        var = int(var)
    legal_actions_player0 = new_game.players_list[0].legal_actions()
    # Must be legal move
    while var not in legal_actions_player0:
        var = float(input("Please enter a correct action.: "))
        if int(math.ceil(var)) == int(var):
            var = int(var)
    # Multiple actions for chopsticks
    if var == 13:
        legal_actions_player0.remove(var)
        var_chopstick_1 = float(input("Please enter first chopstick action: "))
        if int(math.ceil(var_chopstick_1)) == int(var_chopstick_1):
            var_chopstick_1 = int(var_chopstick_1)
        while var_chopstick_1 not in legal_actions_player0:
            var_chopstick_1 = float(input("Please enter a correct action.: "))
            if int(math.ceil(var_chopstick_1)) == int(var_chopstick_1):
                var = int(var_chopstick_1)
        count = 0
        for i in new_game.players_list[0].player_hand:
            if i.number == var_chopstick_1:
                count += 1
        if len(list(legal_actions_player0)) > 1 and count < 2:
            legal_actions_player0.remove(var_chopstick_1)
        var_chopstick_2 = float(input("Please enter second chopstick action: "))
        if int(math.ceil(var_chopstick_2)) == int(var_chopstick_2):
            var_chopstick_2 = int(var_chopstick_2)
        while var_chopstick_2 not in legal_actions_player0:
            var_chopstick_2 = float(input("Please enter a correct action.: "))
            if int(math.ceil(var_chopstick_2)) == int(var_chopstick_2):
                var_chopstick_2 = int(var_chopstick_2)
        temp_action_list = [var_chopstick_1,var_chopstick_2]
        new_game.players_list[0].play_cards_chopstick(temp_action_list)
    else:
        new_game.players_list[0].play_a_card(var)
    return None
# Taking an action as an AI
def bot_action(new_game,state):
    # Taking the most beneficial legal move
    for index, i in enumerate(new_game.players_list[1:]):
        legal_actions_bot = i.legal_actions()
        state[len(state)-2] = i.score
        action = agent.act(state,.01,legal_actions_bot)
        # Chopsticks action
        if action == 13:
            legal_actions_bot.remove(action)
            action1 = agent.act(state,.01,legal_actions_bot)
            count = 0
            for j in i.player_hand:
                if j.number == action1:
                    count += 1
            if len(list(legal_actions_bot)) > 1 and count < 2:
                legal_actions_bot.remove(action1)
            action2 = agent.act(state,.01,legal_actions_bot)
            temp_action_list = [action1,action2]
            i.play_cards_chopstick(temp_action_list)
        else:
            i.play_a_card(action)
    return None
# Game object
new_game = SG.Deck("original",4)
for h in range(0,3):
    for i in range(0,9):
        # Initial state
        state = new_game.report_board_state()
        state.append(0)
        state.append(h*9+i+1)
        state = np.array(state)
        take_action(new_game)
        bot_action(new_game,state)
        # Board cleanup
        for j in new_game.players_list:
            j.take_cards_from_other_player()
    # Board cleanup
    for j in new_game.players_list:
        j.wasabi = False
        j.chopstick = False
    # Board cleanup
    new_game.clear_board_state()
new_game.score_pudding()
print(new_game.declare_winner())
