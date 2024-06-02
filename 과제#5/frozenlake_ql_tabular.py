import numpy as np
import time
import random
import math
from datetime import datetime

total_episodes = 50000       # Total episodes
max_steps = 99               # Max steps per episode
gamma = 0.9                 # Discounting rate
alpha = 1.0					 # update parameter

# Exploration parameters
original_epsilon = 0.4           # Exploration rate
decay_rate = 0.000016            # Exponential decay rate for exploration prob
random.seed(datetime.now().timestamp())	# give a new seed in random number generation.

# state space is defined as size_row X size_col array.
# The boundary cells are holes(H).
# S: start, G: goal, H:hole, F:frozen

max_row = 9
max_col = 9
max_num_actions = 4

env_state_space = \
  [ ['H', 'H', 'H', 'H', 'H', 'H'], \
    ['H', 'S', 'F', 'F', 'F', 'H'], \
		['H', 'F', 'H', 'F', 'H', 'H'], \
		['H', 'F', 'F', 'F', 'H', 'H'], \
		['H', 'H', 'F', 'F', 'G', 'H'], \
		['H', 'H', 'H', 'H', 'H', 'H'] ]

# Create our Q table and initialize its value.
#   dim0:row, dim1:column, dim2: action.
# Q-table is initialized as 0.0.
# for terminal states(H or G), q-a value should be always 0.

Q = np.zeros((max_row,	max_col,  max_num_actions))

# offset of each move action:  up, right, down, left, respectively.
# a new state(location) = current state + offset of an action.
#        action = up    right  down    left.
move_offset = [[-1,0], [0,1],   [1,0],  [0,-1]]
move_str =	   ['up   ', 'right', 'down ', 'left ']

def display_Q_table (Q):
	print("\ncol=0       1        2        3       4         5")
	for r in range(max_row):
		print("row:", r)
		for a in range(max_num_actions):
			for c in range(max_col):
				text = "{:5.2f}".format(Q[r,c,a])
				if c == 0:
					line = text
				else:
					line = line + ",   " + text
			print(line)

# choose an action with epsilon-greedy approach according to Q.
# return value: an action index(0 ~ 3)
def choose_action_with_epsilon_greedy(s, epsilon):
	r = s[0]
	c = s[1]
	# get q-a values of all actions of current state.
	q_a_list = Q[r,c,:]
	max = np.argmax(q_a_list)	# max is action with biggest q-a value.
	rn = random.random()	# 0~1 사이의 random 실수 생성.

	if rn >= epsilon:	# epsilon 보다 크면, action max is selected.
		action = max
	else:
		rn1 = random.random()
		# 4 개의 action 중 하나를 무작위로 선택.
		if rn1 >= 0.75:
			action = 0
		elif rn1>= 0.5:
			action = 1
		elif rn1 >= 0.25:
			action = 2
		else:
			action = 3
	return action

# Q 가 가진 policy 를 greedy 하게 적용하여 취할 action 을 고른다.
def choose_action_with_greedy(s):
	r = s[0]
	c = s[1]
	# get q-a values of all actions of state s.
	q_a_list = Q[r,c,:]
	max_action = np.argmax(q_a_list)	# max is action with biggest q-a value.
	return max_action

# get new state and reward for taking action a at state s.
# deterministic movement is taken.
# reward is given as: F/S:0;  H:-5;   G:5.
def get_new_state_and_reward(s, a):
	new_state = []
	off_set = move_offset[a]

	#  s + off_set gives the new_state.
	new_state.append(s[0] + off_set[0])
	new_state.append(s[1] + off_set[1])

	# compute reward for moving to the new state
	cell = env_state_space[new_state[0]][new_state[1]]
	if cell == 'F':
		rew = 0
	elif cell == 'H':
		rew = -9
	elif cell == 'G':
		rew = 9
	elif cell == 'S':
		rew = 0
	else:
		print("Logic error in get_new_state_and_reward. This cannot happen!")
		time.sleep(1200)
		return [0,0], -20000
	return new_state, rew

# Environment 출력: agent 가 있는 곳에는 * 로 표시.
# agent 의 현재 위치(즉 current state): s
def env_rendering(s):
	for i in range(0, max_row, 1):
		line = ''
		for j in range(0, max_col, 1):
			line = line + env_state_space[i][j]
		if s[0] == i:
			col = s[1]
			line1 = line[:col] + '*' +line[col+1:]
		else:
			line1 = line
		print(line1)

# Learning stage: it iterates for an huge number of episodes
print("Initial Q table is")
display_Q_table(Q)

# start state is the cell with 'S'. terminal states are those with 'H' or 'G.
start_state = [1,1]

print("\nLearning starts.\n")
for episode in range(total_episodes):
	# set the start state of an episode.
	S = start_state

	# we use decayed epsilon in exploration so that it decreases as time goes on.
	epsilon = original_epsilon * math.exp(-decay_rate*episode)

	if episode % 5000 == 0:
		print('episode=', episode, '  epsilon=', epsilon)
		time.sleep(1)

	for step in range(max_steps):
		# Choose an action A from S using policy derived from Q with epsilon-greedy.
		A = choose_action_with_epsilon_greedy(S, epsilon)

		# take action A to observe reward R, and new state S_.
		S_ , R = get_new_state_and_reward(S, A)

		r=S[0]	# row of S
		c=S[1]	# column of S

		# update state-action value Q(s,a)
		Q[r][c][A] = Q[r][c][A] + alpha * (R + gamma * np.max(Q[S_[0]][S_[1]][:]) - Q[r][c][A] )

		S = S_	# move to the new state.

		# if the new state S is a terminal state, terminate the episode.
		if env_state_space[S[0]][S[1]] == 'G' or env_state_space[S[0]][S[1]] == 'H':
			break

print('\nLearning is finished. the Q table is:')
display_Q_table(Q)
# time.sleep(600)

# Test stage: agent 가 길을 찾아 가는 실험.

print("\nTest starts.\n")

for e in range(5):
	S = start_state
	total_rewards = 0
	print("\nEpisode:", e, " start state: (", S[0], ", ", S[1], ")")

	for step in range(max_steps):

		A = choose_action_with_greedy(S)		# S 에서 greedy 하게 다음 action 을 선택.

		S_ , R = get_new_state_and_reward(S, A)

		print("The move is:", move_str[A], " that leads to state (", S_[0], ", ", S_[1], ")" )

		total_rewards += R
		S = S_
		if env_state_space[S[0]][S[1]] == 'G' or env_state_space[S[0]][S[1]] == 'H':

			break
	print("Episode has ended. Total reward received in episode = ", total_rewards)
	time.sleep(1)

print("Program ends!!!")