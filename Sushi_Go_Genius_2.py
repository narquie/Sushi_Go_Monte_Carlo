import Sushi_Go_Monte_Carlo_Class as SG
import numpy as np
from collections import defaultdict
import sys
import pickle
def mc_control(num_episodes, alpha, gamma=.9999, epsilon=1,epsilon_decay=.9999,eps_min=.2):
    def epsilon_greedy(Q_temp,state,epsilon,actions):
        probs = [1-epsilon, epsilon]
        action = np.random.choice(np.arange(2), p=probs)
        temp_list = [0]*13
        for i in actions:
            if i < 10 or i == 13:
                temp_list[i-1] = (Q_temp[(state)][i-1]) + 1000
            elif i > 10:
                temp_number = int(round((i-10)*10)+10-2)
                temp_list[temp_number] = (Q_temp[(state)][temp_number])  + 1000
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
        else:
            np.random.shuffle(actions)
            action = actions[0]
        return(action)
    def episode_create(new_game,Q,epsilon):
        def run_a_round(new_game,Q,epsilon):
            if new_game.round == 1:
                state = [0,0,0,0]
            else:
                state = new_game.report_scores()
            for i in range(0,9):
                new_game.player_actions = []
                for index, j in enumerate(new_game.players_list):
                    new_set = j.legal_actions()
                    action = epsilon_greedy(Q,state[index],epsilon,list(new_set))
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
                    if action <10 or action == 13:
                        action = action - 1
                    elif action > 10:
                        action = int(round((action-10)*10)+10-2)
                    reward = j.reward
                    next_state = j.score
                    temp_num = 0
                    for i in range(0,13):
                        temp_num += Q[next_state][i]*(epsilon/13)
                        #print(temp_list)
                        temp_num += Q[next_state][np.argmax(Q[next_state])]*(1-epsilon)
                    Q[state[index]][action] = Q[state[index]][action]+alpha*(reward + gamma*temp_num - Q[state[index]][action])
                    new_game.player_actions_current.append(action)
                    new_game.player_actions_total.append(action)
                for j in new_game.players_list:
                    j.take_cards_from_other_player()
                state = new_game.report_scores()
            for i in new_game.players_list:
                i.wasabi = False
                i.chopstick = False
            new_game.clear_board_state()
            return(Q)
        Q = run_a_round(new_game,Q,epsilon)
        new_game.deal_hand()
        Q = run_a_round(new_game,Q,epsilon)
        #for i in episode_new:
        #    episode.append(i)
        new_game.deal_hand()
        Q = run_a_round(new_game,Q,epsilon)
        #for i in episode_new:
        #    episode.append(i)
        state = new_game.report_scores()
        new_game.score_pudding()
        winner_index = new_game.declare_winner()
        #print(winner_index)
        next_state = new_game.report_scores()
        reward = [-100]*4
        if isinstance(winner_index, list):
            for i in winner_index:
                next_state[i] += 100
                reward[i] = 100
        else:
            next_state[winner_index] += 100
            reward[winner_index] = 100
        for index, i in enumerate(new_game.players_list):
            temp_num = 0
            for i in range(0,13):
                temp_num += Q[next_state[index]][i]*(epsilon/13)
                #print(temp_list)
                temp_num += Q[next_state[index]][np.argmax(Q[next_state[index]])]*(1-epsilon)
            #print(temp_num)
            #print(Q[state[index]][new_game.player_actions[index]])
            extra = alpha*(reward[index] + gamma*temp_num - Q[state[index]][new_game.player_actions_current[index]])
            #print(extra)
            Q[state[index]][new_game.player_actions_current[index]] += extra

        return Q
    # initialize empty dictionary of arrays
    Q = defaultdict(lambda: np.zeros(13))
    policy = defaultdict(lambda: np.zeros(13))
    # loop over episodes
    for i_episode in range(1, num_episodes+1):
        # monitor progress
        new_game = SG.Deck("original",4)
        ## TODO: complete the function
        epsilon = max(epsilon*epsilon_decay,eps_min)
        Q = episode_create(new_game,Q,epsilon,)
        if i_episode % 1000 == 0:
            print("\rEpisode {}/{}.".format(i_episode, num_episodes), end="")
            print("\n"+str(new_game.player_actions_total))
            print(len(new_game.player_actions_total))
            #sys.stdout.flush()
    return Q
Q = mc_control(1000000, .001)
#policy, Q = mc_control(1000, .01)
Q = dict(Q)
output = open('Q_values.pkl', 'wb')
pickle.dump(Q,output)
output.close()
#input = open('Q_values.pkl', 'rb')
#Q_new = pickle.load(input)
#input.close()
#print(Q_new)
