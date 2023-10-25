import numpy as np
import hashlib

def baseline_hash_function(k):
    """
    a simple hash function mapping any number to {-1, 1}
    """
    remainder = k % 2

    if remainder == 0:
        return -1
    else:
        return 1


def advanced_hash_function(k):
    hash_value = hashlib.sha256(str(k).encode()).hexdigest()

    # Take the last digit of the hash and convert it to an integer.
    last_digit = int(hash_value[-1], 16)

    return baseline_hash_function(last_digit)
    

def alon_matias_szegedy_paper(stream):
    """
    The alon matias szegedy algorithm as presented in their paper
    """
    z = 0
    for k in stream:

        z += advanced_hash_function(k)

    return z*z

def alon_matias_szegedy_mmd(stream, passes=1):
    """
    The alon matias szegedy algorithm as presented in the book of mining massive datasets
    """

    n = len(stream)

    positions = np.random.randint(0, len(stream), passes).tolist()
    positions.sort()
    estimates = [0 for _ in range(passes)]
    
    i = positions[0]
    while i < n:
        for j in range(passes):
            if i >= positions[j] and stream[i] == stream[positions[j]]:
                estimates[j] += 1

        i += 1

    for j in range(passes):
        estimates[j] =  n*(2*estimates[j] -1)
    
    print(estimates)
    return int(np.mean(estimates))


def sum_quadratic_frequences(stream):
    """
    a function computing the actual F2 value
    """
    dc = {}
    for n in stream:
        if n not in dc:
            dc[n] = 1
        else:
            dc[n] += 1
    return sum([v*v for v in dc.values()])

def advanced_instance():
    # each ip is going to be linked with an integer
    # first from numbers 0-1000 we assume that on average they do 10 roughly requests
    stream = np.random.randint(0, 1000, size=10000).tolist()

    # then 50 ips create a lot requests
    ddos_traffic = np.random.randint(1000, 1050, size=5000).tolist()

    stream.extend(ddos_traffic)
    return stream

def baseline_instance():
    return [1,2,3,2,4,1,3,4,1,2,4,3,1,1,2]


def determining_threshold():
    return np.mean([sum_quadratic_frequences(advanced_instance()) for _ in range(100)])

if __name__ == "__main__":

    # print(determining_threshold())

    stream = advanced_instance()

    actual = sum_quadratic_frequences(stream)
    print(actual)

    estimate = alon_matias_szegedy_mmd(stream, passes=5)
    print(estimate)

    estimate = alon_matias_szegedy_paper(stream)
    print(estimate)

