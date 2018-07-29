import Sushi_Go_Monte_Carlo_Class as SG
import numpy as np
from collections import defaultdict
import sys
import pickle
def expected_sarsa(num_episodes, alpha, gamma=.9999, epsilon=1,epsilon_decay=.9999,eps_min=.2):
    def epsilon_greedy(Q_temp,state,epsilon,actions):
        probs = [1-epsilon, epsilon]
        action = np.random.choice(np.arange(2), p=probs)
        temp_list = [0]*13
        # Making sure legal actions are taken
        for i in actions:
            if i < 10 or i == 13:
                temp_list[i-1] = (Q_temp[(state)][i-1]) + 1000
            elif i > 10:
                temp_number = int(round((i-10)*10)+10-2)
                temp_list[temp_number] = (Q_temp[(state)][temp_number])  + 1000
        # 1 - Epsilon chance of taking "best" action
        if action == 0:
            action = np.argmax(temp_list)
            if action == 9:
                action = 10.1
            elif action == 10:
                action = 10.2
            elif action == 11:
                action = 10.3
            else:
                action += 1
        # Epsilon chance to generate random action
        else:
            np.random.shuffle(actions)
            action = actions[0]
        return(action)
    def episode_create(new_game,Q,epsilon):
        def run_a_round(new_game,Q,epsilon):
            # initial state
            if new_game.round == 1:
                state = [0,0,0,0]
            else:
                state = new_game.report_scores()
            for i in range(0,9):
                new_game.player_actions = []
                # Running for each player
                for index, j in enumerate(new_game.players_list):
                    new_set = j.legal_actions()
                    # Regular action
                    action = epsilon_greedy(Q,state[index],epsilon,list(new_set))
                    # Chopstick actions
                    if action == 13:
                        new_set.remove(action)
                        action1 = epsilon_greedy(Q,state[index],epsilon,list(new_set))
                        count = 0
                        for k in j.player_hand:
                            if k.number == action1:
                                count += 1
                        if len(list(new_set)) > 1 and count < 2:
                            new_set.remove(action1)
                        action2 = epsilon_greedy(Q,state[index],epsilon,list(new_set))
                        temp_action_list = [action1,action2]
                        j.play_cards_chopstick(temp_action_list)
                    else:
                        j.play_a_card(action)
                    # Give actions correct index
                    if action <10 or action == 13:
                        action = action - 1
                    elif action > 10:
                        action = int(round((action-10)*10)+10-2)
                    reward = j.reward
                    next_state = j.score
                    temp_num = 0
                    # Calculate expected sarsa based on temporal difference
                    for i in range(0,13):
                        temp_num += Q[next_state][i]*(epsilon/13)
                        temp_num += Q[next_state][np.argmax(Q[next_state])]*(1-epsilon)
                    Q[state[index]][action] = Q[state[index]][action]+alpha*(reward + gamma*temp_num - Q[state[index]][action])
                    new_game.player_actions_current.append(action)
                    new_game.player_actions_total.append(action)
                # Board cleanup
                for j in new_game.players_list:
                    j.take_cards_from_other_player()
                state = new_game.report_scores()
            # Board cleanup
            for i in new_game.players_list:
                i.wasabi = False
                i.chopstick = False
            new_game.clear_board_state()
            return(Q)
        # Run three rounds and winner
        Q = run_a_round(new_game,Q,epsilon)
        new_game.deal_hand()
        Q = run_a_round(new_game,Q,epsilon)
        new_game.deal_hand()
        Q = run_a_round(new_game,Q,epsilon)
        state = new_game.report_scores()
        new_game.score_pudding()
        # Parsing winner and relevant rewards
        winner_index = new_game.declare_winner()
        next_state = new_game.report_scores()
        reward = [-100]*4
        if isinstance(winner_index, list):
            for i in winner_index:
                next_state[i] += 100
                reward[i] = 100
        else:
            next_state[winner_index] += 100
            reward[winner_index] = 100
        # Final action / reward before game end
        for index, i in enumerate(new_game.players_list):
            temp_num = 0
            for i in range(0,13):
                temp_num += Q[next_state[index]][i]*(epsilon/13)
                temp_num += Q[next_state[index]][np.argmax(Q[next_state[index]])]*(1-epsilon)
            extra = alpha*(reward[index] + gamma*temp_num - Q[state[index]][new_game.player_actions_current[index]])
            Q[state[index]][new_game.player_actions_current[index]] += extra
        return Q
    # Initialize empty dictionary of arrays
    Q = defaultdict(lambda: np.zeros(13))
    # Loop over episodes
    for i_episode in range(1, num_episodes+1):
        # Monitor progress
        new_game = SG.Deck("original",4)
        # Decay epsilon
        epsilon = max(epsilon*epsilon_decay,eps_min)
        Q = episode_create(new_game,Q,epsilon,)
        if i_episode % 1000 == 0:
            # Tracking AI actions
            print("\rEpisode {}/{}.".format(i_episode, num_episodes), end="")
            print("\n"+str(new_game.player_actions_total))
            print(len(new_game.player_actions_total))
    return Q
# Lots of trials with little adjustment for actions taken
Q = expected_sarsa(1000000, .001)
Q = dict(Q)
output = open('Q_values.pkl', 'wb')
pickle.dump(Q,output)
output.close()
