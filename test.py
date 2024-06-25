import requests
import time

def main():
    a = time.perf_counter()
    for i in range(10000):
        requests.get("http://localhost:5000")
    b = time.perf_counter()

    print(f"took {b - a}s")

main()
