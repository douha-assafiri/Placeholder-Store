"""
Sends steady traffic to the API to show autoscaling and response times.
python infra/tests/load.py https://store.placeholder-store.site/api/places --minutes 10 --workers 50
"""
import argparse
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def hammer(url, stop_at):
    times, errors = [], 0
    while time.monotonic() < stop_at:
        start = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                response.read()
            times.append(time.monotonic() - start)
        except Exception:
            errors += 1
    return times, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--minutes", type=float, default=10)
    parser.add_argument("--workers", type=int, default=50)
    args = parser.parse_args()

    stop_at = time.monotonic() + args.minutes * 60
    print(f"Sending requests to {args.url} for {args.minutes} minutes with {args.workers} workers")
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda _: hammer(args.url, stop_at), range(args.workers)))

    times = sorted(t for worker_times, _ in results for t in worker_times)
    errors = sum(e for _, e in results)
    if not times:
        print(f"No successful requests, {errors} errors")
        return
    p95 = times[int(len(times) * 0.95) - 1]
    print(f"Requests: {len(times)}, errors: {errors}")
    print(f"Per second: {len(times) / (args.minutes * 60):.1f}")
    print(f"p95 response time: {p95 * 1000:.0f} ms")


if __name__ == "__main__":
    main()
