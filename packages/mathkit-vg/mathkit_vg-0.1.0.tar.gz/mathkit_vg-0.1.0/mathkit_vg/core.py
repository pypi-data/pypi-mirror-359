import math

def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0

def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def fibonacci_upto(n):
    fib = [0, 1]
    while fib[-1] + fib[-2] <= n:
        fib.append(fib[-1] + fib[-2])
    return fib

def is_fibonacci(n):
    x1 = 5 * n * n + 4
    x2 = 5 * n * n - 4
    return is_perfect_square(x1) or is_perfect_square(x2)

def is_perfect_square(x):
    return int(math.sqrt(x)) ** 2 == x

def reverse_number(n):
    return int(str(abs(n))[::-1]) * (1 if n >= 0 else -1)

def digital_root(n):
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return abs(a * b) // gcd(a, b)

def is_strong_number(n):
    return n == sum(math.factorial(int(d)) for d in str(n))

def is_automorphic(n):
    return str(n * n).endswith(str(n))

def prime_factors(n):
    factors = []
    for i in range(2, int(math.sqrt(n)) + 1):
        while n % i == 0:
            factors.append(i)
            n //= i
    if n > 1:
        factors.append(n)
    return factors

def next_prime(n):
    def is_prime(k):
        if k <= 1:
            return False
        for i in range(2, int(k ** 0.5) + 1):
            if k % i == 0:
                return False
        return True

    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate

def is_abundant_number(n):
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) > n

def count_zeros(n):
    return str(abs(n)).count('0')
