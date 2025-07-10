import time
import random
from auction import User, CBCVerifier, PBCVerifier, vc_keygen
from test import Bidder, ChildBlockchain, ParentBlockchain


def measure_auction_py_performance():
    """Measure performance of each process in auction.py"""
    start = time.perf_counter()

    # Key generation
    key_start = time.perf_counter()
    cbc_verifier = CBCVerifier("CBC1")
    key_time = time.perf_counter() - key_start

    # User creation and commitment
    commit_start = time.perf_counter()
    users = []
    for i in range(10):
        user = User(f"User{i}", random.randint(50, 300))
        user.create_commitment(2)  # g=2
        user.encrypt_commitment(cbc_verifier.pubkey)
        users.append(user)
        cbc_verifier.register_user(user)
    commit_time = time.perf_counter() - commit_start

    # Selection process
    select_start = time.perf_counter()
    cbc_verifier.select_top_M_bidders(2)
    select_time = time.perf_counter() - select_start

    total_time = time.perf_counter() - start

    return {
        'total': total_time,
        'key_gen': key_time,
        'commitment': commit_time,
        'selection': select_time
    }


def measure_test_py_performance():
    """Measure performance of each process in test.py"""
    start = time.perf_counter()

    # Bidder creation
    bidder_start = time.perf_counter()
    bidders = []
    for i in range(10):
        bidder = Bidder(f"Bidder{i}", random.randint(50, 300))
        bidders.append(bidder)
    bidder_time = time.perf_counter() - bidder_start

    # Blockchain operations
    blockchain_start = time.perf_counter()
    cbc = ChildBlockchain("CBC1", bidders, 2)
    cbc.decrypt_commitments()
    winners = cbc.select_top_M()
    blockchain_time = time.perf_counter() - blockchain_start

    total_time = time.perf_counter() - start

    return {
        'total': total_time,
        'bidder_creation': bidder_time,
        'blockchain_ops': blockchain_time
    }


def detailed_operation_analysis():
    """Detailed performance analysis of specific operations"""
    print("=== Detailed Operation Performance Analysis ===")

    # Numerical computation vs string operations
    print("\n1. Numerical computation vs string operations:")

    # auction.py style computation
    start = time.perf_counter()
    for _ in range(1000):
        result = pow(2, 100, 2**31-1)
    math_time = time.perf_counter() - start

    # test.py style string operations
    start = time.perf_counter()
    for _ in range(1000):
        commit = f"COMMIT_{100}"
        encrypted = f"ENC_{commit}"
    string_time = time.perf_counter() - start

    print(f"  Numerical computation (1000 times): {math_time:.6f} seconds")
    print(f"  String operations (1000 times): {string_time:.6f} seconds")
    print(
        f"  Ratio: String operations are {string_time/math_time:.2f} times slower than numerical computation")

    # Comparison of sorting operations
    print("\n2. Sorting operations:")

    # Integer sorting
    int_list = [random.randint(1, 1000) for _ in range(100)]
    start = time.perf_counter()
    sorted(int_list, reverse=True)
    int_sort_time = time.perf_counter() - start

    # Object sorting (using lambda)
    class TestObj:
        def __init__(self, val):
            self.val = val

    obj_list = [TestObj(random.randint(1, 1000)) for _ in range(100)]
    start = time.perf_counter()
    sorted(obj_list, key=lambda x: x.val, reverse=True)
    obj_sort_time = time.perf_counter() - start

    print(f"  Integer sorting: {int_sort_time:.6f} seconds")
    print(f"  Object sorting: {obj_sort_time:.6f} seconds")
    print(
        f"  Ratio: Object sorting is {obj_sort_time/int_sort_time:.2f} times slower than integer sorting")


if __name__ == "__main__":
    print("=== auction.py vs test.py Performance Analysis ===")

    # Run multiple times and take average
    auction_times = []
    test_times = []

    for _ in range(100):
        auction_result = measure_auction_py_performance()
        test_result = measure_test_py_performance()
        auction_times.append(auction_result['total'])
        test_times.append(test_result['total'])

    avg_auction = sum(auction_times) / len(auction_times)
    avg_test = sum(test_times) / len(test_times)

    print(f"\nAverage execution time (100 measurements):")
    print(f"auction.py: {avg_auction:.6f} seconds")
    print(f"test.py: {avg_test:.6f} seconds")
    print(
        f"Ratio: test.py is {avg_test/avg_auction:.2f} times slower than auction.py")

    # Detailed analysis
    detailed_operation_analysis()

    # Single detailed measurement
    print(f"\n=== Detailed Breakdown (Single Measurement) ===")
    auction_detail = measure_auction_py_performance()
    test_detail = measure_test_py_performance()

    print(f"\nauction.py details:")
    for key, value in auction_detail.items():
        print(f"  {key}: {value:.6f} seconds")

    print(f"\ntest.py details:")
    for key, value in test_detail.items():
        print(f"  {key}: {value:.6f} seconds")


