
import random

# Dictonary containing letter scores
POINTS = dict(A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1,
              V=4, W=4, X=8, Y=4, Z=10, _=0)

def bonus_template(half):
    "Make a board from the left half."
    return([list(mirror(x)) for x in half.split()])


def mirror(sequence): return sequence + sequence[-2::-1]


SCRABBLE = """
|||||||||
|3..:...3
|.2...;..
|..2...:.
|:..2...:
|....2...
|.;...;..
|..:...:.
|3..:...*
|..:...:.
|.;...;..
|....2...
|:..2...:
|..2...:.
|.2...;..
|||||||||
"""


BONUS = bonus_template(SCRABBLE)

# Internal representations of double word, triple word, double letter, triple letter
DW, TW, DL, TL = '23:;'


def removed(letters, remove):
    "Return a str of letters, but with each letter in remove removed once."
    for L in remove:
        letters = letters.replace(L, '', 1)
    return letters


def prefixes(word):
    "A list of the initial sequences of a word, not including the complete word."
    return [word[:i] for i in range(len(word))]


def transpose(matrix):
    "Transpose e.g. [[1,2,3], [4,5,6]] to [[1, 4], [2, 5], [3, 6]]"
    # or [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
    return list(map(list, zip(*matrix)))


def readwordlist(filename):
    "Return a pair of sets: all the words in a file, and all the prefixes. (Uppercased.)"
    wordset = set(open(filename).read().upper().split())
    prefixset = set(p for word in wordset for p in prefixes(word))
    return wordset, prefixset


WORDS, PREFIXES = readwordlist('words.txt')


class anchor(set):
    "An anchor is where a new word can be placed; has a set of allowable letters."


LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ANY = anchor(LETTERS)  # The anchor that can be any letter


def is_letter(sq):
    return isinstance(sq, str) and sq in LETTERS


def is_empty(sq):
    "Is this an empty square (no letters, but a valid position on board)."
    return sq == '.' or sq == '*' or isinstance(sq, set)


def add_suffixes(hand, pre, start, row, results, anchored=True):
    "Add all possible suffixes, and accumulate (start, word) pairs in results."
    i = start + len(pre)
    if pre in WORDS and anchored and not is_letter(row[i]):
        results.add((start, pre))
    if pre in PREFIXES:
        sq = row[i]
        if is_letter(sq):
            add_suffixes(hand, pre + sq, start, row, results)
        elif is_empty(sq):
            possibilities = sq if isinstance(sq, set) else ANY
            for L in hand:
                if L in possibilities:
                    add_suffixes(hand.replace(L, '', 1), pre + L, start, row, results)
    return results


def legal_prefix(i, row):
    """A legal prefix of an anchor at row[i] is either a string of letters
    already on the board, or new letters that fit into an empty space.
    Return the tuple (prefix_on_board, maxsize) to indicate this.
    E.g. legal_prefix(a_row, 9) == ('BE', 2) and for 6, ('', 2)."""
    s = i
    while is_letter(row[s - 1]): s -= 1
    if s < i:  ## There is a prefix
        return ''.join(row[s:i]), i - s
    while is_empty(row[s - 1]) and not isinstance(row[s - 1], set): s -= 1
    return ('', i - s)


prev_hand, prev_results = '', set()  # cache for find_prefixes


def find_prefixes(hand, pre='', results=None):
    ## Cache the most recent full hand (don't cache intermediate results)
    global prev_hand, prev_results
    if hand == prev_hand: return prev_results
    if results is None: results = set()
    if pre == '': prev_hand, prev_results = hand, results
    # Now do the computation
    if pre in WORDS or pre in PREFIXES: results.add(pre)
    if pre in PREFIXES:
        for L in hand:
            if L == '_':
                for l in LETTERS:
                    find_prefixes(hand.replace(L, '', 1), pre + l, results)
    return results


