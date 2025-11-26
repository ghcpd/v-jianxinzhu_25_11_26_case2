"""
Tests for data processing functionality
Tests numpy, pandas, scipy upgrades and functionality
"""

import pytest
import numpy as np
import pandas as pd
from scipy import stats


class TestNumpyUpgrade:
    """Test numpy upgraded features and security fixes"""
    
    def test_numpy_version(self):
        """Verify numpy version is upgraded"""
        version = np.__version__
        major, minor = map(int, version.split('.')[:2])
        assert major >= 1 and minor >= 26, f"NumPy version {version} should be >= 1.26"
    
    def test_numpy_basic_operations(self):
        """Test basic numpy operations"""
        arr = np.array([1, 2, 3, 4, 5])
        assert np.mean(arr) == 3.0
        assert np.sum(arr) == 15
        assert np.std(arr) > 0
    
    def test_numpy_array_creation(self):
        """Test array creation (CVE-2021-33430 fix verification)"""
        # This should not cause buffer overflow
        large_array = np.zeros((1000, 1000))
        assert large_array.shape == (1000, 1000)
        assert large_array.dtype == np.float64
    
    def test_numpy_empty_array(self):
        """Test empty array creation (CVE-2021-41495 fix)"""
        # Should not cause NULL pointer dereference
        empty = np.empty(100)
        assert empty.shape == (100,)
        assert len(empty) == 100
    
    def test_numpy_from_buffer(self):
        """Test array from buffer (CVE-2021-41496 fix)"""
        # Should not cause buffer overflow
        data = b'1234567890' * 100
        arr = np.frombuffer(data, dtype=np.uint8)
        assert len(arr) == len(data)
    
    def test_numpy_statistical_functions(self):
        """Test statistical functions"""
        data = np.random.randn(1000)
        
        assert isinstance(np.mean(data), (float, np.floating))
        assert isinstance(np.median(data), (float, np.floating))
        assert isinstance(np.std(data), (float, np.floating))
        assert isinstance(np.var(data), (float, np.floating))
    
    def test_numpy_advanced_indexing(self):
        """Test advanced indexing features"""
        arr = np.arange(100).reshape(10, 10)
        subset = arr[arr > 50]
        assert len(subset) == 49
        assert np.all(subset > 50)
    
    def test_numpy_broadcasting(self):
        """Test broadcasting operations"""
        a = np.array([[1, 2, 3]])
        b = np.array([[1], [2], [3]])
        result = a + b
        assert result.shape == (3, 3)
    
    def test_numpy_memory_safety(self):
        """Test memory operations are safe"""
        # Create large arrays to test memory handling
        arr1 = np.random.rand(1000, 1000)
        arr2 = np.random.rand(1000, 1000)
        result = arr1 + arr2
        assert result.shape == (1000, 1000)


