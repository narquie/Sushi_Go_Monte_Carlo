import numpy as np
# The card classs, used to keep track of cards,
# placed in a Deck object, can have multiple
# held by Player object
class Player(object):
    def __init__(self,Deck,position):
        # Deck keeps track of overall board state and deck
        self.deck = Deck
        # Cards in hand
        self.player_hand = None
        # Position in circle (0 next to 1 and deck.num_players-1)
        self.player_position = position
        # Deal first hand
        self.init_player_hand()
        # Card recently in front of player
        self.played_card = None
        # Cards played before
        self.cards_in_play = []
        # Cards set aside as part of draft
        self.awaiting_hand = None
        # Score of player
        self.score = 0
        # Scored reward
        self.reward = 0
        # Number of maki rolls
        self.maki_rolls = 0
        # Wasabi or not
        self.wasabi = False
        # Chopstick or not
        self.chopstick = False
    # Deal first hand
    def init_player_hand(self):
        # The board deals a hand
        self.player_hand = self.deck.deal_hand()
    # Add score based on self.played_card
    def add_score(self,card_added):
        temp_list = []
        counter = 1
        if self.cards_in_play is not None:
            for i in self.cards_in_play:
                if card_added.number == i.number:
                    counter += 1
        marginal = card_added.score(counter)
        if self.wasabi and card_added.number < 4:
            self.score += 3*marginal
            self.reward = 3*marginal
            self.wasabi = False
        else:
            self.score += marginal
            self.reward = marginal
    # Play a card from hand
    def play_a_card(self,action):
        for i in self.player_hand:
            if i.number == action:
                if i.number == 8:
                    self.wasabi = True
                if i.number == 7:
                    self.chopstick = True
                self.played_card = i
                self.player_hand.remove(i)
                self.add_score(self.played_card)
                self.cards_in_play.append(self.played_card)
                self.hand_cards_to_next_player()
                break
        return None
    def play_cards_chopstick(self,actions):
        original_score = self.score
        self.chopstick = False
        for i in self.cards_in_play:
            if i.number == 7:
                chopstick_card = i
                break
        for j in actions:
            for i in self.player_hand:
                if i.number == j:
                    if i.number == 8:
                        self.wasabi = True
                    if i.number == 7:
                        self.chopstick = True
                    self.played_card = i
                    self.player_hand.remove(i)
                    self.add_score(self.played_card)
                    self.cards_in_play.append(self.played_card)
                    break
        self.reward = self.score - original_score
        self.player_hand.append(chopstick_card)
        self.cards_in_play.remove(chopstick_card)
        self.hand_cards_to_next_player()
        return(None)
    # Set down awaiting_hand
    def hand_cards_to_next_player(self):
        if self.player_position != (self.deck.num_players-1):
            self.deck.players_list[self.player_position+1].awaiting_hand = self.player_hand
        elif self.player_position == self.deck.num_players-1:
            self.deck.players_list[0].awaiting_hand = self.player_hand
    # Pick up awaiting_hand
    def take_cards_from_other_player(self):
        if self.awaiting_hand is not None:
            self.player_hand = self.awaiting_hand
        self.awaiting_hand = None
        return None
    def legal_actions(self):
        action_set = set()
        for i in self.player_hand:
            action_set.add(i.number)
        if self.chopstick and len(self.player_hand) > 1:
            action_set.add(13)
        return(action_set)
    # Replenish decks without puddings
    def give_back_cards(self):
        temp_list = []
        temp_cards_in_play = []
        for i in self.cards_in_play:
            if i.number != 9:
                temp_list.append(i)
            else:
                temp_cards_in_play.append(i)
        self.cards_in_play = temp_cards_in_play
        self.deck.take_back_cards(temp_list)
        return None
