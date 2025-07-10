import random
from sympy import randprime

# --- Key Generation (RSA-style) ---


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


# --- Encryption ---


def encrypt(m, pubkey):
    """Encrypt message m using public key"""
    e, n = pubkey
    return pow(m, e, n)


# --- Decryption ---


def decrypt(c, privkey):
    """Decrypt ciphertext c using private key"""
    d, n = privkey
    return pow(c, d, n)


# --- Vector Commitment Key Generation ---


def vc_keygen(k, q):
    """Generate g for vector commitment"""
    # Use 2 as the generator for demonstration
    return 2


# --- User Class ---


class User:
    def __init__(self, user_id, bid_value):
        self.user_id = user_id
        self.bid_value = bid_value
        self.commitment = None
        self.encrypted_commitment = None

    def create_commitment(self, g, modulus=None):
        """Create commitment c_i = g^{v_i} mod p (using bid value directly as exponent)"""
        # Use bid value directly as exponent for more reasonable computation
        # If modulus is provided, use it; otherwise use a large prime for demonstration
        if modulus is None:
            modulus = 2**31 - 1  # Use Mersenne prime for modular arithmetic

        # Safety check: ensure bid value is within safe range for monotonic ordering
        max_safe_bid = 1000  # Adjust based on your auction requirements
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


# --- Child Blockchain (CBC) Verifier ---


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
        # Sort by commitment value (larger is better)
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


# --- Parent Blockchain (PBC) Verifier ---


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
        # Sort by commitment value (larger is better)
        sorted_commitments = sorted(
            self.all_decrypted_commitments, key=lambda x: x[1], reverse=True)
        self.final_winners = sorted_commitments[:M]
        return self.final_winners

    def generate_random_values(self, M):
        """Generate random values for vector commitment"""
        self.random_values = [random.randint(1, 100) for _ in range(M)]
        return self.random_values

    def compute_vector_commitment(self, p):
        """Compute vector commitment C = c1^r1 * c2^r2 * ... * cM^rM mod p"""
        if not self.final_winners or not self.random_values:
            raise ValueError("Final winners or random values not set")

        self.vector_commitment = 1
        for i, (user, commitment) in enumerate(self.final_winners):
            r_i = self.random_values[i]
            self.vector_commitment = (
                self.vector_commitment * pow(commitment, r_i)) % p

        return self.vector_commitment


# --- Commitment Comparison Verification ---


def verify_commitment_ordering(g, modulus, max_bid=1000):
    """
    Verify that g^x mod p maintains monotonic ordering for bid values

    Args:
        g: generator
        modulus: prime modulus
        max_bid: maximum bid value to test

    Returns:
        bool: True if ordering is preserved
    """
    print(
        f"Verifying commitment ordering for g={g}, p={modulus}, max_bid={max_bid}")

    # Test a sample of bid values
    test_bids = [50, 100, 150, 200, 250, 300]
    commitments = []

    for bid in test_bids:
        if bid <= max_bid:
            commitment = pow(g, bid, modulus)
            commitments.append((bid, commitment))
            print(f"  Bid {bid}: commitment = {commitment}")

    # Check if commitments are in ascending order
    is_monotonic = all(commitments[i][1] < commitments[i+1][1]
                       for i in range(len(commitments)-1))

    print(f"  Monotonic ordering preserved: {is_monotonic}")
    return is_monotonic


# --- Main M+1st-price Sealed Bid Auction Protocol ---