def row_plays(hand, row):
    "Return a set of legal plays in row.  A row play is an (start, 'WORD') pair."
    results = set()
    ## To each allowable prefix, add all suffixes, keeping words
    for (i, sq) in enumerate(row[1:-1], 1):
        if isinstance(sq, set):
            pre, maxsize = legal_prefix(i, row)
            if pre:  ## Add to the letters already on the board
                start = i - len(pre)
                add_suffixes(hand, pre, start, row, results, anchored=False)
            else:  ## Empty to left: go through the set of all possible prefixes
                for pre in find_prefixes(hand):
                    if len(pre) <= maxsize:
                        start = i - len(pre)
                        add_suffixes(removed(hand, pre), pre, start, row, results,
                                     anchored=False)
    return results


def find_cross_word(board, i, j):
    """Find the vertical word that crosses board[j][i]. Return (j2, w),
    where j2 is the starting row, and w is the word"""
    sq = board[j][i]
    w = sq if is_letter(sq) else '.'
    for j2 in range(j, 0, -1):
        sq2 = board[j2 - 1][i]
        if is_letter(sq2):
            w = sq2 + w
        else:
            break
    for j3 in range(j + 1, len(board)):
        sq3 = board[j3][i]
        if is_letter(sq3):
            w = w + sq3
        else:
            break
    return (j2, w)


def neighbors(board, i, j):
    """Return a list of the contents of the four neighboring squares,
    in the order N,S,E,W."""
    return [board[j - 1][i], board[j + 1][i],
            board[j][i + 1], board[j][i - 1]]


def set_anchors(row, j, board):
    """Anchors are empty squares with a neighboring letter. Some are resticted
    by cross-words to be only a subset of letters."""
    for (i, sq) in enumerate(row[1:-1], 1):
        neighborlist = (N, S, E, W) = neighbors(board, i, j)
        # Anchors are squares adjacent to a letter.  Plus the '*' square.
        if sq == '*' or (is_empty(sq) and any(map(is_letter, neighborlist))):
            if is_letter(N) or is_letter(S):
                # Find letters that fit with the cross (vertical) word
                (j2, w) = find_cross_word(board, i, j)
                row[i] = anchor(L for L in LETTERS if w.replace('.', L) in WORDS)
            else:  # Unrestricted empty square -- any letter will fit.
                row[i] = ANY


def make_play(play, board, hand):
    "Put the word down on the board."
    (score, (i, j), (di, dj), word) = play
    for (n, L) in enumerate(word):
        hand = hand.replace(L, "", 1)
        board[j + n * dj][i + n * di] = L
    return hand


def calculate_score(board, pos, direction, hand, word):
    "Return the total score for this play."
    total, crosstotal, word_mult = 0, 0, 1
    starti, startj = pos
    di, dj = direction
    other_direction = DOWN if direction == ACROSS else ACROSS
    for (n, L) in enumerate(word):
        i, j = starti + n * di, startj + n * dj
        sq = board[j][i]
        b = BONUS[j][i]
        word_mult *= (1 if is_letter(sq) else
                      3 if b == TW else 2 if b in (DW, '*') else 1)
        letter_mult = (1 if is_letter(sq) else
                       3 if b == TL else 2 if b == DL else 1)
        total += POINTS[L] * letter_mult
        if isinstance(sq, set) and sq is not ANY and direction is not DOWN:
            crosstotal += cross_word_score(board, L, (i, j), other_direction)
    return crosstotal + word_mult * total


def cross_word_score(board, L, pos, direction):
    "Return the score of a word made in the other direction from the main word."
    i, j = pos
    (j2, word) = find_cross_word(board, i, j)
    return calculate_score(board, (i, j2), DOWN, L, word.replace('.', L))


ACROSS, DOWN = (1, 0), (0, 1)  # Directions that words can go


def horizontal_plays(hand, board):
    "Find all horizontal plays -- (score, pos, word) pairs -- across all rows."
    results = set()
    for (j, row) in enumerate(board[1:-1], 1):
        set_anchors(row, j, board)
        for (i, word) in row_plays(hand, row):
            score = calculate_score(board, (i, j), ACROSS, hand, word)
            results.add((score, (i, j), word))
    return results