class Card(object):
    def __init__(self,number):
        # A number for the card for initialization
        self.number = number
        # The card's name per Sushi-Go! Party
        self.name = None
        # Score per card Nigiri for the moment
        self.marginal_score = None
        # Number of rolls for roll cards
        self.number_rolls = None
        # Score for a set
        self.set_bonus = None
        # Number of cards needed for a set of the card
        self.complete_set = None
        # Special card? Perhaps needed to be changed
        self.special_card = None
        # Whether or not the card is dessert (stays on the board)
        self.dessert_card = None
        # If the card scores separately on each number
        self.marginal_set_bonus = None
        self.init_card()
    # Define card characteristics
    def init_card(self):
        if self.number == 1:
            self.name = "Egg Nigiri"
            self.marginal_score = 1
        elif self.number == 2:
            self.name = "Salmon Nigiri"
            self.marginal_score = 2
        elif self.number == 3:
            self.name = "Squid Nigiri"
            self.marginal_score = 3
        elif self.number == 4:
            self.name = "Tempura"
            self.set_bonus = 5
            self.complete_set = 2
        elif self.number == 5:
            self.name = "Sashimi"
            self.set_bonus = 10
            self.complete_set = 3
        elif self.number == 6:
            self.name = "Dumpling"
            self.marginal_set_bonus = [0,1,2,3,4,5]
        elif self.number == 7:
            self.name = "Chopsticks"
            self.special_card = True
        elif self.number == 8:
            self.name = "Wasabi"
            self.special_card = True
        elif self.number == 9:
            self.name = "Pudding"
            self.dessert_card = True
        elif self.number == 10.1:
            self.name = "Maki Roll"
            self.number_rolls = 1
        elif self.number == 10.2:
            self.name = "Maki Roll"
            self.number_rolls = 2
        elif self.number == 10.3:
            self.name = "Maki Roll"
            self.number_rolls = 3
        return None
    def score(self,number):
        # Add score to players' score
        if self.dessert_card or self.special_card or self.number_rolls is not None:
            return(0)
        if self.set_bonus is None and self.marginal_set_bonus is None:
            return self.marginal_score
        elif self.marginal_set_bonus is not None:
            if number < len(self.marginal_set_bonus):
                return self.marginal_set_bonus[number]
            else:
                return(0)
        elif self.set_bonus is not None:
            if number % self.complete_set == 0:
                return self.set_bonus
            else:
                return(0)

