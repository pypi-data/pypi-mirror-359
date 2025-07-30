
import unittest
import pandas as pd
import numpy as np
from ergs_selector.ergs import ERGSSelector

class TestERGSSelector(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset for testing
        data = {
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'feature3': np.random.rand(100),
            'feature4': np.random.rand(100)
        }
        labels = np.random.randint(0, 2, 100)
        self.X = pd.DataFrame(data)
        self.y = pd.Series(labels)

    def test_fit_transform(self):
        # Test if the selector can be fitted and transform the data
        selector = ERGSSelector(top_k=2)
        X_transformed = selector.fit_transform(self.X, self.y)
        
        # Check if the transformed data has the correct number of columns
        self.assertEqual(X_transformed.shape[1], 2)
        
        # Check if the selected features are from the original columns
        self.assertTrue(set(X_transformed.columns).issubset(set(self.X.columns)))

if __name__ == '__main__':
    unittest.main()
