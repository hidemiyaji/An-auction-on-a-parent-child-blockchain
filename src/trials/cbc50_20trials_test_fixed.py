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


def run_simple_auction_trial(cbc_count, total_bidders, M=2):
    """Execute a single trial of Simple Auction"""
    # Distribute bidders evenly across each CBC
    bidders_per_cbc = total_bidders // cbc_count
    remaining_bidders = total_bidders % cbc_count

    bidder_counts = [bidders_per_cbc] * cbc_count
    for i in range(remaining_bidders):
        bidder_counts[i] += 1

    start_time = time.perf_counter()
    winners = run_simple_auction(bidder_counts, cbc_count, M, silent=True)
    end_time = time.perf_counter()

    return end_time - start_time


def run_propose_auction_trial(cbc_count, total_bidders, M=2):
    """Execute a single trial of DLP-based Auction"""
    # Distribute users evenly across each CBC
    users_per_cbc = total_bidders // cbc_count

    start_time = time.perf_counter()
    # Redirect standard output to suppress output from propose_auction
    import io
    import contextlib

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        run_auction(N_cbcs=cbc_count, users_per_cbc=users_per_cbc, M=M)

    end_time = time.perf_counter()

    return end_time - start_time


def run_multiple_trials(auction_type, cbc_count, total_bidders, num_trials=20):
    """Execute specified number of trials and calculate statistics"""
    execution_times = []

    print(
        f"Running {num_trials} trials for {auction_type} with {cbc_count} CBCs...")

    for trial in range(num_trials):
        if auction_type == "Simple Auction":
            execution_time = run_simple_auction_trial(cbc_count, total_bidders)
        elif auction_type == "DLP-based Auction":
            execution_time = run_propose_auction_trial(
                cbc_count, total_bidders)
        else:
            raise ValueError(f"Unknown auction type: {auction_type}")

        execution_times.append(execution_time)

        if (trial + 1) % 5 == 0:
            print(f"  Completed {trial + 1}/{num_trials} trials")

    # Calculate statistics
    avg_time = statistics.mean(execution_times)
    std_dev = statistics.stdev(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)

    return {
        'average': avg_time,
        'std_dev': std_dev,
        'min': min_time,
        'max': max_time,
        'raw_times': execution_times
    }


def main():
    """Main execution function"""
    print("CBC=50 20-trial performance measurement")
    print("=" * 50)

    # Experiment parameters
    cbc_count = 50
    total_bidders = 1000  # 20 bidders per CBC
    num_trials = 20
    M = 2  # Select top 2

    print(f"Experiment settings:")
    print(f"  Number of CBCs: {cbc_count}")
    print(f"  Total bidders: {total_bidders}")
    print(f"  Bidders per CBC: {total_bidders // cbc_count}")
    print(f"  Number of winners: {M}")
    print(f"  Number of trials: {num_trials}")
    print()

    # Simple Auction measurement
    print("1. Measuring Simple Auction...")
    simple_results = run_multiple_trials(
        "Simple Auction", cbc_count, total_bidders, num_trials)

    # DLP-based Auction measurement
    print("\n2. Measuring DLP-based Auction...")
    dlp_results = run_multiple_trials(
        "DLP-based Auction", cbc_count, total_bidders, num_trials)

    # Display results
    print("\n" + "=" * 50)
    print("Measurement Results")
    print("=" * 50)

    print(f"Simple Auction (CBC={cbc_count}, {num_trials} trials):")
    print(
        f"  Average time: {simple_results['average']:.6f}s ({simple_results['average']*1000:.3f}ms)")
    print(
        f"  Standard deviation: {simple_results['std_dev']:.6f}s ({simple_results['std_dev']*1000:.3f}ms)")
    print(
        f"  Minimum time: {simple_results['min']:.6f}s ({simple_results['min']*1000:.3f}ms)")
    print(
        f"  Maximum time: {simple_results['max']:.6f}s ({simple_results['max']*1000:.3f}ms)")

    print(f"\nDLP-based Auction (CBC={cbc_count}, {num_trials} trials):")
    print(
        f"  Average time: {dlp_results['average']:.6f}s ({dlp_results['average']*1000:.3f}ms)")
    print(
        f"  Standard deviation: {dlp_results['std_dev']:.6f}s ({dlp_results['std_dev']*1000:.3f}ms)")
    print(
        f"  Minimum time: {dlp_results['min']:.6f}s ({dlp_results['min']*1000:.3f}ms)")
    print(
        f"  Maximum time: {dlp_results['max']:.6f}s ({dlp_results['max']*1000:.3f}ms)")

    # Generate results for LaTeX table
    print("\n" + "=" * 50)
    print("Results for LaTeX Table")
    print("=" * 50)

    print("Simple Auction:")
    print(f"  {simple_results['average']*1000:.3f} & {simple_results['std_dev']*1000:.3f} & {simple_results['min']*1000:.3f} & {simple_results['max']*1000:.3f}")

    print("DLP-based Auction:")
    print(f"  {dlp_results['average']*1000:.3f} & {dlp_results['std_dev']*1000:.3f} & {dlp_results['min']*1000:.3f} & {dlp_results['max']*1000:.3f}")

    # Save results to file
    output_file = f"cbc50_20trials_results_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_file, 'w') as f:
        f.write("CBC=50 20-trial performance measurement results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Experiment settings:\n")
        f.write(f"  Number of CBCs: {cbc_count}\n")
        f.write(f"  Total bidders: {total_bidders}\n")
        f.write(f"  Bidders per CBC: {total_bidders // cbc_count}\n")
        f.write(f"  Number of winners: {M}\n")
        f.write(f"  試行回数: {num_trials}\n\n")

        f.write("Simple Auction結果:\n")
        f.write(
            f"  平均時間: {simple_results['average']:.6f}秒 ({simple_results['average']*1000:.3f}ms)\n")
        f.write(
            f"  標準偏差: {simple_results['std_dev']:.6f}秒 ({simple_results['std_dev']*1000:.3f}ms)\n")
        f.write(
            f"  最小時間: {simple_results['min']:.6f}秒 ({simple_results['min']*1000:.3f}ms)\n")
        f.write(
            f"  最大時間: {simple_results['max']:.6f}秒 ({simple_results['max']*1000:.3f}ms)\n\n")

        f.write("DLP-based Auction結果:\n")
        f.write(
            f"  平均時間: {dlp_results['average']:.6f}秒 ({dlp_results['average']*1000:.3f}ms)\n")
        f.write(
            f"  標準偏差: {dlp_results['std_dev']:.6f}秒 ({dlp_results['std_dev']*1000:.3f}ms)\n")
        f.write(
            f"  最小時間: {dlp_results['min']:.6f}秒 ({dlp_results['min']*1000:.3f}ms)\n")
        f.write(
            f"  最大時間: {dlp_results['max']:.6f}秒 ({dlp_results['max']*1000:.3f}ms)\n\n")

        f.write("LaTeX表用データ:\n")
        f.write("Simple Auction:\n")
        f.write(
            f"  {simple_results['average']*1000:.3f} & {simple_results['std_dev']*1000:.3f} & {simple_results['min']*1000:.3f} & {simple_results['max']*1000:.3f}\n")
        f.write("DLP-based Auction:\n")
        f.write(
            f"  {dlp_results['average']*1000:.3f} & {dlp_results['std_dev']*1000:.3f} & {dlp_results['min']*1000:.3f} & {dlp_results['max']*1000:.3f}\n")

    print(f"\n結果が {output_file} に保存されました。")

    return simple_results, dlp_results


if __name__ == "__main__":
    main()
