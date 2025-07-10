import ordinal_auction
import math
import sys
import time
import random
import concurrent.futures
# Use perf_counter for more precise time measurement
from time import perf_counter
from ordinal_auction import Bidder, ChildBlockchain, ParentBlockchain
# Import necessary classes and functions from auction.py
from propose_auction import User, CBCVerifier, PBCVerifier, vc_keygen, verify_commitment_ordering

# Increase the limit for large integer string conversion
sys.set_int_max_str_digits(10000)


def generate_random_bidders_for_auction(chain_id: str, n: int) -> list:
    """
    Function to generate n random bidders for auction.py

    Args:
        chain_id: Chain ID (e.g., "CBCA", "CBCB")
        n: Number of bidders to generate

    Returns:
        List of User objects for auction.py
    """
    bidders = []
    for i in range(1, n + 1):
        bidder_id = f"{chain_id}_Bidder{i}"
        # Generate random bid values from $50 to $300
        bid_value = random.randint(50, 300)
        bidders.append(User(bidder_id, bid_value))
    return bidders


def generate_random_bidders(chain_id: str, n: int) -> list:
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
        # Generate random bid values from $50 to $300
        bid_value = random.randint(50, 300)
        bidders.append(Bidder(bidder_id, bid_value))
    return bidders


def run_performance_test(bidder_counts, num_child_blockchains, M, n_trials=5):
    """
    Execute n times and measure average execution time

    Args:
        bidder_counts: List of number of bidders in each CBC
        num_child_blockchains: Number of CBCs
        M: Number of winners to select
        n_trials: Number of executions
    """
    print(f"\n{'='*60}")
    print(f"PERFORMANCE TEST ({n_trials} trials)")
    print(f"{'='*60}")

    times_simple = []
    times_dlp = []

    for trial in range(1, n_trials + 1):
        print(f"\n--- Trial {trial}/{n_trials} ---")

        # Simple auction (test.py) measurement
        print("Testing Simple Auction (test.py)...")
        start_time = perf_counter()

        # Original auction using test.py
        child_blockchains = []

        for i in range(num_child_blockchains):
            chain_id = f"CBC{chr(65 + i)}"
            bidder_count = bidder_counts[i]

            # Generate random bidders
            bidders = generate_random_bidders(chain_id, bidder_count)
            child_blockchain = ChildBlockchain(chain_id, bidders, M=M)
            child_blockchains.append(child_blockchain)

        # Parent Blockchain setup
        parent = ParentBlockchain(child_blockchains, M=M)
        parent.collect_winners()
        global_winners = parent.determine_global_winners()

        simple_time = perf_counter() - start_time
        times_simple.append(simple_time)
        print(f"Simple auction time: {simple_time:.6f} seconds")

        # DLP auction (auction.py) measurement
        print("Testing DLP-based Auction (auction.py)...")
        start_time = perf_counter()

        # Complete DLP-based auction using auction.py (suppress output)
        final_winners, vector_commitment = run_auction_with_generated_data(
            bidder_counts, num_child_blockchains, M, silent=True
        )

        dlp_time = perf_counter() - start_time
        times_dlp.append(dlp_time)
        print(f"DLP auction time: {dlp_time:.6f} seconds")

    # Calculate statistics
    avg_simple = sum(times_simple) / len(times_simple)
    avg_dlp = sum(times_dlp) / len(times_dlp)

    std_simple = math.sqrt(
        sum((t - avg_simple)**2 for t in times_simple) / len(times_simple))
    std_dlp = math.sqrt(
        sum((t - avg_dlp)**2 for t in times_dlp) / len(times_dlp))

    # Display results
    print(f"\n{'='*60}")
    print(f"PERFORMANCE RESULTS ({n_trials} trials)")
    print(f"{'='*60}")
    print(f"Configuration:")
    print(f"  Child Blockchains: {num_child_blockchains}")
    print(f"  Total Bidders: {sum(bidder_counts)}")
    print(f"  Winners per CBC: {M}")
    print(f"  Bidder distribution: {bidder_counts}")

    print(f"\nSimple Auction (test.py):")
    print(
        f"  Average time: {avg_simple:.6f} seconds ({avg_simple*1000:.3f} ms)")
    print(f"  Standard deviation: ± {std_simple:.6f} seconds")
    print(f"  Individual times: {[f'{t:.6f}' for t in times_simple]}")

    print(f"\nDLP-based Auction (auction.py):")
    print(f"  Average time: {avg_dlp:.6f} seconds ({avg_dlp*1000:.3f} ms)")
    print(f"  Standard deviation: ± {std_dlp:.6f} seconds")
    print(f"  Individual times: {[f'{t:.6f}' for t in times_dlp]}")

    print(f"\nPerformance Comparison:")
    speedup = avg_dlp / avg_simple if avg_simple > 0 else float('inf')
    print(f"  DLP auction is {speedup:.2f}x slower than simple auction")
    print(
        f"  Overhead: {(avg_dlp - avg_simple):.6f} seconds ({(avg_dlp - avg_simple)*1000:.3f} ms)")

    # Also display minimum and maximum times
    print(f"\nDetailed Statistics:")
    print(
        f"  Simple Auction - Min: {min(times_simple):.6f}s, Max: {max(times_simple):.6f}s")
    print(
        f"  DLP Auction - Min: {min(times_dlp):.6f}s, Max: {max(times_dlp):.6f}s")

    # Also display total execution time for performance test
    performance_test_total_time = sum(times_simple) + sum(times_dlp)
    print(f"\nPerformance Test Summary:")
    print(
        f"  Total test execution time: {performance_test_total_time:.6f} seconds ({performance_test_total_time*1000:.3f} ms)")
    print(
        f"  Average time per trial: {performance_test_total_time/n_trials:.6f} seconds")

    # Additional statistical information (in comment format)
    # Detailed analysis of average time per execution:
    # - Simple Auction average time: {avg_simple:.6f} seconds per trial
    # - DLP Auction average time: {avg_dlp:.6f} seconds per trial
    # - Combined average time: {(avg_simple + avg_dlp):.6f} seconds per trial
    # - Efficiency indicator: DLP/Simple ratio = {speedup:.2f}x
    # - Standard deviation comparison: Simple±{std_simple:.6f}s vs DLP±{std_dlp:.6f}s
    print(f"\n# Additional Analysis (Detailed average time per execution):")
    print(
        f"# - Simple Auction average time: {avg_simple:.6f} seconds per trial")
    print(f"# - DLP Auction average time: {avg_dlp:.6f} seconds per trial")
    print(
        f"# - Combined average time: {(avg_simple + avg_dlp):.6f} seconds per trial")
    print(f"# - Efficiency indicator: DLP/Simple ratio = {speedup:.2f}x")
    print(
        f"# - Standard deviation comparison: Simple±{std_simple:.6f}s vs DLP±{std_dlp:.6f}s")