def measure_auction_py_performance():
    """Measure performance of each process in auction.py"""
    start = time.perf_counter()

    # Key generation
    key_start = time.perf_counter()
    cbc_verifier = CBCVerifier("CBC1")
    key_time = time.perf_counter() - key_start

    # User creation and commitment
    commit_start = time.perf_counter()
    users = []
    for i in range(10):
        user = User(f"User{i}", random.randint(50, 300))
        user.create_commitment(2)  # g=2
        user.encrypt_commitment(cbc_verifier.pubkey)
        users.append(user)
        cbc_verifier.register_user(user)
    commit_time = time.perf_counter() - commit_start

    # Selection process
    select_start = time.perf_counter()
    cbc_verifier.select_top_M_bidders(2)
    select_time = time.perf_counter() - select_start

    total_time = time.perf_counter() - start

    return {
        'total': total_time,
        'key_gen': key_time,
        'commitment': commit_time,
        'selection': select_time
    }


def measure_test_py_performance():
    """Measure performance of each process in test.py"""
    start = time.perf_counter()

    # Bidder creation
    bidder_start = time.perf_counter()
    bidders = []
    for i in range(10):
        bidder = Bidder(f"Bidder{i}", random.randint(50, 300))
        bidders.append(bidder)
    bidder_time = time.perf_counter() - bidder_start

    # Blockchain operations
    blockchain_start = time.perf_counter()
    cbc = ChildBlockchain("CBC1", bidders, 2)
    cbc.decrypt_commitments()
    winners = cbc.select_top_M()
    blockchain_time = time.perf_counter() - blockchain_start

    total_time = time.perf_counter() - start

    return {
        'total': total_time,
        'bidder_creation': bidder_time,
        'blockchain_ops': blockchain_time
    }


def detailed_operation_analysis():
    """Detailed performance analysis of specific operations"""
    print("=== Detailed Operation Performance Analysis ===")

    # Numerical computation vs string operations
    print("\n1. Numerical computation vs string operations:")

    # auction.py style computation
    start = time.perf_counter()
    for _ in range(1000):
        result = pow(2, 100, 2**31-1)
    math_time = time.perf_counter() - start

    # test.py style string operations
    start = time.perf_counter()
    for _ in range(1000):
        commit = f"COMMIT_{100}"
        encrypted = f"ENC_{commit}"
    string_time = time.perf_counter() - start

    print(f"  Numerical computation (1000 times): {math_time:.6f} seconds")
    print(f"  String operations (1000 times): {string_time:.6f} seconds")
    print(
        f"  Ratio: String operations are {string_time/math_time:.2f} times slower than numerical computation")

    # Comparison of sorting operations
    print("\n2. Sorting operations:")

    # Integer sorting
    int_list = [random.randint(1, 1000) for _ in range(100)]
    start = time.perf_counter()
    sorted(int_list, reverse=True)
    int_sort_time = time.perf_counter() - start

    # Object sorting (using lambda)
    class TestObj:
        def __init__(self, val):
            self.val = val

    obj_list = [TestObj(random.randint(1, 1000)) for _ in range(100)]
    start = time.perf_counter()
    sorted(obj_list, key=lambda x: x.val, reverse=True)
    obj_sort_time = time.perf_counter() - start

    print(f"  Integer sorting: {int_sort_time:.6f} seconds")
    print(f"  Object sorting: {obj_sort_time:.6f} seconds")
    print(
        f"  Ratio: Object sorting is {obj_sort_time/int_sort_time:.2f} times slower than integer sorting")


if __name__ == "__main__":
    print("=== auction.py vs test.py Performance Analysis ===")

    # Run multiple times and take average
    auction_times = []
    test_times = []

    for _ in range(100):
        auction_result = measure_auction_py_performance()
        test_result = measure_test_py_performance()
        auction_times.append(auction_result['total'])
        test_times.append(test_result['total'])

    avg_auction = sum(auction_times) / len(auction_times)
    avg_test = sum(test_times) / len(test_times)

    print(f"\nAverage execution time (100 measurements):")
    print(f"auction.py: {avg_auction:.6f} seconds")
    print(f"test.py: {avg_test:.6f} seconds")
    print(
        f"Ratio: test.py is {avg_test/avg_auction:.2f} times slower than auction.py")

    # Detailed analysis
    detailed_operation_analysis()

    # Single detailed measurement
    print(f"\n=== Detailed Breakdown (Single Measurement) ===")
    auction_detail = measure_auction_py_performance()
    test_detail = measure_test_py_performance()

    print(f"\nauction.py details:")
    for key, value in auction_detail.items():
        print(f"  {key}: {value:.6f} seconds")

    print(f"\ntest.py details:")
    for key, value in test_detail.items():
        print(f"  {key}: {value:.6f} seconds")