def run_auction(N_cbcs=3, users_per_cbc=5, M=2):
    """
    Run the complete M+1st-price sealed bid auction

    Args:
        N_cbcs: Number of Child Blockchains
        users_per_cbc: Number of users per CBC
        M: Number of winners to select
    """
    print("=" * 60)
    print("M+1st-price Sealed Bid Auction from N Child Blockchains")
    print("=" * 60)

    # Setup Phase
    print("\n--- Setup Phase ---")

    # 1. PBC generates g
    g = vc_keygen(1, 100)  # k=1, q=100 for demonstration
    print(f"Generated g: {g}")

    # 2. PBC generates random values (will be used later)
    pbc_verifier = PBCVerifier()
    print(f"PBC public key: {pbc_verifier.pubkey}")

    # 3. Create CBCs and their verifiers
    cbcs = []
    for i in range(N_cbcs):
        cbc_id = f"CBC_{chr(65+i)}"  # CBC_A, CBC_B, CBC_C, ...
        cbc_verifier = CBCVerifier(cbc_id)
        print(f"{cbc_id} public key: {cbc_verifier.pubkey}")
        cbcs.append(cbc_verifier)

    # CBC Round
    print(f"\n--- CBC Round (Processing {N_cbcs} Child Blockchains) ---")

    for cbc_idx, cbc in enumerate(cbcs):
        print(f"\n--- Processing {cbc.cbc_id} ---")

        # Create users for this CBC
        users = []
        for i in range(users_per_cbc):
            user_id = f"{cbc.cbc_id}_User_{i+1}"
            bid_value = random.randint(10, 100)  # Random bid between $10-$100
            user = User(user_id, bid_value)
            users.append(user)
            cbc.register_user(user)

        # Bidding phase
        print("Bidding phase:")
        for user in users:
            # 1. User creates commitment c_i = g^{bin(v_i)}
            commitment = user.create_commitment(g)

            # 2. User encrypts commitment
            encrypted = user.encrypt_commitment(cbc.pubkey)

            print(f"  {user.user_id}: bid={user.bid_value}, "
                  f"bin(bid)={bin(user.bid_value)[2:]}, "
                  f"commitment={commitment}")

        # CBC verifier processes
        print("CBC verifier processing:")

        # 3. Decrypt all commitments
        cbc.decrypt_commitments()

        # 4. Select top M winners
        top_winners = cbc.select_top_M(M)
        print(f"  Top {M} winners in {cbc.cbc_id}:")
        for user, commitment in top_winners:
            print(f"    {user.user_id}: commitment={commitment}")

        # 5. Encrypt winners for PBC
        encrypted_winners = cbc.encrypt_winners_for_pbc(pbc_verifier.pubkey)
        pbc_verifier.collect_encrypted_winners(encrypted_winners)

    # PBC Round
    print(f"\n--- PBC Round ---")

    # 1. Decrypt all commitments from CBCs
    print("Decrypting commitments from all CBCs...")
    pbc_verifier.decrypt_all_commitments()

    print("All candidates:")
    for user, commitment in pbc_verifier.all_decrypted_commitments:
        print(f"  {user.user_id}: commitment={commitment}")

    # 2. Select final top M winners
    final_winners = pbc_verifier.select_final_winners(M)

    print(f"\nFinal Top {M} Winners:")
    for i, (user, commitment) in enumerate(final_winners):
        print(
            f"  {i+1}. {user.user_id}: bid=${user.bid_value}, commitment={commitment}")

    # 3. Generate random values and compute vector commitment
    random_values = pbc_verifier.generate_random_values(M)
    p = pbc_verifier.pubkey[1]  # Use n as substitute for p
    vector_commitment = pbc_verifier.compute_vector_commitment(p)

    print(f"\nVector Commitment:")
    print(f"  Random values: {random_values}")
    print(f"  Vector commitment C: {vector_commitment}")

    # Verification phase
    print(f"\n--- Verification Phase ---")
    print(f"Published auxiliary information: {random_values}")
    print("All users can now verify the vector commitment...")

    return final_winners, vector_commitment


# --- Main Function ---


def main():
    """Main function to run the auction"""
    # Run auction with 3 CBCs, 4 users per CBC, select top 2 winners
    final_winners, vector_commitment = run_auction(
        N_cbcs=3, users_per_cbc=4, M=2)

    print("\n" + "=" * 60)
    print("Auction Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
