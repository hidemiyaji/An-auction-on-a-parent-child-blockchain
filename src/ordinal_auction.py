from typing import List
import random
import time
from time import perf_counter


class Bidder:
    def __init__(self, bidder_id: str, bid_value: int):
        self.id = bidder_id
        self.bid_value = bid_value


class ChildBlockchain:
    def __init__(self, id: str, bidders: List[Bidder], M: int):
        self.id = id
        self.bidders = bidders
        self.M = M
        self.top_bidders = []  # Stores top M bidders

    def select_top_M(self) -> List[Bidder]:
        """Determine the top M users with the highest bid amounts in each CBC"""
        # Sort by bid amount in descending order
        sorted_bidders = sorted(
            self.bidders, key=lambda x: x.bid_value, reverse=True)
        self.top_bidders = sorted_bidders[:self.M]
        return self.top_bidders


class ParentBlockchain:
    def __init__(self, child_chains: List[ChildBlockchain], M: int):
        self.child_chains = child_chains
        self.M = M
        self.all_winners = []  # Store winners from each CBC

    def collect_winners(self) -> None:
        """Aggregate top M bidders from each CBC"""
        for child in self.child_chains:
            winners = child.select_top_M()
            self.all_winners.extend(winners)

    def determine_global_winners(self) -> List[Bidder]:
        """Determine the top M users with the highest bid amounts in PBC"""
        # Sort all winners by bid amount in descending order
        sorted_winners = sorted(
            self.all_winners, key=lambda x: x.bid_value, reverse=True)
        return sorted_winners[:self.M]

        return sorted_winners[:self.M]


def generate_random_bidders(chain_id: str, n: int) -> List[Bidder]:
    """
    Function to generate n random bidders for test.py

    Args:
        chain_id: Chain ID (e.g., "CBCA", "CBCB")
        n: Number of bidders to generate

    Returns:
        List of Bidder objects for test.py
    """
    bidders = []
    for i in range(1, n + 1):
        bidder_id = f"{chain_id}_Bidder{i}"
        # Generate random bid values from $50 to $300 (same range as test-verify.py)
        bid_value = random.randint(50, 300)
        bidders.append(Bidder(bidder_id, bid_value))
    return bidders


def run_simple_auction(bidder_counts, num_child_blockchains, M, silent=False):
    """
    Function to execute simple auction (same experimental conditions as test-verify.py)

    Args:
        bidder_counts: List of number of bidders in each CBC
        num_child_blockchains: Number of ChildBlockchains
        M: Number of top bidders selected from each CBC
        silent: If True, suppress detailed output

    Returns:
        final_winners: List of final winners
    """
    if not silent:
        print(f"=== Simple Auction Execution ===")
        print(f"Number of Child Blockchains: {num_child_blockchains}")
        print(f"Selected from each CBC: Top {M} bidders")
        print(f"Total bidders: {sum(bidder_counts)}")
        print(f"Bidder distribution: {bidder_counts}")
        print()

    # Create ChildBlockchains
    child_blockchains = []
    for i in range(num_child_blockchains):
        chain_id = f"CBC{chr(65 + i)}"  # CBCA, CBCB, CBCC, ...
        bidder_count = bidder_counts[i]

        # Generate random bidders
        bidders = generate_random_bidders(chain_id, bidder_count)

        # Create ChildBlockchain
        cbc = ChildBlockchain(chain_id, bidders, M)
        child_blockchains.append(cbc)

        if not silent:
            print(f"{chain_id} ({bidder_count} bidders):")
            for bidder in bidders:
                print(f"  {bidder.id}: ${bidder.bid_value}")

            # Display top M bidders from each CBC
            top_bidders = cbc.select_top_M()
            print(f"  → Top {M} bidders:")
            for j, bidder in enumerate(top_bidders):
                print(f"    {j+1}. {bidder.id}: ${bidder.bid_value}")
            print()

    # Final selection in ParentBlockchain
    parent = ParentBlockchain(child_blockchains, M)
    parent.collect_winners()
    final_winners = parent.determine_global_winners()

    if not silent:
        print(f"=== Final Result: Overall Top {M} Bidders ===")
        for i, winner in enumerate(final_winners):
            print(f"{i+1}. {winner.id}: ${winner.bid_value}")
        print()

    return final_winners


