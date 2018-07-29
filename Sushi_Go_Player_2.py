import Sushi_Go_Monte_Carlo_Class as SG
import numpy as np
from collections import defaultdict
import sys
import pickle
import math
# Import file with instructions for AI agents
Q_input = open('Q_values.pkl', 'rb')
Q = pickle.load(Q_input)
Q_input.close()
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
def bot_action(new_game,Q,state):
    # Taking the most beneficial legal move
    def max_Q(state,Q_temp,set_actions):
        temp_list = [0]*13
        for i in set_actions:
            if i < 10 or i == 13:
                temp_list[i-1] = (Q_temp[state][i-1]) + 1000
            elif i > 10:
                temp_number = int(round((i-10)*10)+10-2)
                temp_list[temp_number] = (Q_temp[state][temp_number])  + 1000
        action = np.argmax(temp_list)
        if action == 9:
            action = 10.1
        elif action == 10:
            action = 10.2
        elif action == 11:
            action = 10.3
        else:
            action += 1
        return(action)
    # Going through each bot, take the best action
    for index, i in enumerate(new_game.players_list[1:]):
        legal_actions_bot = i.legal_actions()
        new_state = state[index]
        action = max_Q(new_state,Q,legal_actions_bot)
        # Chopsticks action
        if action == 13:
            print(action)
            legal_actions_bot.remove(action)
            action1 = max_Q(new_game,Q,legal_actions_bot)
            count = 0
            for j in i.player_hand:
                if j.number == action1:
                    count += 1
            if len(list(legal_actions_bot)) > 1 and count < 2:
                legal_actions_bot.remove(action1)
            action2 = max_Q(new_state,Q,legal_actions_bot)
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
        if new_game.round == 1:
            state = [0,0,0,0]
        else:
            state = new_game.report_scores()
        take_action(new_game)
        bot_action(new_game,Q,state)
        # Board cleanup
        for j in new_game.players_list:
            j.take_cards_from_other_player()
    # Board cleanup
    for j in new_game.players_list:
        j.wasabi = False
        j.chopstick = False
    # Board cleanup
    new_game.clear_board_state()
print(new_game.declare_winner())