def run_auction_with_generated_data(bidder_counts, num_child_blockchains, M, silent=False):
    """
    Execute auction using auction.py code

    Args:
        bidder_counts: List of number of bidders in each CBC
        num_child_blockchains: Number of CBCs
        M: Number of winners to select
        silent: If True, suppress detailed output
    """
    if not silent:
        print("=" * 60)
        print("M+1st-price Sealed Bid Auction using auction.py")
        print("=" * 60)

    # Setup Phase
    if not silent:
        print("\n--- Setup Phase ---")

    # 1. PBC generates g
    g = vc_keygen(1, 100)
    if not silent:
        print(f"Generated g: {g}")

    # Use a large prime as modulus
    large_prime = 2**31 - 1  # Mersenne prime

    # 2. Verify commitment ordering is preserved
    if not silent:
        print("\n--- Verifying Commitment Ordering ---")
    # Suppress output during silent execution when running verify_commitment_ordering
    import io
    import sys
    if silent:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    ordering_preserved = verify_commitment_ordering(g, large_prime, 300)

    if silent:
        sys.stdout = old_stdout

    if not ordering_preserved:
        if not silent:
            print("Warning: Commitment ordering may not be preserved!")
        return None, None

    # 2. PBC verifier setup
    pbc_verifier = PBCVerifier()
    if not silent:
        print(f"\nPBC public key: {pbc_verifier.pubkey}")

    # 3. Create CBC verifiers
    cbc_verifiers = []
    for i in range(num_child_blockchains):
        cbc_id = f"CBC{chr(65 + i)}"
        cbc_verifier = CBCVerifier(cbc_id)
        if not silent:
            print(f"{cbc_id} public key: {cbc_verifier.pubkey}")
        cbc_verifiers.append(cbc_verifier)

    # CBC Round
    if not silent:
        print(
            f"\n--- CBC Round (Processing {num_child_blockchains} Child Blockchains) ---")

    all_users_info = []  # For statistics

    for i, cbc_verifier in enumerate(cbc_verifiers):
        if not silent:
            print(f"\n--- Processing {cbc_verifier.cbc_id} ---")

        # Generate users for this CBC
        bidder_count = bidder_counts[i]
        users = generate_random_bidders_for_auction(
            cbc_verifier.cbc_id, bidder_count)

        # Register users in CBC
        for user in users:
            cbc_verifier.register_user(user)
            all_users_info.append(user)

        # Bidding phase
        if not silent:
            print("Bidding phase:")

        for user in users:
            # Create commitment c_i = g^{v_i} mod p (using bid value directly)
            commitment = user.create_commitment(g, large_prime)

            # Encrypt commitment
            encrypted = user.encrypt_commitment(cbc_verifier.pubkey)

            if not silent:
                print(f"  {user.user_id}: bid=${user.bid_value}, "
                      f"commitment=g^{user.bid_value} mod {large_prime} = {commitment}")

        # CBC verifier processes
        if not silent:
            print("CBC verifier processing:")

        # Decrypt all commitments
        cbc_verifier.decrypt_commitments()

        # Select top M winners
        top_winners = cbc_verifier.select_top_M(M)
        if not silent:
            print(f"  Top {M} winners in {cbc_verifier.cbc_id}:")
            for user, commitment in top_winners:
                print(f"    {user.user_id}: commitment={commitment}")

        # Encrypt winners for PBC
        encrypted_winners = cbc_verifier.encrypt_winners_for_pbc(
            pbc_verifier.pubkey)
        pbc_verifier.collect_encrypted_winners(encrypted_winners)

    # PBC Round
    if not silent:
        print(f"\n--- PBC Round ---")

    # Decrypt all commitments from CBCs
    if not silent:
        print("Decrypting commitments from all CBCs...")
    pbc_verifier.decrypt_all_commitments()

    if not silent:
        print("All candidates:")
        for user, commitment in pbc_verifier.all_decrypted_commitments:
            print(f"  {user.user_id}: commitment={commitment}")

    # Select final top M winners
    final_winners = pbc_verifier.select_final_winners(M)

    if not silent:
        print(f"\nFinal Top {M} Winners:")
        for i, (user, commitment) in enumerate(final_winners):
            print(
                f"  {i+1}. {user.user_id}: bid=${user.bid_value}, commitment={commitment}")

    # Generate random values and compute vector commitment
    random_values = pbc_verifier.generate_random_values(M)
    p = pbc_verifier.pubkey[1]  # Use n as substitute for p
    vector_commitment = pbc_verifier.compute_vector_commitment(p)

    if not silent:
        print(f"\nVector Commitment:")
        print(f"  Random values: {random_values}")
        print(f"  Vector commitment C: {vector_commitment}")

        # Statistics
        print(f"\n{'='*50}")
        print("Auction Statistics:")
        print(f"{'='*50}")
        total_bidders = sum(bidder_counts)
        print(f"Total Child Blockchains: {num_child_blockchains}")
        print(f"Total Bidders: {total_bidders}")
        print(
            f"Average Bidders per Chain: {total_bidders / num_child_blockchains:.1f}")
        print(f"Winners per CBC: {M}")
        print(f"Final Global Winners: {M}")

    return final_winners, vector_commitment