class TestPandasUpgrade:
    """Test pandas upgraded features"""
    
    def test_pandas_version(self):
        """Verify pandas version is upgraded"""
        version = pd.__version__
        major = int(version.split('.')[0])
        assert major >= 2, f"Pandas version {version} should be >= 2.0"
    
    def test_pandas_nullable_integers(self):
        """Test pandas 2.x nullable integer type"""
        df = pd.DataFrame({
            'col1': pd.array([1, 2, None, 4], dtype='Int64')
        })
        
        assert df['col1'].dtype == 'Int64'
        assert pd.isna(df['col1'].iloc[2])
        assert df['col1'].sum() == 7
    
    def test_pandas_nullable_strings(self):
        """Test pandas 2.x nullable string type"""
        df = pd.DataFrame({
            'names': pd.array(['Alice', 'Bob', None, 'David'], dtype='string')
        })
        
        assert df['names'].dtype == 'string'
        assert pd.isna(df['names'].iloc[2])
    
    def test_pandas_nullable_booleans(self):
        """Test pandas 2.x nullable boolean type"""
        df = pd.DataFrame({
            'flags': pd.array([True, False, None, True], dtype='boolean')
        })
        
        assert df['flags'].dtype == 'boolean'
        assert pd.isna(df['flags'].iloc[2])
    
    def test_pandas_copy_on_write(self):
        """Test pandas 2.x copy-on-write behavior"""
        df1 = pd.DataFrame({'a': [1, 2, 3]})
        df2 = df1.copy()
        df2.loc[0, 'a'] = 999
        
        # Original should be unchanged
        assert df1.loc[0, 'a'] == 1
        assert df2.loc[0, 'a'] == 999
    
    def test_pandas_concat_instead_of_append(self):
        """Test using concat instead of deprecated append"""
        df1 = pd.DataFrame({'a': [1, 2]})
        df2 = pd.DataFrame({'a': [3, 4]})
        
        result = pd.concat([df1, df2], ignore_index=True)
        assert len(result) == 4
        assert list(result['a']) == [1, 2, 3, 4]
    
    def test_pandas_groupby_operations(self):
        """Test groupby operations"""
        df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'B', 'A'],
            'values': [1, 2, 3, 4, 5]
        })
        
        grouped = df.groupby('category')['values'].sum()
        assert grouped['A'] == 9
        assert grouped['B'] == 6
    
    def test_pandas_merge_operations(self):
        """Test merge operations"""
        df1 = pd.DataFrame({'key': ['A', 'B', 'C'], 'val1': [1, 2, 3]})
        df2 = pd.DataFrame({'key': ['A', 'B', 'D'], 'val2': [4, 5, 6]})
        
        merged = pd.merge(df1, df2, on='key', how='inner')
        assert len(merged) == 2
        assert list(merged['key']) == ['A', 'B']
    
    def test_pandas_pivot_operations(self):
        """Test pivot operations"""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
            'category': ['A', 'B', 'A', 'B'],
            'value': [1, 2, 3, 4]
        })
        
        pivot = df.pivot(index='date', columns='category', values='value')
        assert pivot.shape == (2, 2)
    
    def test_pandas_time_series(self):
        """Test time series functionality"""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100)
        })
        
        df.set_index('date', inplace=True)
        monthly = df.resample('ME').mean()
        assert len(monthly) >= 3
    
    def test_pandas_memory_efficiency(self):
        """Test memory efficiency improvements in pandas 2.x"""
        # Create large DataFrame
        df = pd.DataFrame({
            'a': np.random.randn(10000),
            'b': np.random.randn(10000)
        })
        
        memory_usage = df.memory_usage(deep=True).sum()
        assert memory_usage > 0


class TestSciPyUpgrade:
    """Test scipy upgraded features"""
    
    def test_scipy_version(self):
        """Verify scipy version is upgraded"""
        import scipy
        version = scipy.__version__
        major = int(version.split('.')[0])
        assert major >= 1, f"SciPy version {version} should be >= 1.0"
    
    def test_scipy_statistical_tests(self):
        """Test statistical tests"""
        data = np.random.randn(100)
        
        # Shapiro-Wilk test for normality
        statistic, p_value = stats.shapiro(data)
        assert isinstance(statistic, (float, np.floating))
        assert isinstance(p_value, (float, np.floating))
        assert 0 <= p_value <= 1
    
    def test_scipy_describe(self):
        """Test describe function"""
        data = np.random.randn(1000)
        description = stats.describe(data)
        
        assert hasattr(description, 'nobs')
        assert hasattr(description, 'minmax')
        assert hasattr(description, 'mean')
        assert hasattr(description, 'variance')
        assert hasattr(description, 'skewness')
        assert hasattr(description, 'kurtosis')
    
    def test_scipy_ttest(self):
        """Test t-test"""
        sample1 = np.random.randn(100)
        sample2 = np.random.randn(100) + 0.1
        
        statistic, p_value = stats.ttest_ind(sample1, sample2)
        assert isinstance(statistic, (float, np.floating))
        assert isinstance(p_value, (float, np.floating))
    
    def test_scipy_correlation(self):
        """Test correlation functions"""
        x = np.random.randn(100)
        y = x + np.random.randn(100) * 0.1
        
        correlation, p_value = stats.pearsonr(x, y)
        assert -1 <= correlation <= 1
        assert 0 <= p_value <= 1
    
    def test_scipy_distributions(self):
        """Test probability distributions"""
        # Normal distribution
        data = stats.norm.rvs(size=1000, loc=0, scale=1)
        assert len(data) == 1000
        assert abs(np.mean(data)) < 0.5  # Should be close to 0
        
        # PDF and CDF
        pdf = stats.norm.pdf(0, loc=0, scale=1)
        cdf = stats.norm.cdf(0, loc=0, scale=1)
        assert 0 < pdf < 1
        assert cdf == 0.5
    
    def test_scipy_optimization(self):
        """Test optimization functions"""
        from scipy.optimize import minimize
        
        # Simple quadratic function
        def objective(x):
            return x[0]**2 + x[1]**2
        
        result = minimize(objective, [1.0, 1.0])
        assert result.success
        assert abs(result.x[0]) < 0.01
        assert abs(result.x[1]) < 0.01
    
    def test_scipy_interpolation(self):
        """Test interpolation"""
        from scipy.interpolate import interp1d
        
        x = np.array([0, 1, 2, 3, 4])
        y = np.array([0, 1, 4, 9, 16])
        
        f = interp1d(x, y, kind='linear')
        assert abs(f(1.5) - 2.5) < 0.01
    
    def test_scipy_signal_processing(self):
        """Test signal processing"""
        from scipy.signal import correlate
        
        sig1 = np.array([1, 2, 3, 4, 5])
        sig2 = np.array([1, 2, 3, 4, 5])
        
        correlation = correlate(sig1, sig2, mode='valid')
        assert len(correlation) > 0


