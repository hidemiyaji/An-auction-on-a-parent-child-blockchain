"""
Individual CBC Configuration Test
File for testing auction performance with individual CBC count configurations

This file provides the following capabilities:
1. Auction execution with specific CBC counts
2. Detailed comparison between Simple Auction and DLP Auction
3. Detailed analysis of execution times
"""

from scalability_auction_test import (
    run_simple_auction, run_dlp_auction,
    calculate_bidder_distribution, generate_random_bidders_simple, generate_random_users_dlp
)
from time import perf_counter
import random


def test_single_configuration(num_cbcs, total_bidders=None, M=2, trials=5, verbose=True):
    """
    Test with a single CBC configuration

    Args:
        num_cbcs: Number of CBCs
        total_bidders: Total number of bidders (automatically calculated if None)
        M: Number of winners per CBC
        trials: Number of trials
        verbose: Whether to display detailed output
    """
    if total_bidders is None:
        total_bidders = 50 + (num_cbcs - 5) * 5  # Scaling calculation

    bidder_distribution = calculate_bidder_distribution(
        num_cbcs, total_bidders)

    if verbose:
        print(f"="*80)
        print(f"INDIVIDUAL CONFIGURATION TEST")
        print(f"="*80)
        print(f"Configuration:")
        print(f"  Number of CBCs: {num_cbcs}")
        print(f"  Total bidders: {total_bidders}")
        print(f"  Winners per CBC (M): {M}")
        print(f"  Bidder distribution: {bidder_distribution}")
        print(f"  Number of trials: {trials}")
        print()

    simple_times = []
    dlp_times = []

    # Execute multiple times and take average
    for trial in range(trials):
        if verbose:
            print(f"Trial {trial + 1}/{trials}:")

        # Simple Auction test
        start_time = perf_counter()
        simple_winners = run_simple_auction(
            num_cbcs, bidder_distribution, M, silent=not verbose)
        simple_time = perf_counter() - start_time
        simple_times.append(simple_time)

        if verbose:
            print(
                f"  Simple Auction time: {simple_time:.6f} seconds ({simple_time*1000:.3f} ms)")

        # DLP Auction test
        start_time = perf_counter()
        dlp_winners, vector_commitment = run_dlp_auction(
            num_cbcs, bidder_distribution, M, silent=not verbose)
        dlp_time = perf_counter() - start_time
        dlp_times.append(dlp_time)

        if verbose:
            print(
                f"  DLP Auction time: {dlp_time:.6f} seconds ({dlp_time*1000:.3f} ms)")
            print(f"  Ratio (DLP/Simple): {dlp_time/simple_time:.2f}x")
            print()

    # Calculate statistics
    avg_simple = sum(simple_times) / len(simple_times)
    avg_dlp = sum(dlp_times) / len(dlp_times)

    if verbose:
        print(f"="*60)
        print(f"SUMMARY RESULTS")
        print(f"="*60)
        print(f"Simple Auction:")
        print(
            f"  Average time: {avg_simple:.6f} seconds ({avg_simple*1000:.3f} ms)")
        print(f"  Min time: {min(simple_times):.6f} seconds")
        print(f"  Max time: {max(simple_times):.6f} seconds")
        print(f"  All times: {[f'{t:.6f}' for t in simple_times]}")
        print()
        print(f"DLP Auction:")
        print(f"  Average time: {avg_dlp:.6f} seconds ({avg_dlp*1000:.3f} ms)")
        print(f"  Min time: {min(dlp_times):.6f} seconds")
        print(f"  Max time: {max(dlp_times):.6f} seconds")
        print(f"  All times: {[f'{t:.6f}' for t in dlp_times]}")
        print()
        print(f"Performance Comparison:")
        print(
            f"  DLP is {avg_dlp/avg_simple:.2f}x {'faster' if avg_dlp < avg_simple else 'slower'} than Simple")
        print(
            f"  Time difference: {abs(avg_dlp - avg_simple):.6f} seconds ({abs(avg_dlp - avg_simple)*1000:.3f} ms)")

    return {
        'num_cbcs': num_cbcs,
        'total_bidders': total_bidders,
        'avg_simple': avg_simple,
        'avg_dlp': avg_dlp,
        'simple_times': simple_times,
        'dlp_times': dlp_times
    }


def demonstrate_auction_details(num_cbcs=5, total_bidders=25, M=2):
    """
    Demonstration function to display detailed auction operations
    """
    print(f"="*80)
    print(f"DETAILED AUCTION DEMONSTRATION")
    print(f"="*80)
    print(f"Configuration: {num_cbcs} CBCs, {total_bidders} bidders, M={M}")
    print()

    bidder_distribution = calculate_bidder_distribution(
        num_cbcs, total_bidders)

    print(f"--- SIMPLE AUCTION DETAILS ---")
    simple_winners = run_simple_auction(
        num_cbcs, bidder_distribution, M, silent=False)

    print(f"\n--- DLP AUCTION DETAILS ---")
    dlp_winners, vector_commitment = run_dlp_auction(
        num_cbcs, bidder_distribution, M, silent=False)

    print(f"\n--- COMPARISON ---")
    print(f"Simple Auction winners:")
    for i, winner in enumerate(simple_winners):
        print(f"  {i+1}. {winner.id}: ${winner.bid_value}")

    print(f"DLP Auction winners:")
    for i, (user, commitment) in enumerate(dlp_winners):
        print(
            f"  {i+1}. {user.user_id}: ${user.bid_value} (commitment: {commitment})")


def run_quick_comparison():
    """
    Quick comparison test for each CBC count configuration
    """
    cbc_counts = [5, 10, 20, 50]

    print(f"="*80)
    print(f"QUICK COMPARISON TEST")
    print(f"="*80)

    for num_cbcs in cbc_counts:
        print(f"\nTesting {num_cbcs} CBCs...")
        result = test_single_configuration(num_cbcs, trials=3, verbose=False)

        print(f"  Simple: {result['avg_simple']*1000:.2f} ms")
        print(f"  DLP:    {result['avg_dlp']*1000:.2f} ms")
        print(f"  Ratio:  {result['avg_dlp']/result['avg_simple']:.2f}x")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "demo":
            # Detailed auction demonstration
            demonstrate_auction_details()

        elif command == "quick":
            # Quick comparison test
            run_quick_comparison()

        elif command == "test":
            # Individual configuration test
            num_cbcs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            trials = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            test_single_configuration(num_cbcs, trials=trials)

        else:
            print("Unknown command. Available commands:")
            print("  demo  - Show detailed auction demonstration")
            print("  quick - Run quick comparison test")
            print("  test [num_cbcs] [trials] - Test specific configuration")
    else:
        print("Cross-Chain Auction Individual Configuration Test")
        print("\nUsage:")
        print("  python individual_cbc_test.py demo")
        print("  python individual_cbc_test.py quick")
        print("  python individual_cbc_test.py test [num_cbcs] [trials]")
        print("\nExamples:")
        print("  python individual_cbc_test.py demo")
        print("  python individual_cbc_test.py test 20 10")
        print("  python individual_cbc_test.py quick")

        # Execute default simple test
        print("\nRunning default test (10 CBCs, 5 trials)...")
        test_single_configuration(10, trials=5)
