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

## Output Results

### 1. Real-time Progress

```
Trial 1/10: Simple=0.000025s, DLP=0.000008s
Trial 2/10: Simple=0.000023s, DLP=0.000007s
...
```

### 2. Results by Configuration

```
Results for 10 CBCs:
  Simple Auction:
    Average: 0.000024s (0.024ms)
    Std Dev: ±0.000003s
    Range: 0.000020s - 0.000028s
  DLP Auction:
    Average: 0.000007s (0.007ms)
    Std Dev: ±0.000001s
    Range: 0.000006s - 0.000009s
  Performance Ratio: DLP is 0.29x faster
```

### 3. Comprehensive Summary

```
CBC Count  Total Bidders   Simple Avg (ms)  DLP Avg (ms)    Ratio
------------------------------------------------------------------------
5          50              0.018            0.005           0.28x
10         55              0.024            0.007           0.29x
20         65              0.035            0.010           0.29x
50         95              0.065            0.018           0.28x
```

### 4. Scalability Analysis

- Analysis of execution time growth rate
- Optimal configuration recommendations
- Performance bottleneck identification

## Technical Details

### Simple Auction Implementation

- **Algorithm**: Multi-stage sorting
- **Complexity**: O(n log n)
- **Main Processing**:
  - Bid amount sorting in each CBC
  - Integrated sorting in PBC

### DLP-based Auction Implementation

- **Encryption**: RSA-style encryption
- **Commitment**: g^v mod p format
- **Main Processing**:
  - Commitment generation
  - Encryption/decryption
  - Vector Commitment calculation

### Measurement Precision

- **Timer**: Uses `time.perf_counter()`
- **Precision**: Microsecond level
- **Statistics**: Mean and standard deviation calculation through multiple trials

## Result Storage

Test results are automatically saved to files:

```
scalability_test_results_20241230_143022.txt
```

File names include timestamps and record the following information:
- Test configuration
- Detailed results for each CBC count
- Statistical information

## Notes

1. **Test Duration**: For 50 CBCs with 10 trials, testing takes approximately 30 seconds to 1 minute
2. **Memory Usage**: Memory usage temporarily increases with large CBC counts
3. **Result Variation**: Results may vary depending on system load
4. **Python Environment**: sympy library is required (`pip install sympy`)

## Troubleshooting

### If sympy is not found

```bash
pip install sympy
```

### In case of insufficient memory

Reduce CBC count or number of trials:

```bash
python run_scalability_test.py --cbc-counts 5,10,20 --trials 5
```

### If execution time is too long

Reduce the number of trials:

```bash
python run_scalability_test.py --trials 3
```

## Development & Extension

To add new CBC counts or test configurations:

1. Specify using the `--cbc-counts` option in `run_scalability_test.py`
2. Adjust the `calculate_bidder_distribution` function in `scalability_auction_test.py`
3. Add new analysis functionality as needed

## License

This test suite was created for academic research purposes.
