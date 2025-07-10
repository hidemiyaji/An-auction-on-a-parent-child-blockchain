# Cross-Chain Auction Scalability Test

A test suite for measuring the performance of cross-chain auctions by varying the number of CBCs (Child Blockchains) to 5, 10, 20, and 50.

## File Structure

### Main Files

- **`scalability_auction_test.py`** - Main implementation file
  - Simple Auction (based on ordinal_auction.py)
  - DLP-based Auction (based on propose_auction.py)
  - Integrated implementation and performance measurement functionality for both methods

- **`run_scalability_test.py`** - Test execution file
  - Command-line argument support
  - Automatic result saving functionality
  - Comprehensive analysis report generation

- **`individual_cbc_test.py`** - Individual configuration test file
  - Detailed testing for specific CBC counts
  - Auction operation demonstration
  - Simple comparison testing

## Usage

### 1. Basic Scalability Test

```bash
# Default settings (CBC counts: 5,10,20,50, trials: 10)
python run_scalability_test.py

# Change number of trials
python run_scalability_test.py --trials 20

# Change CBC counts
python run_scalability_test.py --cbc-counts 5,10,15,20,25

# Enable verbose output
python run_scalability_test.py --verbose
```

### 2. Individual Configuration Testing

```bash
# Default test (10 CBCs, 5 trials)
python individual_cbc_test.py

# Detailed auction demonstration
python individual_cbc_test.py demo

# Quick comparison test
python individual_cbc_test.py quick

# Test with specific configuration (20 CBCs, 10 trials)
python individual_cbc_test.py test 20 10
```

### 3. Direct Execution (Within Python Code)

```python
from scalability_auction_test import run_scalability_test, display_summary_results

# Execute scalability test
results = run_scalability_test([5, 10, 20, 50], n_trials=10)

# Display results
display_summary_results(results)
```

## Test Configuration

### Default Settings

- **CBC Counts**: 5, 10, 20, 50
- **Number of Trials**: 10 (for statistical reliability)
- **Bid Range**: $50-$300
- **Winners per CBC (M)**: 2 bidders
- **Total Bidders**: Automatically scaled according to CBC count

### Bidder Distribution

Total bidders automatically adjusted according to CBC count:
- 5 CBCs: 50 bidders
- 10 CBCs: 55 bidders
- 20 CBCs: 65 bidders
- 50 CBCs: 95 bidders

Bidders are distributed as evenly as possible across each CBC.


## Development & Extension

To add new CBC counts or test configurations:

1. Specify using the `--cbc-counts` option in `run_scalability_test.py`
2. Adjust the `calculate_bidder_distribution` function in `scalability_auction_test.py`
3. Add new analysis functionality as needed

## License

This test suite was created for academic research purposes.