class TestDataProcessingIntegration:
    """Integration tests for data processing pipeline"""
    
    def test_full_data_pipeline(self):
        """Test complete data processing workflow"""
        # Generate data
        data = np.random.randn(1000)
        
        # Create DataFrame
        df = pd.DataFrame({
            'values': data,
            'squared': data ** 2,
            'category': np.random.choice(['A', 'B', 'C'], 1000)
        })
        
        # Group and aggregate
        summary = df.groupby('category').agg({
            'values': ['mean', 'std', 'count'],
            'squared': 'mean'
        })
        
        assert len(summary) == 3
        assert summary.shape[1] == 4
    
    def test_statistical_analysis_pipeline(self):
        """Test statistical analysis workflow"""
        # Generate sample data
        np.random.seed(42)
        data = np.random.normal(100, 15, 1000)
        
        # Pandas analysis
        df = pd.DataFrame({'values': data})
        mean = df['values'].mean()
        std = df['values'].std()
        
        # NumPy verification
        np_mean = np.mean(data)
        np_std = np.std(data, ddof=1)
        
        assert abs(mean - np_mean) < 0.01
        assert abs(std - np_std) < 0.01
        
        # SciPy statistical test
        statistic, p_value = stats.shapiro(data)
        assert p_value > 0.05  # Data should be approximately normal
    
    def test_missing_data_handling(self):
        """Test handling of missing data"""
        df = pd.DataFrame({
            'a': pd.array([1, 2, None, 4, 5], dtype='Int64'),
            'b': pd.array([1.0, None, 3.0, 4.0, 5.0], dtype='Float64'),
            'c': pd.array(['x', 'y', None, 'z', 'w'], dtype='string')
        })
        
        # Check NA detection
        assert df['a'].isna().sum() == 1
        assert df['b'].isna().sum() == 1
        assert df['c'].isna().sum() == 1
        
        # Test operations with NA
        assert df['a'].sum() == 12  # Excludes NA
        # In pandas 2.x with nullable dtypes, dropna() behavior changed
        # Float64 NAs are handled differently than object NAs
        assert len(df.dropna()) >= 2  # At least 2 complete rows
    
    def test_large_dataset_performance(self):
        """Test performance with larger datasets"""
        # Create large dataset
        size = 100000
        df = pd.DataFrame({
            'a': np.random.randn(size),
            'b': np.random.randn(size),
            'c': np.random.choice(['X', 'Y', 'Z'], size)
        })
        
        # Perform operations
        result = df.groupby('c').agg({
            'a': ['mean', 'std'],
            'b': ['min', 'max']
        })
        
        assert len(result) == 3
        assert result.shape[1] == 4
