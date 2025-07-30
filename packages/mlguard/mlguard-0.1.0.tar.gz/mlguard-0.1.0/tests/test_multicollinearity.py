import pandas as pd
from mlguard.multicollinearitychecker import MulticollinearityChecker

def test_high_multicollinearity_detection():
    #  two collinear features
    X = pd.DataFrame({
        'f1': [1, 2, 3, 4, 5],
        'f2': [2, 4, 6, 8, 10],  # Perfect linear relation with f1
        'f3': [5, 3, 6, 2, 1]   
    })

    result = MulticollinearityChecker.check_vif(X, vif_threshold=5.0)

    assert isinstance(result, dict)
    assert 'vif_scores' in result
    assert 'high_vif_features' in result
    assert 'collinearity_status' in result
    assert result['collinearity_status'] == "High Multicollinearity Detected"
    assert any(v > 5.0 for v in result['vif_scores'].values())


def test_no_multicollinearity_detection():
    # with low correlation
    X = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [5, 3, 1, 4, 2],
        'feature3': [2, 3, 2, 3, 2]
    })

    result = MulticollinearityChecker.check_vif(X, vif_threshold=10.0)  #  high threshold

    assert isinstance(result, dict)
    assert result['collinearity_status'] == "No Significant Multicollinearity"
    assert len(result['high_vif_features']) == 0


def test_invalid_input_type():
    # a non-DataFrame, non-ndarray input
    try:
        MulticollinearityChecker.check_vif([1, 2, 3, 4])
    except Exception as e:
        assert isinstance(e, TypeError)


def test_too_few_features():
    # Less than 2 data
    X = pd.DataFrame({'feature1': [1, 2, 3, 4, 5]})
    try:
        MulticollinearityChecker.check_vif(X)
    except Exception as e:
        assert isinstance(e, ValueError)
