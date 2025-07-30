import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from mlguard.bias_detecter import BiasDetectionChecker

def test_bias_detection_checker_no_bias():
    X, y = make_classification(n_samples=200, n_features=5, random_state=42)

    sensitive_feature = np.random.choice(['GroupA', 'GroupB'], size=200)

    X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    X_df['sensitive'] = sensitive_feature

    model = LogisticRegression()
    model.fit(X, y)

    result = BiasDetectionChecker.check_group_bias(
        model=model,
        X=X_df,
        y=y,
        sensitive_feature='sensitive',
        metric='accuracy',
        threshold=0.2
    )

    assert isinstance(result, dict)
    assert 'bias_status' in result
    assert result['bias_status'] in ['Bias Detected', 'No Significant Bias']
    assert 'group_performance' in result
    assert all(0.0 <= v <= 1.0 for v in result['group_performance'].values())


def test_bias_detection_checker_bias_detected():
    
    X, y = make_classification(n_samples=200, n_features=5, random_state=42)

    sensitive_feature = np.array(['GroupA'] * 100 + ['GroupB'] * 100)

    y[:100] = 1  # Groupa mostly positive
    y[100:] = 0  # Groupb mostly negative

    
    X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
    X_df['sensitive'] = sensitive_feature

    # Overfit a dummy model to exaggerate bias
    model = LogisticRegression()
    model.fit(X, y)

    # ruun bias check
    result = BiasDetectionChecker.check_group_bias(
        model=model,
        X=X_df,
        y=y,
        sensitive_feature='sensitive',
        metric='accuracy',
        threshold=0.1
    )


    assert isinstance(result, dict)
    assert 'bias_status' in result
    assert result['bias_status'] == 'Bias Detected'
    assert result['bias_gap'] > 0.1
