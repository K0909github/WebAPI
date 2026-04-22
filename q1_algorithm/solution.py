import sys


def main() -> None:
    input = sys.stdin.readline
    n, k = map(int, input().split())
    a = list(map(int, input().split()))

    left = 0
    s = 0
    best = 0

    for right in range(n):
        s += a[right]
        while s > k and left <= right:
            s -= a[left]
            left += 1
        best = max(best, right - left + 1)

    print(best)


if __name__ == "__main__":
    main()
