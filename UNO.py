'''
This is a 2 player text-based UNO Game. You can play against a human or a randomized strategy.
The state of the game is represented by a 6-tuple of (player_turn (0 or 1), player1_hand, player2_hand, top_card (on the pile), deck (to draw from), pick (whether current player has picked a card)).
This does not incorporate all the complex rules of UNO, but does incorporate the core ruleset.
'''

import random

'''
    Takes two functions (representing player strategies) and plays a game of UNO using them. Pick A=player to play. 
'''
def play_uno(A ,B):
    players = [A, B]

    # Unpack state
    p, hand0, hand1, top_card, deck, pick = state = UNO_setup()

    # Play until game ends
    while True:

        # Ask current player to pick a move
        card = players[p](state)

        # If the player waits, update the state to reflect turn passing
        if card == 'wait':
            print(players[p].__name__, 'waits')
            state = (1-p, hand1, hand0, top_card, deck, 0)

        # If the player picks, update the state accordingly
        elif card == 'pick':
            print(players[p].__name__, 'picks')
            state = draw(state)

        # Otherwise, play the picked card.
        else:
            print(players[p].__name__, 'played', convert_name(card))
            state = play_card(card, state)


        p, hand0, hand1, top_card, deck, pick = state
        # Check if a player has to call UNO or has won! Note: Does not have functionality to catch someone before saying UNO due to synchronicity issues.
        if len(hand0) == 1:
            print(players[p].__name__, 'calls UNO')
        if len(hand1) == 1:
            print(players[1 -p].__name__, 'calls UNO')
        if len(hand1) == 0:
            return( players[1-p].__name__ , 'wins!')
        if len(hand0) == 0:
            return(players[p].__name__)

def UNO_setup():
    # Sets up deck with one of each [color, face] and 4 Wilds and Draw Fours (represented as ?W and ?F internally).
    deck = [color + card for color in 'RGBY' for card in '0123456789SRD123456789SRD'] + [color+card for card in 'WF' for color in '?'*4]
    random.shuffle(deck)

    #Picks the first card, and deals cards to players. Defaults to starting with 5 cards, but can be modified by specifiying third parameter.
    top_card = start_card(deck)
    hand0 = deal([], deck)
    hand1 = deal([], deck)

    # Plays top card to get state
    state = play_card(top_card, (0, hand0, hand1, '', deck, 0))
    return(state)

'''
Deals num_cards to hand0 from deck.
'''
def deal(hand0, deck, num_cards=5):
    for _ in range(num_cards):
        # Resets deck if empty
        if not deck:
            deck = [color + card for color in 'RGBY' for card in '0123456789SRD123456789SRD'] + [color +card for card in 'WF' for color in '????']
            random.shuffle(deck)

        # Adds cards to hand
        hand0.append(deck.pop(0))
    return(hand0)

'''
Draws a card from the deck, sets as top card if it isn't wild or draw four
'''
def start_card(deck):
    top_card = deck.pop(0)
    if top_card[1] in "WF":
        return(start_card(deck))
    return top_card

def draw(state):
    p, hand0, hand1, top_card, deck, pick = state
    pick = 1
    hand0 = deal(hand0, deck, 1)
    return (p, hand0, hand1, top_card, deck, pick)

def play_card(card, state):
    p, hand0, hand1, top_card, deck, pick = state
    top_card = card
    # Plays card, if playable
    try:
        if card[1] in 'WF':
            temp = '?' + card[1]
            hand0.remove(temp)
        else:
            hand0.remove(card)
    except:
        pass

    # Play special cards
    if card[1] in 'RSDWF':
        if (card[1] in 'RS'):
            return((p, hand0, hand1, top_card, deck, 0))
        elif(card[1] == 'D'):
            hand1 = deal(hand1, deck, 2)
            return((1-p, hand1, hand0, top_card, deck, 0))
        elif(card[1] in 'WF'):
            if card[1] =="F": hand1 = deal(hand1, deck, 4)
            top_card = card[0] + '?'
            return ((1-p, hand1, hand0, top_card, deck, 0))
    # Play number cards
    return (1 -p, hand1, hand0, top_card, deck, 0)