# Initializes deck and rest of objects
class Deck(object):
    def __init__(self,setup, num_players):
        self.deck_cards = None
        self.setup = setup
        self.num_players = num_players
        self.players_list = []
        if self.setup == "original":
            self.init_deck_cards_original()
        self.init_players()
        self.round = 1
    def init_players(self):
        # Create the players
        for i in range(0,self.num_players):
            self.players_list.append(Player(self,i))
        return None
    def init_deck_cards_original(self):
        self.deck_cards = []
        for i in range(1,60):
            if i<=4:
                self.deck_cards.append(Card(1))
            elif i <= 9:
                self.deck_cards.append(Card(2))
            elif i <= 12:
                self.deck_cards.append(Card(3))
            elif i <= 20:
                self.deck_cards.append(Card(4))
            elif i <= 28:
                self.deck_cards.append(Card(5))
            elif i <= 36:
                self.deck_cards.append(Card(6))
            elif i <= 39:
                self.deck_cards.append(Card(7))
            elif i <= 42:
                self.deck_cards.append(Card(8))
            elif i <= 47:
                self.deck_cards.append(Card(9))
            elif i <= 51:
                self.deck_cards.append(Card(10.1))
            elif i <= 56:
                self.deck_cards.append(Card(10.2))
            elif i < 60:
                self.deck_cards.append(Card(10.3))
        return None
    # Deals cards when called
    def deal_hand(self):
        np.random.shuffle(self.deck_cards)
        temp_deck = self.deck_cards[0:9]
        self.deck_cards = self.deck_cards[9:]
        return(temp_deck)
    # Add dessert per round
    def add_dessert(self):
        if self.round == 2:
            for i in range(0,3):
                self.deck_cards.append(Card(9))
        if self.round == 3:
            for i in range(0,2):
                self.deck_cards.append(Card(9))
        return None
    # Take cards back in deck
    def take_back_cards(self,hand):
        for i in hand:
            self.deck_cards.append(i)
        return None
    def report_scores(self):
        temp_list = []
        for i in self.players_list:
            temp_list.append(i.score)
        return(temp_list)
    # Declares the current board state with num cards, maki rolls, score
    def report_board_state(self):
        temp_list_cards = [0]*12
        end_list_cards = []
        for i in self.players_list:
            current_list_cards = temp_list_cards
            for j in i.cards_in_play:
                if j.number < 10:
                    current_list_cards[j.number-1] += 1
                else:
                    num_temp = int(round((j.number-10)*10)+10-2)
                    current_list_cards[num_temp] += 1
            current_list_cards.append(i.maki_rolls)
            current_list_cards.append(i.score)
            for j in current_list_cards:
                end_list_cards.append(j)
        return(end_list_cards)
    # Set up for next round
    def clear_board_state(self):
        for i in self.players_list:
            for j in i.cards_in_play:
                if j.number == 10.1:
                    i.maki_rolls += 1
                if j.number == 10.2:
                    i.maki_rolls += 2
                if j.number == 10.3:
                    i.maki_rolls += 3
        # Score Maki
        maki_list = []
        for i in self.players_list:
            maki_list.append(i.maki_rolls)
        def max_maki_func(maki_list):
            max_maki = max(maki_list)
            if max_maki == 0:
                return(None)
            count = 0
            index_list = []
            for index, i in enumerate(maki_list):
                if i == max_maki:
                    index_list.append(index)
            return(index_list)
        max_maki_index = max_maki_func(maki_list)
        if max_maki_index is not None:
            for i in max_maki_index:
                self.players_list[i].score += 6
                self.players_list[i].reward = 6
                maki_list[i] = -1
        max_maki_index = max_maki_func(maki_list)
        if max_maki_index is not None:
            for i in max_maki_index:
                self.players_list[i].score += 3
                self.players_list[i].reward = 3
                maki_list[i] = -1
        for i in self.players_list:
            i.give_back_cards()
            i.maki_rolls = 0
        # Make another round
        self.round += 1
        # Add relevant amount of dessert
        self.add_dessert()
        for i in self.players_list:
            i.init_player_hand()
    # Score pudding at end of game
    def score_pudding(self):
        pudding_list = [0]*self.num_players
        for index, i in enumerate(self.players_list):
            for j in i.cards_in_play:
                if j.number == 9:
                    pudding_list[index] += 1
        max_puddy = max(pudding_list)
        index_list = []
        for index, i in enumerate(pudding_list):
            if i == max_puddy:
                index_list.append(index)
        max_puddy_list = index_list
        for i in max_puddy_list:
            self.players_list[i].score += 6
            self.players_list[i].reward = 6
        min_puddy = min(pudding_list)
        index_list = []
        for index, i in enumerate(pudding_list):
            if i == min_puddy:
                index_list.append(index)
        min_puddy_list = index_list
        for i in min_puddy_list:
            self.players_list[i].score -= 6
            self.players_list[i].reward = -6
        return None
    def declare_winner(self):
        temp_list = []
        for i in self.players_list:
            temp_list.append(i.score)
        max_score = max(temp_list)
        max_index = []
        for index,i in enumerate(temp_list):
            if i == max_score:
                max_index.append(index)
        if len(max_index) > 1:
            tiebreaker_list = [0]*self.num_players
            for i in max_index:
                count = 0
                for j in self.players_list[i].cards_in_play:
                    if j.number == 9:
                        count += 1
                tiebreaker_list[i] = count
            max_tiebreaker = max(tiebreaker_list)
            tiebreaker_max_list = []
            for index,i in enumerate(tiebreaker_list):
                if i == max_tiebreaker:
                    tiebreaker_max_list.append(1)
                else:
                    tiebreaker_max_list.append(0)
            return(tiebreaker_max_list)
        else:
            return(max_index[0])
