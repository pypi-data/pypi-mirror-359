from yw_core.yw_core import records2annotations

def check_records2annotations(records, expected_annotations):
    assert records2annotations(records).strip() == expected_annotations.strip()

def test_zeroCell():
    records = []
    expected_annotations = ''
    check_records2annotations(records, expected_annotations)

def test_oneCell_emptyString():
    records = [{'inputs': {}, 'outputs': {}, 'output_candidates': {}}]
    expected_annotations = """
# @BEGIN cell-1
# @END cell-1
"""
    check_records2annotations(records, expected_annotations)

def test_twoCells_emptyString():
    records = [{'inputs': {}, 'outputs': {}, 'output_candidates': {}},
               {'inputs': {}, 'outputs': {}, 'output_candidates': {}}]
    expected_annotations = """
# @BEGIN cell-1
# @END cell-1

# @BEGIN cell-2
# @END cell-2
"""
    check_records2annotations(records, expected_annotations)

def test_oneCell_oneOutputcandidate():
    records = [{'inputs': {}, 'outputs': {}, 'output_candidates': {'x'}}]
    expected_annotations = """
# @BEGIN cell-1
# @END cell-1
"""
    check_records2annotations(records, expected_annotations)

def test_twoCells_cell0zeroInputOneOutput_cell1oneInputzeroOutput():
    records = [{'inputs': {}, 'outputs': {'x'}, 'output_candidates': {}},
               {'inputs': {'x'}, 'outputs': {}, 'output_candidates': {'y'}}]
    expected_annotations = """
# @BEGIN cell-1
# @OUT x
# @END cell-1

# @BEGIN cell-2
# @IN x
# @END cell-2
"""
    check_records2annotations(records, expected_annotations)

def test_twoCells_cell0zeroInputTwoOutputs_cell1twoInputszeroOutput():
    records = [{'inputs': {}, 'outputs': {'x', 'y'}, 'output_candidates': {}},
               {'inputs': {'x', 'y'}, 'outputs': {}, 'output_candidates': {}}]
    expected_annotations = """
# @BEGIN cell-1
# @OUT x
# @OUT y
# @END cell-1

# @BEGIN cell-2
# @IN x
# @IN y
# @END cell-2
"""
    check_records2annotations(records, expected_annotations)

def test_threeCells_cell0zeroInputOneOutput_cell1oneInputOneOutput_cell2oneInputZeroOutput():
    records = [{'inputs': {}, 'outputs': {'x'}, 'output_candidates': {}},
               {'inputs': {'x'}, 'outputs': {'x'}, 'output_candidates': {}},
               {'inputs': {'x'}, 'outputs': {}, 'output_candidates': {}}]
    expected_annotations = """
# @BEGIN cell-1
# @OUT x
# @END cell-1

# @BEGIN cell-2
# @IN x
# @OUT x @AS x-1
# @END cell-2

# @BEGIN cell-3
# @IN x @AS x-1
# @END cell-3
"""
    check_records2annotations(records, expected_annotations)

def test_threeCells_cell0zeroInputOneOutput_cell1empty_cell2oneInputZeroOutput():
    records = [{'inputs': {}, 'outputs': {'x'}, 'output_candidates': {}},
               {'inputs': {}, 'outputs': {}, 'output_candidates': {}},
               {'inputs': {'x'}, 'outputs': {}, 'output_candidates': {}}]
    expected_annotations = """
# @BEGIN cell-1
# @OUT x
# @END cell-1

# @BEGIN cell-2
# @END cell-2

# @BEGIN cell-3
# @IN x
# @END cell-3
"""
    check_records2annotations(records, expected_annotations)
