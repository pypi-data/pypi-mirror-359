"""
Tests for the prepo package.
"""

import unittest
import pandas as pd
import numpy as np
from src.prepo import FeaturePreProcessor


class TestFeaturePreProcessor(unittest.TestCase):
    """Test cases for the FeaturePreProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = FeaturePreProcessor()

        # Create a simple test dataframe
        self.test_data = {
            'date_column': ['2023-01-01', '2023-01-02', np.nan, '2023-01-04', '2023-01-05'],
            'price_USD': [100.50, np.nan, 200.75, 150.25, 300.00],
            'percentage_score': [0.85, 0.92, np.nan, 0.78, 0.95],
            'rating_100': [85, 92, np.nan, 78, 95],
            'is_active': [True, False, np.nan, True, False],
            'category': ['A', 'B', np.nan, 'A', 'C'],
            'revenue': [1000.50, 2000.75, np.nan, 1500.25, 3000.00],
            'count': [10, 15, np.nan, 12, 20],
            'description': ['Product A', np.nan, 'Product C', 'Product D', 'Product E']
        }
        self.df = pd.DataFrame(self.test_data)

    def test_determine_datatypes(self):
        """Test the determine_datatypes method."""
        datatypes = self.processor.determine_datatypes(self.df)

        # Check that the method correctly identifies column types
        self.assertEqual(datatypes['date_column'], 'temporal')
        self.assertEqual(datatypes['price_USD'], 'price')
        self.assertEqual(datatypes['percentage_score'], 'percentage')
        self.assertEqual(datatypes['rating_100'], 'numeric')
        self.assertEqual(datatypes['is_active'], 'binary')
        self.assertEqual(datatypes['category'], 'categorical')
        self.assertEqual(datatypes['revenue'], 'price')
        self.assertEqual(datatypes['count'], 'integer')
        self.assertEqual(datatypes['description'], 'string')

    def test_clean_data_drop_na(self):
        """Test the clean_data method with drop_na=True."""
        clean_df, _ = self.processor.clean_data(self.df, drop_na=True)

        # Check that rows with NaN values are dropped
        self.assertEqual(len(clean_df), 2)  # Only 2 rows have no NaN values

    def test_clean_data_impute(self):
        """Test the clean_data method with drop_na=False."""
        clean_df, _ = self.processor.clean_data(self.df, drop_na=False)

        # Check that NaN values are imputed
        self.assertFalse(clean_df['price_USD'].isna().any())
        self.assertFalse(clean_df['percentage_score'].isna().any())

    def test_process(self):
        """Test the process method."""
        processed_df = self.processor.process(self.df, drop_na=True, scaler_type='standard', remove_outlier=True)

        # Check that the processed dataframe has the expected shape
        self.assertEqual(len(processed_df), 2)  # Only 2 rows have no NaN values
        self.assertEqual(len(processed_df.columns), 9)  # All columns should be preserved

        # Check that numeric columns are scaled (mean should be close to 0 for standard scaling)
        self.assertAlmostEqual(processed_df['price_USD'].mean(), 0, delta=1e-10)
        self.assertAlmostEqual(processed_df['percentage_score'].mean(), 0, delta=1e-10)


if __name__ == '__main__':
    unittest.main()
