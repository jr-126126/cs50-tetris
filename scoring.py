from const import SCORE_SINGLE, SCORE_DOUBLE, SCORE_TRIPLE, SCORE_TETRIS

def calculate_score(lines_cleared, level):
    if lines_cleared == 1:
        return SCORE_SINGLE * (level + 1)
    elif lines_cleared == 2:
        return SCORE_DOUBLE * (level + 1)
    elif lines_cleared == 3:
        return SCORE_TRIPLE * (level + 1)
    elif lines_cleared == 4:
        return SCORE_TETRIS * (level + 1)
    return 0