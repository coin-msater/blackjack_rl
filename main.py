from envs import BlackjackEnv, CARD_DECK, CARD_VALUES

n_decks = 1

def basic_blackjack_rand_strat():
    env = BlackjackEnv()
    state, info = env.reset()
    terminated = False

    while not terminated:
        action = env.action_space.sample()
        next_state, reward, terminated, truncated, info = env.step(action)
        state = next_state

    return reward

n_episodes = 10000
if __name__ == "__main__":
    total_reward = 0
    for i in range(n_episodes):
        total_reward += basic_blackjack_rand_strat()
    print(f"Average Returns: {total_reward / n_episodes}")
