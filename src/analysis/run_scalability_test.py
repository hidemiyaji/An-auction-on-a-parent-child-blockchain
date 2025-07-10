#!/usr/bin/env python3
"""
Cross-Chain Auction Scalability Test Runner
Evaluate the performance of cross-chain auctions with varying numbers of CBCs (Cross-Chain Bidders).
This script runs a scalability test for cross-chain auctions, allowing users to specify the number of trials and CBC counts.
How to use:
python run_scalability_test.py [--trials N] [--cbc-counts 5,10,20,50]
"""

import argparse
import sys
from scalability_auction_test import run_scalability_test, display_summary_results
from time import perf_counter


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Cross-Chain Auction Scalability Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_scalability_test.py
  python run_scalability_test.py --trials 20
  python run_scalability_test.py --cbc-counts 5,10,15,20
  python run_scalability_test.py --trials 10 --cbc-counts 5,10,20,50,100
        """
    )

    parser.add_argument(
        '--trials', '-t',
        type=int,
        default=10,
        help='Number of trials per CBC configuration (default: 10)'
    )

    parser.add_argument(
        '--cbc-counts', '-c',
        type=str,
        default='5,10,20,50',
        help='Comma-separated list of CBC counts to test (default: 5,10,20,50)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output during testing'
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Parse CBC counts
    try:
        cbc_counts = [int(x.strip()) for x in args.cbc_counts.split(',')]
        cbc_counts.sort()  # Sort for consistent testing order
    except ValueError:
        print("Error: Invalid CBC counts format. Use comma-separated integers (e.g., 5,10,20,50)")
        sys.exit(1)

    # Validate parameters
    if args.trials <= 0:
        print("Error: Number of trials must be positive")
        sys.exit(1)

    if any(count <= 0 for count in cbc_counts):
        print("Error: All CBC counts must be positive")
        sys.exit(1)

    # Display configuration
    print("="*80)
    print("CROSS-CHAIN AUCTION SCALABILITY TEST")
    print("="*80)
    print(f"Configuration:")
    print(f"  CBC counts to test: {cbc_counts}")
    print(f"  Trials per configuration: {args.trials}")
    print(f"  Verbose output: {'Enabled' if args.verbose else 'Disabled'}")
    print(f"  Auction types: Simple Auction vs DLP-based Auction")
    print()

    # Estimate total time
    estimated_time = len(cbc_counts) * args.trials * 0.1  # Rough estimate
    print(f"Estimated total runtime: ~{estimated_time:.1f} seconds")
    print("\nStarting test...\n")

    # Run the scalability test
    start_time = perf_counter()

    try:
        results = run_scalability_test(cbc_counts, args.trials)

        # Display comprehensive results
        display_summary_results(results)

        total_time = perf_counter() - start_time

        print(f"\n{'='*80}")
        print(f"TEST COMPLETED SUCCESSFULLY")
        print(f"{'='*80}")
        print(f"Total execution time: {total_time:.2f} seconds")
        print(
            f"Average time per configuration: {total_time/len(cbc_counts):.2f} seconds")
        print(
            f"Average time per trial: {total_time/(len(cbc_counts)*args.trials):.4f} seconds")

        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"scalability_test_results_{timestamp}.txt"

        with open(results_file, 'w') as f:
            f.write(f"Cross-Chain Auction Scalability Test Results\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"Configuration: CBC counts {cbc_counts}, {args.trials} trials each\n\n")

            f.write(
                f"{'CBC Count':<10} {'Total Bidders':<15} {'Simple Avg (ms)':<15} {'DLP Avg (ms)':<15} {'Ratio':<10}\n")
            f.write("-" * 80 + "\n")

            for num_cbcs, data in results.items():
                simple_ms = data['avg_simple'] * 1000
                dlp_ms = data['avg_dlp'] * 1000
                ratio = data['avg_dlp'] / data['avg_simple']
                f.write(
                    f"{num_cbcs:<10} {data['total_bidders']:<15} {simple_ms:<15.3f} {dlp_ms:<15.3f} {ratio:<10.2f}x\n")

        print(f"\nDetailed results saved to: {results_file}")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during test execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import time  # Add this import for timestamp
    main()