def run_performance_test(bidder_counts, num_child_blockchains, M, n_trials=5):
    """
    Execute performance test for simple auction

    Args:
        bidder_counts: List of number of bidders in each CBC
        num_child_blockchains: Number of ChildBlockchains
        M: Number of top bidders selected from each CBC
        n_trials: Number of executions
    """
    print(f"=== Simple Auction Performance Test ===")
    print(f"Number of executions: {n_trials}")
    print(f"Number of Child Blockchains: {num_child_blockchains}")
    print(f"Selected from each CBC: Top {M} bidders")
    print(f"Total bidders: {sum(bidder_counts)}")
    print(f"Bidder distribution: {bidder_counts}")
    print()

    execution_times = []

    for trial in range(n_trials):
        start_time = perf_counter()

        # Execute simple auction (without detailed output)
        final_winners = run_simple_auction(
            bidder_counts, num_child_blockchains, M, silent=True
        )

        execution_time = perf_counter() - start_time
        execution_times.append(execution_time)

        print(f"Trial {trial + 1}: {execution_time:.6f} seconds")

    # Display statistical information
    avg_time = sum(execution_times) / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)

    print(f"\n=== Performance Statistics ===")
    print(f"Average execution time: {avg_time:.6f} seconds ({avg_time*1000:.3f} ms)")
    print(f"Minimum execution time: {min_time:.6f} seconds ({min_time*1000:.3f} ms)")
    print(f"Maximum execution time: {max_time:.6f} seconds ({max_time*1000:.3f} ms)")
    print(f"Average time per trial: {avg_time:.6f} seconds per trial")


# Execution example with same experimental conditions as test-verify.py
if __name__ == "__main__":
    # Same experimental settings as test-verify.py
    bidder_counts = [3, 5, 4, 6, 2, 7, 8, 3, 5, 4]  # Number of bidders in each ChildBlockchain
    num_child_blockchains = 10  # Number of ChildBlockchains
    M = 2  # Number of top bidders selected from each ChildBlockchain

    print("Please select:")
    print("1. Simple Auction Execution (detailed display)")
    print("2. Simple Auction Execution (results only)")
    print("3. Performance Test (multiple executions)")

    choice = input("Selection (1, 2, 3): ").strip()

    if choice == "1":
        # Execute auction with detailed display
        start_time = perf_counter()
        final_winners = run_simple_auction(
            bidder_counts, num_child_blockchains, M, silent=False)
        execution_time = perf_counter() - start_time
        print(
            f"Execution time: {execution_time:.6f} seconds ({execution_time*1000:.3f} ms)")

    elif choice == "2":
        # Display results only
        start_time = perf_counter()
        final_winners = run_simple_auction(
            bidder_counts, num_child_blockchains, M, silent=True)
        execution_time = perf_counter() - start_time

        print(f"=== Simple Auction Results ===")
        print(f"Final winners (top {M} bidders):")
        for i, winner in enumerate(final_winners):
            print(f"{i+1}. {winner.id}: ${winner.bid_value}")
        print(
            f"\nExecution time: {execution_time:.6f} seconds ({execution_time*1000:.3f} ms)")

    elif choice == "3":
        # Performance test
        print("\nPlease select number of executions:")
        print("1. 10 times")
        print("2. 20 times")
        print("3. 50 times")
        print("4. 100 times")
        print("5. Custom number")

        trials_choice = input("Selection (1, 2, 3, 4, 5): ").strip()

        if trials_choice == "1":
            n_trials = 10
        elif trials_choice == "2":
            n_trials = 20
        elif trials_choice == "3":
            n_trials = 50
        elif trials_choice == "4":
            n_trials = 100
        elif trials_choice == "5":
            try:
                n_trials = int(input("Enter number of executions: "))
            except ValueError:
                print("Invalid input. Executing with default value of 10 times.")
                n_trials = 10
        else:
            print("Invalid selection. Executing with default value of 10 times.")
            n_trials = 10

        run_performance_test(bidder_counts, num_child_blockchains, M, n_trials)

    else:
        print("Invalid selection. Please select 1, 2, or 3.")