# Example Usage
if __name__ == "__main__":
    # Start measuring total program execution time
    total_start_time = perf_counter()

    # Set the number of bidders for each ChildBlockchain individually (10 ChildBlockchains)
    # Number of bidders in each ChildBlockchain
    bidder_counts = [3, 5, 4, 6, 2, 7, 8, 3, 5, 4]
    num_child_blockchains = 10  # Number of ChildBlockchains
    M = 2  # Number of top bidders selected from each ChildBlockchain

    print("Please select:")
    print("1. Simple auction execution with test.py")
    print("2. Complete DLP-based auction execution with auction.py")
    print("3. Execute both and compare")
    print("4. Performance test (execute n times and measure average time)")

    choice = input("Selection (1, 2, 3, 4): ").strip()

    if choice == "4":
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
            n_trials = int(input("Enter number of executions: "))
        else:
            print("Invalid selection. Executing with default value of 10 times.")
            n_trials = 10

        run_performance_test(bidder_counts, num_child_blockchains, M, n_trials)
    elif choice == "1" or choice == "3":
        # Measure execution time for selections 1 and 3 individually
        section_start_time = perf_counter()

        print("\n" + "="*60)
        print("TEST.PY SIMPLE AUCTION")
        print("="*60)

        # Original auction using test.py
        child_blockchains = []

        for i in range(num_child_blockchains):
            chain_id = f"CBC{chr(65 + i)}"
            bidder_count = bidder_counts[i]

            # Generate random bidders
            bidders = generate_random_bidders(chain_id, bidder_count)
            child_blockchain = ChildBlockchain(chain_id, bidders, M=M)
            child_blockchains.append(child_blockchain)

            # Display information of generated bidders
            print(f"\n{chain_id} Bidders ({bidder_count} bidders):")
            for bidder in bidders:
                print(f"  {bidder.id}: ${bidder.bid_value}")

        # Parent Blockchain setup
        parent = ParentBlockchain(child_blockchains, M=M)
        parent.collect_winners()
        global_winners = parent.determine_global_winners()

        # Display statistical information for each ChildBlockchain
        print(f"\n{'='*50}")
        print("Child Blockchain Statistics:")
        print(f"{'='*50}")
        total_bidders = sum(bidder_counts)
        print(f"Total Child Blockchains: {num_child_blockchains}")
        print(f"Total Bidders: {total_bidders}")
        print(
            f"Average Bidders per Chain: {total_bidders / num_child_blockchains:.1f}")

        # Output results
        print(f"\n{'='*50}")
        print(f"Global Top {M+1} Winners:")
        print(f"{'='*50}")
        for i, winner in enumerate(global_winners):
            print(
                f"{i+1}. {winner.id} (Bid: ${winner.bid_value}, Commitment: {winner.commitment})")

        simple_execution_time = perf_counter() - section_start_time
        print(f"\n{'='*50}")
        print(
            f"Simple Auction Execution Time: {simple_execution_time:.6f} seconds ({simple_execution_time*1000:.3f} ms)")
        print(f"{'='*50}")

    elif choice == "2" or choice == "3":
        # Measure execution time for selections 2 and 3 individually
        section_start_time = perf_counter()

        if choice == "3":
            print("\n\n")

        print("="*60)
        print("AUCTION.PY DLP-BASED AUCTION")
        print("="*60)

        # Complete DLP-based auction using auction.py
        final_winners, vector_commitment = run_auction_with_generated_data(
            bidder_counts, num_child_blockchains, M
        )

        print("\n" + "=" * 60)
        print("DLP-based Auction Complete!")
        print("=" * 60)

        dlp_execution_time = perf_counter() - section_start_time
        print(
            f"\nDLP Auction Execution Time: {dlp_execution_time:.6f} seconds ({dlp_execution_time*1000:.3f} ms)")
        print("=" * 60)
    else:
        print("Invalid selection. Please select 1, 2, 3, or 4.")

    # Display total program execution time
    total_execution_time = perf_counter() - total_start_time
    print(f"\n{'='*60}")
    print(f"TOTAL PROGRAM EXECUTION TIME")
    print(f"{'='*60}")
    print(
        f"Total time: {total_execution_time:.6f} seconds ({total_execution_time*1000:.3f} ms)")
    print(f"Program finished successfully!")
    print(f"{'='*60}")