''' 
    Strategy that plays a random legal move
'''
def clueless(state):
    p, hand0, hand1, top_card, deck, pick = state
    # Calculate legal moves
    moves = legal_moves(state)

    # If there is no option but to pick/wait, do that
    if (moves == 'pick' or moves == 'wait'):
        return moves

    # If there are moves, pick and play a random move
    if moves != set():
        card = random.choice(list(moves))
        # If move is a wild or draw four, pick a random color
        if card[0] == '?':
            return 'RYBG'[random.randint(0, 3)]+card[1]
        return card

'''
Copy of clueless to have the computer play against itself, to check time efficiency and do some stats
'''
def clueless2(state):
    p, hand0, hand1, top_card, deck, pick = state
    moves = legal_moves(state)
    if moves == 'pick' or moves == 'wait':
        return(moves)
    if moves != set():
        card = random.choice(list(moves))
        if card[0] == '?':
            return('RYBG'[random.randint(0 ,3) ]+card[1])
    return card

'''
    Strategy that takes input from user, validates, and plays
'''
def player(state):
    p, hand0, hand1, top_card, deck, pick = state

    # Print cards, top card, and rules. Ask for player move.
    print("Your Cards are:",)
    for i, card in enumerate(hand0):
        indent = " "
        print(indent*i + convert_name(card))
    print("Top card: ", convert_name(top_card))
    card = input("\nPick a card to play. Type a letter from Y, G, B, R for color, \nand a number or one of [S, R, D, F, W] for Skip, Reverse, Draw Two, Draw Four, and Wild. \nType 'pick' to pick a card and 'wait' to pass the turn if you already picked. \nExample: Y7 for Yellow 7, BF for Draw Four with color Blue.\n")

    # Validate that move is legal
    while(((card[0] not in "RGBY") or (card[1] not in "0123456798SRDFW")) and (card not in ["pick", "wait"]) or (card=="wait" and pick!=1)):
        print("Invalid Move. Play Again")
        card = input()

    return card

'''
    Converts internal representation of cards to wet-wear friendly words
'''
def convert_name(card):
    colors = {'R' :'Red ', 'Y' :'Yellow ' ,'G' :'Green ', 'B' :'Blue ', '?' :''}
    faces = {'W':'Wild', 'F' :'Draw Four', 'S' :'Skip' ,'R' :'Reverse', 'D' :'Draw Two' }
    if card[1] not in 'WF':
        color = colors[card[0]]
    else:
        color = ''
    if card[1] in 'WFDRS':
        face = faces[card[1]]
    else:
        face = card[1]
    return(color+face)

'''
    Finds all playable cards
'''
def check_cards(hand, top_card):
    playable = []
    for card in hand:
        if card[1] in 'WF':
            playable.append(card)
        if card[0] == top_card[0]:
            playable.append(card)
        elif card[1] == top_card[1]:
            playable.append(card)
    return playable

'''
    Takes a state, finds playable cards, returns them if there are any, or returns 'pick' or 'wait'
'''
def legal_moves(state):
    p, hand0, hand1, top_card, deck, pick = state
    cards_playable = check_cards(hand0, top_card)
    if cards_playable:
        return set(cards_playable)
    else:
        return('pick' if not pick else 'wait')


# The following function test the speedo f the program
# def timedExec(f, *args):
#     import time
#     t = time.clock()
#     result = f(*args)
#     t0 = time.clock()
#     return t0 - t, result
#
# def playN(A ,B, N=1000):
#     time = 0
#     d = {A.__name__ :0, B.__name__ :0}
#     for n in range(N):
#         if n % 2:
#             time1, results =  timedExec(play_uno, A, B)
#             d[results] +=1
#             time += time1
#         else:
#             time1, results =  timedExec(play_uno, B, A)
#             d[results] +=1
#             time += time1
#         print(results)
#     print(d, time / float(N))


def main():
    play_uno(player, clueless)
