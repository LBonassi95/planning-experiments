import pandas as pd

RT = 'RT'
PL = 'PL'
EN = 'EN'
D = 'D'
SYS = 'SYS'
I = 'I'
SOL = 'SOL'
DEFAULT_SOLUTION_FOUND_STRINGS = ['Strong cyclic plan found.', 'Policy successfully found.' , 'Solution found.', 'Plan found.']

def get_col_domain(df: pd.DataFrame, col):
        domain = []
        for index, row in df.iterrows():
            if df.loc[index, col] not in domain:
                domain.append(df.loc[index, col])
        return domain