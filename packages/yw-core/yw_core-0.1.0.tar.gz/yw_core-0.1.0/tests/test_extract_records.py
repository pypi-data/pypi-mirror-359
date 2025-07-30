from yw_core.yw_core import extract_records
from textwrap import dedent

EMPTY = set()

def check_extract_records(code_cells, expected_definite_records, expected_possible_records):
    assert extract_records(code_cells=[dedent(code_cell) for code_cell in code_cells], is_upper_estimate=False) == expected_definite_records
    assert extract_records(code_cells=[dedent(code_cell) for code_cell in code_cells], is_upper_estimate=True) == expected_possible_records

def test_zeroCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():
    code_cells = []
    expected_definite_records = []
    expected_possible_records = expected_definite_records
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_oneCellWithEmptyString_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():
    code_cells = ['']
    expected_definite_records = [{'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}]
    expected_possible_records = expected_definite_records
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_varAssigned_andNotUsedInTheSameCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():
    code_cells = ["x = 1"]
    expected_definite_records = [{'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}]
    expected_possible_records = expected_definite_records
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_varAssigned_andUsedInTheSameCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():
    
    code_cells = [
        """
        x = 1
        y = x + 1 
        """
    ]

    expected_definite_records = [{'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_varAssigned_andUsedInAnotherCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        x = 1
        """,""" 
        y = x + 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_varAssigned_andNotUsedInAnotherCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        x = 1
        """,""" 
        y = 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_varAssigned_thenReassignAndUsedInAnotherCell_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        x = 1
        ""","""
        x = 3
        y = x + 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_ifNotInALoop_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        x = 1
        ""","""
        y = 1
        ""","""
        # Union of the if-else branches
        if x > 0:
            tmp1 = 1
            y = y + tmp1
        else:
            tmp2 = 2
            y = y + tmp2
        """
    ]
    
    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'y'}, 'output_candidates': {'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x', 'y'}, 'outputs': EMPTY, 'output_candidates': {'tmp1', 'tmp2', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_ifInALoop_validCellsCorrectDefiniteAnswerWrongPossibleAnswer():
    
    code_cells = [
        """
        x, y = 1, 2
        ""","""
        # Order of executing the if-else branches matters
        # Definite: order with the minimum number of inputs
        # Possible: order with the maximum number of inputs
        for i in range(x):
            if i > 0:
                y = y + a
            else:
                a = 10
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x', 'y'}, 'output_candidates': {'x', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x', 'y'}, 'outputs': EMPTY, 'output_candidates': {'i', 'a', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'x', 'y'}, 'output_candidates': {'x', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x', 'a', 'y'}, 'outputs': EMPTY, 'output_candidates': {'x', 'i', 'a', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_for_validCellsCorrectDefiniteAnswerWrongPossibleAnswer():

    code_cells = [
        """
        x = 5
        ""","""
        # Use x as the argument of range()
        for i in range(x):
            tmp = i + 1
            y = tmp + 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'i', 'tmp', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x', 'i', 'tmp', 'y'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_classInstanceChangedInMethod_validCellsWrongDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        x = [1, 2, 3]
        ""","""
        x.append(1)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}        
    ]

    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_classInstanceNotChangedInMethod_validCellsCorrectDefiniteAnswerWrongPossibleAnswer():

    code_cells = [
        """
        x = [1, 2, 3]
        ""","""
        # The index method does not change x
        # x should NOT be an output candidate
        idx = x.index(1)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'idx'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x', 'idx'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_hiddenModification_mutableObjChangedInPlace_directAssignedMutableObjChangedTogether_validCellsWrongDefiniteAnswerCorrectPossibleAnswer():
    
    code_cells = [
        """
        lst1 = [1, 2, 3]
        lst2 = lst1
        ""","""
        lst1.append(4)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'lst1'}, 'output_candidates': {'lst1', 'lst2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'lst1'}, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'lst1', 'lst2'}, 'output_candidates': {'lst1', 'lst2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst2 = lst1', 'alias_vars': {'lst1', 'lst2'}},
        {'inputs': {'lst1', 'lst2'}, 'outputs': EMPTY, 'output_candidates': {'lst1', 'lst2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst2 = lst1', 'alias_vars': {'lst1', 'lst2'}}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)


def test_hiddenModification_mutableObjChangedInPlace_referredMutableObjsChangedTogether_validCellsWrongDefiniteAnswerCorrectPossibleAnswer():
    
    code_cells = [
        """
        a = set([1, 2, 3])
        b = set([2, 3, 4])
        lst = [a, b]
        ""","""
        for e in lst:
            e.add(1)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'lst'}, 'output_candidates': {'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'lst'}, 'outputs': EMPTY, 'output_candidates': {'e'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'lst', 'a', 'b'}, 'output_candidates': {'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst = [a, b]', 'alias_vars': {'a', 'b', 'lst'}},
        {'inputs': {'lst', 'a', 'b'}, 'outputs': EMPTY, 'output_candidates': {'e', 'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst = [a, b]', 'alias_vars': {'a', 'b', 'lst'}}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_hiddenModification_mutableObjChangedInPlace_referredImmutableObjsDoNotChange_validCellsCorrectDefiniteAnswerWrongPossibleAnswer():
    
    code_cells = [
        """
        a = 1
        b = 2
        lst = [a, b]
        ""","""
        lst[0] = 10
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'lst'}, 'output_candidates': {'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'lst'}, 'outputs': EMPTY, 'output_candidates': {'lst'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'lst', 'a', 'b'}, 'output_candidates': {'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst = [a, b]', 'alias_vars': {'a', 'b', 'lst'}},
        {'inputs': {'lst', 'a', 'b'}, 'outputs': EMPTY, 'output_candidates': {'lst', 'a', 'b'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'lst = [a, b]', 'alias_vars': {'a', 'b', 'lst'}}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_hiddenModification_mutableObjNotChangedInPlace_referredMutableObjsDoNotChange_validCellsWrongDefiniteAnswerWrongPossibleAnswer():
    
    code_cells = [
        """
        import pandas as pd
        df1 = pd.DataFrame({'a': [1, 2, 3]})
        df2 = pd.DataFrame({'b': [2, 3, 4]})
        dfs = [df1, df2]
        ""","""
        for df in dfs:
            df = df + 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': {'dfs'}, 'output_candidates': {'dfs', 'df1', 'df2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'dfs'}, 'outputs': EMPTY, 'output_candidates': {'df'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]

    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': {'dfs', 'df1', 'df2'}, 'output_candidates': {'dfs', 'df1', 'df2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'dfs = [df1, df2]', 'alias_vars': {'df1', 'df2', 'dfs'}},
        {'inputs': {'dfs', 'df1', 'df2'}, 'outputs': EMPTY, 'output_candidates': {'df', 'dfs', 'df1', 'df2'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': 'dfs = [df1, df2]', 'alias_vars': {'df1', 'df2', 'dfs'}}
    ]

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

####################################################################################################
# Assumption 1: inputs and outputs of a function are required to be written at cell level
####################################################################################################

def test_cellLevelVarUsedInNonMutatingFuncBody_notAtCellLevel_validCellsWrongDefiniteAnswerWrongPossibleAnswer_hasWorkaround():

    code_cells = [
        """
        # This non-mutating function uses a variable (i.e., x) defined at cell level
        def add_one(x):
            x = x + 1
            return x
        ""","""
        x = 1
        ""","""
        # Can NOT detect that x is used here
        y = add_one()
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_cellLevelVarUsedInNonMutatingFuncBody_andRedundantlyAtCellLevel_validCellsCorrectDefiniteAnswerWrongPossibleAnswer():

    code_cells = [
        """
        # This non-mutating function uses local variable v
        def add_one(v):
            return v + 1
        ""","""
        x = 1
        ""","""
        # Variable x is used at the cell level
        y = add_one(x)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x', 'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_cellLevelVarUsedInMutatingFuncBody_notAtCellLevel_validCellsWrongDefiniteAnswerWrongPossibleAnswer_hasWorkaround():

    code_cells = [
        """
        # This mutating function uses a variable (i.e., x) defined at cell level
        def add_one():
            x.append(1)
            return x
        ""","""
        x = [1]
        ""","""
        # Can NOT detect that x is used and reassigned here
        y = add_one()
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records

    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_cellLevelVarAssignedInFuncBody_notAtCellLevel_validCellsWrongDefiniteAnswerCorrectPossibleAnswer():

    code_cells = [
        """
        def add_one(v):
            v.append(1)
            return v
        ""","""
        x = [1]
        ""","""
        # Can NOT detect that x is reassigned at this cell
        y = add_one(x)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x', 'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_cellLevelVarUsedAndReassignedInFuncBody_andRedundantlyAtCellLevel_validCellsCorrectDefiniteAnswerCorrectPossibleAnswer():
    
    code_cells = [
        """
        # This mutating function uses local variable v
        def add_one(v):
            v.append(1)
            return v
        ""","""
        x = [1]
        ""","""
        # Varaible x is used and reassigned at cell level
        x = add_one(x)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': {'x'}, 'output_candidates': {'x'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': {'x'}, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

####################################################################################################
# Assumption 2: a variable name can NOT be reused as a function name, and vice versa
####################################################################################################

def test_VarNameReassignedToFunc_ValidCellsWrongDefiniteAnswerWrongPossibleAnswer_hasNoWorkaround():

    code_cells = [
        """
        add_one = 1
        ""","""
        # add_one is not an output candidate as it is reassigned to a function
        add_one = add_one + 1
        # Reassign the variable name to a function
        def add_one(v):
            return v + 1
        y = add_one(5)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'add_one'}, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_funcNameReassignedToVar_ValidCellsWrongDefiniteAnswerWrongPossibleAnswer_hasNoWorkaround():

    code_cells = [
        """
        def add_one(v):
            return v + 1
        ""","""
        x = add_one(5)
        # Reassign the function name to a variable
        add_one = x + 1
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'x'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)

def test_funcNameReassignedToVarAndReused_InvalidCellsAnyAnswer():

    code_cells = [
        """
        def add_one(v):
            return v + 1
        ""","""
        # Reassign the function name to a variable
        add_one = 5
        ""","""
        # The function cannot be reused as it has been reassigned to a variable.
        y = add_one(1)
        """
    ]

    expected_definite_records = [
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': {'add_one'}, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': EMPTY, 'refers_code': EMPTY, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY},
        {'inputs': EMPTY, 'outputs': EMPTY, 'output_candidates': {'y'}, 'refers_code': {'add_one'}, 'defines_code': EMPTY, 'alias_stmt': None, 'alias_vars': EMPTY}
    ]
    expected_possible_records = expected_definite_records
    
    check_extract_records(code_cells, expected_definite_records, expected_possible_records)
