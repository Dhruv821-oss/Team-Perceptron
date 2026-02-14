import pandas as pd
import numpy as np
from stress_testing.engine_stressor import PortfolioStressor

# --- STEP 1: Create Mock Data ---
# This simulates the Nifty50 data your detection module produces
data = {
    'Date': pd.date_range(start='2023-01-01', periods=100),
    'return': np.random.normal(0, 0.01, 100),
    'volatility': np.random.uniform(0.1, 0.2, 100),
    'Close': np.linspace(100, 110, 100)
}
mock_df = pd.DataFrame(data)

# --- STEP 2: Create a Mock Allocation Function ---
# This mimics your teammate's work. 
# Logic: If volatility > 0.3, reduce exposure to 0% (Capital Protection)
def mock_allocation_engine(df):
    weights = np.where(df['volatility'] > 0.3, 0.0, 1.0) # [cite: 15, 16]
    return df['return'] * weights

# --- STEP 3: Run the Stress Test ---
try:
    stressor = PortfolioStressor(mock_df)
    
    # Check if run_test executes without errors
    stressor.run_test(mock_allocation_engine)
    
    # Check if results dictionary is populated
    if stressor.results:
        print("\n✅ SUCCESS: Stress testing logic is capturing results.")
    
    # Check if plotting works (it should open a window)
    stressor.plot_results()
    
except Exception as e:
    print(f"\n❌ FAILED: There is a bug in the code: {e}")