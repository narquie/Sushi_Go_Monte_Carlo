import Sushi_Go_Monte_Carlo_Class as SG
import numpy as np
from collections import defaultdict
import sys
import pickle
def mc_control(num_episodes, alpha, gamma=.9999, epsilon=1,epsilon_decay=.9999,eps_min=.05):
    def epsilon_greedy(Q_temp,state,epsilon,actions):
        probs = [1-epsilon, epsilon]
        action = np.random.choice(np.arange(2), p=probs)
        temp_list = [0]*13
        for i in actions:
            if i < 10 or i == 13:
                temp_list[i-1] = (Q_temp[tuple(state)][i-1]) + 1000
            elif i > 10:
                temp_number = int(round((i-10)*10)+10-2)
                temp_list[temp_number] = (Q_temp[tuple(state)][temp_number])  + 1000
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
    def episode_create(new_game,Q,epsilon,policy):
        def run_a_round(new_game,Q,epsilon,policy):
            state = [0,0,0,0]
            episode = []
            for i in range(0,9):
                for j in new_game.players_list:
                    new_set = j.legal_actions()
                    action = epsilon_greedy(Q,state,epsilon,list(new_set))
                    if action == 13:
                        new_set.remove(action)
                        action1 = epsilon_greedy(Q,state,epsilon,list(new_set))
                        if len(list(new_set)) > 1:
                            new_set.remove(action1)
                        action2 = epsilon_greedy(Q,state,epsilon,list(new_set))
                        temp_action_list = [action1,action2]
                        j.play_cards_chopstick(temp_action_list)
                    else:
                        j.play_a_card(action)
                    if action <10 or action == 13:
                        action = action - 1
                    elif action > 10:
                        action = int(round((action-10)*10)+10-2)
                    policy[tuple(state)] = action
                    reward = j.reward
                    episode.append((state,action,reward))
                for j in new_game.players_list:
                    j.take_cards_from_other_player()
                state = new_game.report_scores()
            for i in new_game.players_list:
                i.wasabi = False
                i.chopstick = False
            new_game.clear_board_state()
            return(episode,policy)
        episode, policy = run_a_round(new_game,Q,epsilon,policy)
        new_game.deal_hand()
        episode_new, policy = run_a_round(new_game,Q,epsilon,policy)
        for i in episode_new:
            episode.append(i)
        new_game.deal_hand()
        episode_new, policy = run_a_round(new_game,Q,epsilon,policy)
        for i in episode_new:
            episode.append(i)
        new_game.score_pudding()
        winner_index = new_game.declare_winner()
        #print(winner_index)
        state = episode[-1][0]
        reward = [-100]*4
        if isinstance(winner_index, list):
            for i in winner_index:
                state[i] += 100
                reward[i] = 100
        else:
            state[winner_index] += 100
            reward[winner_index] = 100
        actions = []
        for i in range(-4,0):
            actions.append(episode[len(episode)+i][1])
        for i in range(0,new_game.num_players):
            episode.append((state,actions[i],reward[i]))
        return episode,policy
    # initialize empty dictionary of arrays
    Q = defaultdict(lambda: np.zeros(13))
    policy = defaultdict(lambda: np.zeros(13))
    # loop over episodes
    for i_episode in range(1, num_episodes+1):
        # monitor progress
        new_game = SG.Deck("original",4)
        if i_episode % 1000 == 0:
            print("\rEpisode {}/{}.".format(i_episode, num_episodes), end="")
            print("\n"+str(actions))
            print(len(actions))
            #sys.stdout.flush()

        ## TODO: complete the function
        epsilon = max(epsilon*epsilon_decay,eps_min)
        # generate an episode
        episode,policy = episode_create(new_game,Q,epsilon,policy)
        # obtain the states, actions, and rewards
        states, actions, rewards = zip(*episode)
        # prepare for discounting
        discounts = np.array([gamma**i for i in range(len(rewards)+1)])
        # update the sum of the returns, number of visits, and action-value
        # function estimates for each state-action pair in the episode
        for i, state in enumerate(states):
            reward = sum(rewards[i:]*discounts[:-(1+i)])
            Q[tuple(state)][actions[i]] = Q[tuple(state)][actions[i]]+alpha*(reward - Q[tuple(state)][actions[i]])
    return policy, Q
#policy, Q = mc_control(1000000, .01)
policy, Q = mc_control(1000, .01)
Q = dict(Q)
output = open('Q_values.pkl', 'wb')
pickle.dump(Q,output)
output.close()
#input = open('Q_values.pkl', 'rb')
#Q_new = pickle.load(input)
#input.close()
#print(Q_new)
