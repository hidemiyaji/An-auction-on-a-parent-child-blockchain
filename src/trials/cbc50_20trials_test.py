#!/usr/bin/env python3
"""
20-trial measurement script for CBC=50
Performance comparison between Simple Auction and DLP-based Auction
"""

from propose_auction import run_auction
from ordinal_auction import run_simple_auction
import sys
import time
import statistics
from pathlib import Path

# Add script directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))


def run_single_trial(cbc_count, total_bidders, auction_class):
    """Execute a single trial"""
    start_time = time.perf_counter()

    # Execute auction
    auction = auction_class(cbc_count=cbc_count, total_bidders=total_bidders)
    winners = auction.run_auction()

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    return execution_time


def run_multiple_trials(cbc_count, total_bidders, auction_class, num_trials=20):
    """Execute specified number of trials and calculate statistics"""
    execution_times = []

    print(
        f"Running {num_trials} trials for {auction_class.__name__} with {cbc_count} CBCs...")

    for trial in range(num_trials):
        execution_time = run_single_trial(
            cbc_count, total_bidders, auction_class)
        execution_times.append(execution_time)

        if (trial + 1) % 5 == 0:
            print(f"  Completed {trial + 1}/{num_trials} trials")

    # Calculate statistics
    avg_time = statistics.mean(execution_times)
    std_dev = statistics.stdev(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)

    return {
        'execution_times': execution_times,
        'average': avg_time,
        'std_dev': std_dev,
        'min': min_time,
        'max': max_time
    }


def main():
    """Main measurement process"""
    print("Starting 20-trial measurement for CBC=50...")
    print("="*60)

    # Measurement parameters
    cbc_count = 50
    total_bidders = 275  # 50 CBCs with approximately 5.5 bidders each
    num_trials = 20

    # Simple Auction measurement
    print("\n1. Simple Auction measurement:")
    simple_results = run_multiple_trials(
        cbc_count=cbc_count,
        total_bidders=total_bidders,
        auction_class=OrdinalAuction,
        num_trials=num_trials
    )

    # DLP-based Auction measurement
    print("\n2. DLP-based Auction measurement:")
    dlp_results = run_multiple_trials(
        cbc_count=cbc_count,
        total_bidders=total_bidders,
        auction_class=ProposeAuction,
        num_trials=num_trials
    )

    # Display results
    print("\n" + "="*60)
    print("Measurement Results (CBC=50, 20 Trials)")
    print("="*60)

    print(f"\nSimple Auction:")
    print(f"  Average Time: {simple_results['average']:.6f} s")
    print(f"  Std Dev:      {simple_results['std_dev']:.6f} s")
    print(f"  Min Time:     {simple_results['min']:.6f} s")
    print(f"  Max Time:     {simple_results['max']:.6f} s")

    print(f"\nDLP-based Auction:")
    print(f"  Average Time: {dlp_results['average']:.6f} s")
    print(f"  Std Dev:      {dlp_results['std_dev']:.6f} s")
    print(f"  Min Time:     {dlp_results['min']:.6f} s")
    print(f"  Max Time:     {dlp_results['max']:.6f} s")

    # Comparative analysis
    performance_ratio = dlp_results['average'] / simple_results['average']
    print(f"\nPerformance Ratio (DLP/Simple): {performance_ratio:.2f}x")

    # Output in LaTeX table format
    print("\n" + "="*60)
    print("LaTeX Table Format:")
    print("="*60)

    print("\\begin{table}[htbp]")
    print("\\centering")
    print(
        "\\caption{Performance Comparison between Simple Auction and DLP-based Auction (20 Trials)}")
    print("\\begin{tabular}{lcccc}")
    print("\\hline")
    print("\\textbf{Method} & Simple Auction &  DLP-based Auction\\\\")
    print("\\hline")
    print(
        f"\\textbf{{Average Time (s)}} & {simple_results['average']:.6f} & {dlp_results['average']:.6f}  \\\\")
    print(
        f"\\textbf{{Std Dev (s)}} & {simple_results['std_dev']:.6f}  & {dlp_results['std_dev']:.6f}  \\\\")
    print(
        f"\\textbf{{Min (s)}} & {simple_results['min']:.6f}  & {dlp_results['min']:.6f} \\\\")
    print(
        f"\\textbf{{Max (s)}} & {simple_results['max']:.6f}  & {dlp_results['max']:.6f}  \\\\")
    print("\\hline")
    print("\\end{tabular}")
    print("\\label{tab:auction_performance}")
    print("\\end{table}")

    # Save results to file
    results_file = script_dir / "cbc50_20trials_results.txt"
    with open(results_file, 'w') as f:
        f.write("CBC=50 20-trial measurement results\n")
        f.write("="*60 + "\n")
        f.write(
            f"Measurement date/time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Number of CBCs: {cbc_count}\n")
        f.write(f"Total bidders: {total_bidders}\n")
        f.write(f"Number of trials: {num_trials}\n\n")

        f.write("Simple Auction results:\n")
        f.write(f"  Average time: {simple_results['average']:.6f} s\n")
        f.write(f"  Standard deviation: {simple_results['std_dev']:.6f} s\n")
        f.write(f"  Minimum time: {simple_results['min']:.6f} s\n")
        f.write(f"  Maximum time: {simple_results['max']:.6f} s\n\n")

        f.write("DLP-based Auction results:\n")
        f.write(f"  Average time: {dlp_results['average']:.6f} s\n")
        f.write(f"  Standard deviation: {dlp_results['std_dev']:.6f} s\n")
        f.write(f"  Minimum time: {dlp_results['min']:.6f} s\n")
        f.write(f"  Maximum time: {dlp_results['max']:.6f} s\n\n")

        f.write(f"Performance ratio (DLP/Simple): {performance_ratio:.2f}x\n")

        f.write("\nIndividual measurement values:\n")
        f.write("Simple Auction execution times:\n")
        f.write(str(simple_results['execution_times']) + "\n\n")
        f.write("DLP-based Auction execution times:\n")
        f.write(str(dlp_results['execution_times']) + "\n")

    print(f"\nResults saved to {results_file}.")

    return simple_results, dlp_results


if __name__ == "__main__":
    main()
