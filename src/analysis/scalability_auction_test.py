import random
import time
from time import perf_counter
from typing import List
import math
from sympy import randprime


# --- RSA-style Key Generation ---
def generate_keys(bit_length=16):
    """Generate RSA-style public and private key pairs"""
    lower = 2**(bit_length // 2 - 1)
    upper = 2**(bit_length // 2) - 1
    p = randprime(lower, upper)
    q = p
    while q == p:
        q = randprime(lower, upper)
    n = p * q
    phi = (p-1)*(q-1)
    e = 65537  # Common public exponent
    # Ensure e and phi are coprime
    while phi % e == 0:
        e = randprime(3, 1000)
    # Calculate secret exponent d
    d = pow(e, -1, phi)
    return (e, n), (d, n)


def encrypt(m, pubkey):
    """Encrypt message m using public key"""
    e, n = pubkey
    return pow(m, e, n)


def decrypt(c, privkey):
    """Decrypt ciphertext c using private key"""
    d, n = privkey
    return pow(c, d, n)


def vc_keygen(k, q):
    """Generate g for vector commitment"""
    return 2


# --- Simple Auction Classes (ordinal_auction.py based) ---
class Bidder:
    def __init__(self, bidder_id: str, bid_value: int):
        self.id = bidder_id
        self.bid_value = bid_value


class ChildBlockchain:
    def __init__(self, id: str, bidders: List[Bidder], M: int):
        self.id = id
        self.bidders = bidders
        self.M = M
        self.top_bidders = []

    def select_top_M(self) -> List[Bidder]:
        """各CBCで入札額が高額な上位M名のユーザを決定"""
        sorted_bidders = sorted(
            self.bidders, key=lambda x: x.bid_value, reverse=True)
        self.top_bidders = sorted_bidders[:self.M]
        return self.top_bidders


class ParentBlockchain:
    def __init__(self, child_chains: List[ChildBlockchain], M: int):
        self.child_chains = child_chains
        self.M = M
        self.all_winners = []

    def collect_winners(self) -> None:
        """Aggregate the M top winner from each CBC"""
        for child in self.child_chains:
            winners = child.select_top_M()
            self.all_winners.extend(winners)

    def determine_global_winners(self) -> List[Bidder]:
        """Detemine the M top winner in PBC"""
        sorted_winners = sorted(
            self.all_winners, key=lambda x: x.bid_value, reverse=True)
        return sorted_winners[:self.M]


# --- DLP-based Auction Classes (propose_auction.py based) ---
class User:
    def __init__(self, user_id, bid_value):
        self.user_id = user_id
        self.bid_value = bid_value
        self.commitment = None
        self.encrypted_commitment = None

    def create_commitment(self, g, modulus=None):
        """Create commitment c_i = g^{v_i} mod p"""
        if modulus is None:
            modulus = 2**31 - 1

        max_safe_bid = 1000
        if self.bid_value > max_safe_bid:
            raise ValueError(
                f"Bid value {self.bid_value} exceeds safe range {max_safe_bid}")

        self.commitment = pow(g, self.bid_value, modulus)
        return self.commitment

    def encrypt_commitment(self, pubkey):
        """Encrypt commitment using verifier's public key"""
        if self.commitment is None:
            raise ValueError("Commitment not created yet")
        self.encrypted_commitment = encrypt(self.commitment, pubkey)
        return self.encrypted_commitment


class CBCVerifier:
    def __init__(self, cbc_id):
        self.cbc_id = cbc_id
        self.pubkey, self.privkey = generate_keys()
        self.users = []
        self.decrypted_commitments = []
        self.top_M_winners = []

    def register_user(self, user):
        """Register a user in this CBC"""
        self.users.append(user)

    def decrypt_commitments(self):
        """Decrypt all received encrypted commitments"""
        self.decrypted_commitments = []
        for user in self.users:
            if user.encrypted_commitment is not None:
                decrypted = decrypt(user.encrypted_commitment, self.privkey)
                self.decrypted_commitments.append((user, decrypted))
        return self.decrypted_commitments

    def select_top_M(self, M):
        """Select top M users based on commitment values"""
        sorted_commitments = sorted(self.decrypted_commitments,
                                    key=lambda x: x[1], reverse=True)
        self.top_M_winners = sorted_commitments[:M]
        return self.top_M_winners

    def encrypt_winners_for_pbc(self, pbc_pubkey):
        """Encrypt top M winners' commitments for PBC"""
        encrypted_winners = []
        for user, commitment in self.top_M_winners:
            encrypted = encrypt(commitment, pbc_pubkey)
            encrypted_winners.append((user, encrypted))
        return encrypted_winners


class PBCVerifier:
    def __init__(self):
        self.pubkey, self.privkey = generate_keys()
        self.all_encrypted_winners = []
        self.all_decrypted_commitments = []
        self.final_winners = []
        self.random_values = []
        self.vector_commitment = None

    def collect_encrypted_winners(self, cbc_encrypted_winners):
        """Collect encrypted winners from all CBCs"""
        self.all_encrypted_winners.extend(cbc_encrypted_winners)

    def decrypt_all_commitments(self):
        """Decrypt all commitment values from CBCs"""
        self.all_decrypted_commitments = []
        for user, encrypted_commitment in self.all_encrypted_winners:
            decrypted = decrypt(encrypted_commitment, self.privkey)
            self.all_decrypted_commitments.append((user, decrypted))
        return self.all_decrypted_commitments

    def select_final_winners(self, M):
        """Select top M winners globally"""
        sorted_commitments = sorted(
            self.all_decrypted_commitments, key=lambda x: x[1], reverse=True)
        self.final_winners = sorted_commitments[:M]
        return self.final_winners

    def generate_random_values(self, M):
        """Generate random values for vector commitment"""
        self.random_values = [random.randint(1, 100) for _ in range(M)]
        return self.random_values

    def compute_vector_commitment(self, p):
        """Compute vector commitment"""
        if not self.final_winners or not self.random_values:
            raise ValueError("Final winners or random values not set")

        self.vector_commitment = 1
        for i, (user, commitment) in enumerate(self.final_winners):
            r_i = self.random_values[i]
            self.vector_commitment = (
                self.vector_commitment * pow(commitment, r_i)) % p

        return self.vector_commitment


# --- Bidder Generation Functions ---
def generate_random_bidders_simple(chain_id: str, n: int) -> List[Bidder]:
    """Generate random bidders for Simple Auction"""
    bidders = []
    for i in range(1, n + 1):
        bidder_id = f"{chain_id}_Bidder{i}"
        bid_value = random.randint(50, 300)  # $50-$300 range
        bidders.append(Bidder(bidder_id, bid_value))
    return bidders


def generate_random_users_dlp(chain_id: str, n: int) -> List[User]:
    """Generate random users for DLP Auction"""
    users = []
    for i in range(1, n + 1):
        user_id = f"{chain_id}_User{i}"
        bid_value = random.randint(50, 300)  # $50-$300 range
        users.append(User(user_id, bid_value))
    return users


# --- Bidder Distribution Calculator ---
def calculate_bidder_distribution(num_cbcs: int, total_bidders: int) -> List[int]:
    """Calculate bidder distribution across CBCs"""
    base_count = total_bidders // num_cbcs
    remainder = total_bidders % num_cbcs

    distribution = [base_count] * num_cbcs
    for i in range(remainder):
        distribution[i] += 1

    return distribution


# --- Simple Auction Implementation ---
def run_simple_auction(num_cbcs: int, bidder_counts: List[int], M: int, silent=True):
    """Run Simple Auction with specified CBC count"""
    if not silent:
        print(f"=== Simple Auction: {num_cbcs} CBCs ===")
        print(f"Total bidders: {sum(bidder_counts)}")
        print(f"Bidder distribution: {bidder_counts}")

    # Create Child Blockchains
    child_blockchains = []
    for i in range(num_cbcs):
        chain_id = f"CBC{chr(65 + i % 26)}{i // 26 + 1 if i >= 26 else ''}"
        bidder_count = bidder_counts[i]

        # Generate random bidders
        bidders = generate_random_bidders_simple(chain_id, bidder_count)
        cbc = ChildBlockchain(chain_id, bidders, M)
        child_blockchains.append(cbc)

    # Parent Blockchain processing
    parent = ParentBlockchain(child_blockchains, M)
    parent.collect_winners()
    final_winners = parent.determine_global_winners()

    if not silent:
        print(f"Final winners ({M}):")
        for i, winner in enumerate(final_winners):
            print(f"  {i+1}. {winner.id}: ${winner.bid_value}")

    return final_winners


# --- DLP Auction Implementation ---
def run_dlp_auction(num_cbcs: int, bidder_counts: List[int], M: int, silent=True):
    """Run DLP-based Auction with specified CBC count"""
    if not silent:
        print(f"=== DLP Auction: {num_cbcs} CBCs ===")
        print(f"Total bidders: {sum(bidder_counts)}")
        print(f"Bidder distribution: {bidder_counts}")

    # Setup phase
    g = vc_keygen(1, 100)
    large_prime = 2**31 - 1
    pbc_verifier = PBCVerifier()

    # Create CBC verifiers
    cbc_verifiers = []
    for i in range(num_cbcs):
        cbc_id = f"CBC{chr(65 + i % 26)}{i // 26 + 1 if i >= 26 else ''}"
        cbc_verifier = CBCVerifier(cbc_id)
        cbc_verifiers.append(cbc_verifier)

    # CBC Round
    for i, cbc_verifier in enumerate(cbc_verifiers):
        bidder_count = bidder_counts[i]
        users = generate_random_users_dlp(cbc_verifier.cbc_id, bidder_count)

        # Register users and process commitments
        for user in users:
            cbc_verifier.register_user(user)
            commitment = user.create_commitment(g, large_prime)
            encrypted = user.encrypt_commitment(cbc_verifier.pubkey)

        # CBC processing
        cbc_verifier.decrypt_commitments()
        top_winners = cbc_verifier.select_top_M(M)
        encrypted_winners = cbc_verifier.encrypt_winners_for_pbc(
            pbc_verifier.pubkey)
        pbc_verifier.collect_encrypted_winners(encrypted_winners)

    # PBC Round
    pbc_verifier.decrypt_all_commitments()
    final_winners = pbc_verifier.select_final_winners(M)
    random_values = pbc_verifier.generate_random_values(M)
    p = pbc_verifier.pubkey[1]
    vector_commitment = pbc_verifier.compute_vector_commitment(p)

    if not silent:
        print(f"Final winners ({M}):")
        for i, (user, commitment) in enumerate(final_winners):
            print(f"  {i+1}. {user.user_id}: ${user.bid_value}")

    return final_winners, vector_commitment


# --- Performance Testing Functions ---
def run_scalability_test(cbc_counts: List[int], n_trials: int = 10):
    """Run scalability test for different CBC counts"""
    M = 2  # Winners per CBC
    base_total_bidders = 50  # Base number of total bidders

    print("="*80)
    print("CROSS-CHAIN AUCTION SCALABILITY TEST")
    print("="*80)
    print(f"Test conditions:")
    print(f"- Trials per configuration: {n_trials}")
    print(f"- Winners per CBC (M): {M}")
    print(f"- Bid range: $50-$300")
    print(f"- Base total bidders: {base_total_bidders}")
    print()

    results = {}

    for num_cbcs in cbc_counts:
        print(f"\n{'='*60}")
        print(f"TESTING: {num_cbcs} Child Blockchains")
        print(f"{'='*60}")

        # Scale total bidders with CBC count to maintain realistic load
        total_bidders = base_total_bidders + (num_cbcs - 5) * 5
        bidder_distribution = calculate_bidder_distribution(
            num_cbcs, total_bidders)

        print(f"Configuration:")
        print(f"  - Number of CBCs: {num_cbcs}")
        print(f"  - Total bidders: {total_bidders}")
        print(f"  - Average bidders per CBC: {total_bidders / num_cbcs:.1f}")
        print(f"  - Bidder distribution: {bidder_distribution}")
        print()

        simple_times = []
        dlp_times = []

        for trial in range(n_trials):
            print(f"Trial {trial + 1}/{n_trials}:", end=" ")

            # Test Simple Auction
            start_time = perf_counter()
            simple_winners = run_simple_auction(
                num_cbcs, bidder_distribution, M, silent=True)
            simple_time = perf_counter() - start_time
            simple_times.append(simple_time)

            # Test DLP Auction
            start_time = perf_counter()
            dlp_winners, vector_commitment = run_dlp_auction(
                num_cbcs, bidder_distribution, M, silent=True)
            dlp_time = perf_counter() - start_time
            dlp_times.append(dlp_time)

            print(f"Simple={simple_time:.6f}s, DLP={dlp_time:.6f}s")

        # Calculate statistics
        avg_simple = sum(simple_times) / len(simple_times)
        avg_dlp = sum(dlp_times) / len(dlp_times)
        std_simple = math.sqrt(
            sum((t - avg_simple)**2 for t in simple_times) / len(simple_times))
        std_dlp = math.sqrt(
            sum((t - avg_dlp)**2 for t in dlp_times) / len(dlp_times))

        # Store results
        results[num_cbcs] = {
            'total_bidders': total_bidders,
            'avg_simple': avg_simple,
            'avg_dlp': avg_dlp,
            'std_simple': std_simple,
            'std_dlp': std_dlp,
            'simple_times': simple_times,
            'dlp_times': dlp_times
        }

        # Display results for this configuration
        print(f"\nResults for {num_cbcs} CBCs:")
        print(f"  Simple Auction:")
        print(f"    Average: {avg_simple:.6f}s ({avg_simple*1000:.3f}ms)")
        print(f"    Std Dev: ±{std_simple:.6f}s")
        print(
            f"    Range: {min(simple_times):.6f}s - {max(simple_times):.6f}s")
        print(f"  DLP Auction:")
        print(f"    Average: {avg_dlp:.6f}s ({avg_dlp*1000:.3f}ms)")
        print(f"    Std Dev: ±{std_dlp:.6f}s")
        print(f"    Range: {min(dlp_times):.6f}s - {max(dlp_times):.6f}s")
        print(
            f"  Performance Ratio: DLP is {avg_dlp/avg_simple:.2f}x {'faster' if avg_dlp < avg_simple else 'slower'}")

    return results


def display_summary_results(results):
    """Display comprehensive summary of all results"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE SCALABILITY ANALYSIS")
    print(f"{'='*80}")

    # Summary table
    print(f"\n{'CBC Count':<10} {'Total Bidders':<15} {'Simple Avg (ms)':<15} {'DLP Avg (ms)':<15} {'Ratio':<10}")
    print("-" * 80)

    for num_cbcs, data in results.items():
        simple_ms = data['avg_simple'] * 1000
        dlp_ms = data['avg_dlp'] * 1000
        ratio = data['avg_dlp'] / data['avg_simple']

        print(
            f"{num_cbcs:<10} {data['total_bidders']:<15} {simple_ms:<15.3f} {dlp_ms:<15.3f} {ratio:<10.2f}x")

    # Scalability analysis
    print(f"\n{'='*60}")
    print("SCALABILITY ANALYSIS")
    print(f"{'='*60}")

    cbc_counts = list(results.keys())

    # Calculate growth rates
    print("\nExecution Time Growth Analysis:")
    for i in range(1, len(cbc_counts)):
        prev_cbcs = cbc_counts[i-1]
        curr_cbcs = cbc_counts[i]

        prev_simple = results[prev_cbcs]['avg_simple']
        curr_simple = results[curr_cbcs]['avg_simple']
        simple_growth = (curr_simple - prev_simple) / prev_simple * 100

        prev_dlp = results[prev_cbcs]['avg_dlp']
        curr_dlp = results[curr_cbcs]['avg_dlp']
        dlp_growth = (curr_dlp - prev_dlp) / prev_dlp * 100

        print(f"  {prev_cbcs} → {curr_cbcs} CBCs:")
        print(f"    Simple Auction: {simple_growth:+.1f}% change")
        print(f"    DLP Auction: {dlp_growth:+.1f}% change")

    # Performance recommendations
    print(f"\n{'='*60}")
    print("PERFORMANCE RECOMMENDATIONS")
    print(f"{'='*60}")

    best_simple_cbcs = min(
        results.keys(), key=lambda x: results[x]['avg_simple'])
    best_dlp_cbcs = min(results.keys(), key=lambda x: results[x]['avg_dlp'])

    print(f"Best Simple Auction performance: {best_simple_cbcs} CBCs")
    print(f"Best DLP Auction performance: {best_dlp_cbcs} CBCs")

    # Determine optimal configuration
    optimal_configs = []
    for num_cbcs, data in results.items():
        if data['avg_dlp'] < data['avg_simple']:
            optimal_configs.append(
                (num_cbcs, data['avg_dlp']/data['avg_simple']))

    if optimal_configs:
        best_config = min(optimal_configs, key=lambda x: x[1])
        print(
            f"Optimal configuration: {best_config[0]} CBCs (DLP is {1/best_config[1]:.2f}x faster)")
    else:
        print("Simple Auction consistently outperforms DLP Auction in this test range")


# --- Main Execution ---
if __name__ == "__main__":
    # Configuration for scalability test
    cbc_test_counts = [5, 10, 20, 50]
    n_trials = 15  # Number of trials per configuration

    print("Cross-Chain Auction Scalability Testing")
    print("Testing CBC counts:", cbc_test_counts)
    print(f"Trials per configuration: {n_trials}")
    print("\nStarting test...")

    # Run comprehensive scalability test
    start_time = perf_counter()
    results = run_scalability_test(cbc_test_counts, n_trials)
    total_time = perf_counter() - start_time

    # Display comprehensive results
    display_summary_results(results)

    print(f"\n{'='*80}")
    print(f"TOTAL TEST EXECUTION TIME: {total_time:.2f} seconds")
    print(f"{'='*80}")
    print("Test completed successfully!")
