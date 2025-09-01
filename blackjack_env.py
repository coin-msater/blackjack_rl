import random
from poker_cards import CARD_DECK, CARD_VALUES
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class BlackjackEnv(gym.Env):
    
    def __init__(self, n_decks = 1, n_actions = 2):
        self._n_decks = n_decks
        self._player_stands = False

        # init hands
        self._dealer_hand = []
        self._player_hand = []
        self._shoe = CARD_DECK * n_decks
        self.np_random.shuffle(self._shoe)

        # action space: hit, stand
        self.action_space = spaces.Discrete(n_actions)

        # observation space: own_hand_value, ace_value, has_ace, dealer_up_card, is_blackjack, is_bust
        self.observation_space = spaces.Dict({
            "own_hand_value": spaces.Discrete(32),
            "usable_aces": spaces.Discrete(2),
            "dealer_up_card_value": spaces.Discrete(12)
            })

    def reset(self, seed = None, options = None):
        super().reset(seed = seed)
        
        # 1. reset deck and hands
        self._shoe = CARD_DECK * self._n_decks
        self.np_random.shuffle(self._shoe)
        self._player_hand.clear()
        self._dealer_hand.clear()
        self._player_stands = False

        # 2. deal 2 cards to each player
        for i in range(2):
            self._dealer_hand.append(self._shoe.pop())
            self._player_hand.append(self._shoe.pop())

        # 3. return obs, info
        obs = self._get_obs()
        info = self._get_info()

        return obs, info

    def step(self, action):
        # 1. actions
        match action:
            case 0:
                self._player_stands = True
            case 1:
                self._player_hand.append(self._shoe.pop())

        # 2. update state
        reward = 0
        terminated = False
        truncated = False
        next_obs = self._get_obs()
        info = self._get_info()


        # outcomes: -1 if player bust
        if self._is_bust(self._player_hand):
            terminated = True
            reward = -1
            return next_obs, reward, terminated, truncated, info


        # outcomes: dealer play if player stands, 1 if win, -1 if lose, if player bj, dealer bj = 0, dealer no bj = 1.5
        if self._player_stands:
            self._dealer_play()
            reward = self._decide_winner()
            terminated = True

        return next_obs, reward, terminated, truncated, info    

    def _get_obs(self):
        total, num_aces, num_usable_aces = self._evaluate_hand(self._player_hand)
        obs = {
            "own_hand_value": total,
            "usable_aces": 1 if num_usable_aces > 0 else 0,
            "dealer_up_card_value": self._get_dealer_up_card()
            }
        return obs

    def _get_info(self):
        info = {
            "shoe": self._shoe,
            "player hand": self._player_hand,
            "dealer hand": self._dealer_hand
        }
        return info
    
    def _get_dealer_up_card(self):
        return CARD_VALUES[self._dealer_hand[0]]
    
    def _evaluate_hand(self, hand):
        total = 0
        aces = 0
        
        for card in hand:
            total += CARD_VALUES[card]
            if card == 'A':
                aces += 1

        # adjust aces
        usable_aces = aces
        while total > 21 and usable_aces > 0:
            total -= 10
            usable_aces -= 1

        return total, aces, usable_aces

    def _is_blackjack(self, hand):
        value, _, _ = self._evaluate_hand(hand)
        return value == 21 and len(hand) == 2
    
    def _is_bust(self, hand):
        value, _, _ = self._evaluate_hand(hand)
        return value > 21
    
    def _dealer_play(self):
        # hard 17 rule
        # for S17: if total >= 17
        while True:
            total, aces, usable_aces = self._evaluate_hand(self._dealer_hand)
            if total >= 17:
                break
            self._dealer_hand.append(self._shoe.pop())

    def _decide_winner(self):
        player_value, _, _ = self._evaluate_hand(self._player_hand)
        dealer_value, _, _ = self._evaluate_hand(self._dealer_hand)

        # outcomes: dealer play if player stands
        # if this function is ran, player is not bust
        # player bj: dealer bj = 0, dealer no bj = 1.5
        # player no bj: dealer bust = 1, dealer bj = -1, dealer > player = -1, dealer < player = 1, dealer = player = 0

        if self._is_bust(self._player_hand):
            return -1

        if self._is_blackjack(self._player_hand):
            if self._is_blackjack(self._dealer_hand):
                return 0
            else:
                return 1.5

        if self._is_bust(self._dealer_hand) or player_value > dealer_value:
            return 1
        elif dealer_value > player_value or self._is_blackjack(self._dealer_hand):
            return -1
        else:
            return 0
    
    def render(self, reward = None):
        print(f"Player hand: {self._player_hand}, value: {self._evaluate_hand(self._player_hand)[0]}")
        print(f"Dealer hand: {self._dealer_hand}, value: {self._evaluate_hand(self._dealer_hand)[0]}")
        if reward != None:
            print(f"Player Returns: {reward}")