def all_plays(hand, board):
    """All plays in both directions. A play is a (score, pos, dir, word) tuple,
    where pos is an (i, j) pair, and dir is a (delta-_i, delta_j) pair."""
    hplays = horizontal_plays(hand, board)
    vplays = horizontal_plays(hand, transpose(board))
    return (set((score, (i, j), ACROSS, w) for (score, (i, j), w) in hplays) |
            set((score, (i, j), DOWN, w) for (score, (j, i), w) in vplays))


NOPLAY = None


def best_play(hand, board):
    "Return the highest-scoring play.  Or None."
    plays = all_plays(hand, board)
    return sorted(plays)[-1] if plays else NOPLAY


def best_strat(hand, board):
    return best_play(hand, board)


def best_strat2(hand, board):
    return best_play(hand, board)


def player(hand, board):
    d = {'DOWN': (0, 1), 'ACROSS': (1, 0)}
    print("Your Hand:", hand)
    play = input("Enter a word, a direction from between ACROSS and DOWN, and the position to play at as (i, j).\n Example: HATS ACROSS 8 8")
    print(play.split())
    while True:
        word, direction, i, j = tuple(play.split())
        print(word, direction, i, j)
        pos, direction = (int(i), int(j)), d[direction.upper()]
        return (calculate_score(board, pos, direction, hand, word), pos, direction, word)



def draw_tiles(bag, hand=''):
    while bag and len(hand) < 7:
        random.shuffle(bag)
        l = len(bag)
        hand = hand + bag.pop(0)
        assert len(bag) + 1 == l
    return hand


def scrabble_setup():
    bag = list('E' * 12 + 'AI' * 9 + 'O' * 8 + 'NRT' * 6 + 'LSUD' * 4 + 'G' * 3 + 'BCMPFHVWY' * 2 + 'KJXQZ')
    hand0 = draw_tiles(bag)
    hand1 = draw_tiles(bag)
    return (0, (hand0, 0), (hand1, 0), bag)


def make_board():
    board = bonus_template("""
    |||||||||
    |........
    |........
    |........
    |........
    |........
    |........
    |........
    |.......*
    |........
    |........
    |........
    |........
    |........
    |........
    |........
    |||||||||
    """)
    print(board)
    # board = map(list, board)
    return board


def show_board(board):
    "Print the board."
    for j, row in enumerate(board):
        for i, sq in enumerate(row):
            if is_empty(sq):
                print(BONUS[i][j], end="")
            else:
                print(sq, end="")
        print("")
    print("\n")


def play_scrabble(A, B):
    strategies = [A, B]

    # state = (p, (hand0, score0), (hand1, score1), bag)
    (p, (hand0, score0), (hand1, score1), bag) = state = scrabble_setup()
    board = make_board()
    show_board(board)
    while bag:
        play = strategies[p](state[p + 1][0], board)
        if play:
            print(play)
            if p == 0:
                hand0 = make_play(play, board, hand0)
                score0 += play[0]
                hand0 = draw_tiles(bag, hand0)
            if p == 1:
                hand1 = make_play(play, board, hand1)
                score1 += play[0]
                hand1 = draw_tiles(bag, hand1)
        p = 1 - p
        show_board(board)
        state = (p, (hand0, score0), (hand1, score1), bag)
    if score0 > score1:
        print(score1, score0)
        return A.__name__
    if score0 < score1:
        print(score1, score0)
        return B.__name__
    return "DRAW"


def timedExec(f, *args):
    import time
    t = time.clock()
    result = f(*args)
    t0 = time.clock()
    return t0 - t, result


def playN(A, B, N=1000):
    time = 0
    d = {A.__name__: 0, B.__name__: 0, "DRAW": 0}
    for n in range(N):
        if n % 2:
            time1, result = timedExec(play_scrabble, A, B)
            d[result] += 1
            time += time1
        else:
            time1, result = timedExec(play_scrabble, B, A)
            d[result] += 1
            time += time1
    print(d, time / float(N))


def main():
    play_scrabble(player, best_strat)
