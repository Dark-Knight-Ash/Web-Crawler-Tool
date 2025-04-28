# main.py
import json
from crawler import get_all_links

def main():
    url = input("Enter the starting URL (e.g. https://example.com): ").strip()
    result = get_all_links(url)

    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

    print(f"\n✅ Crawling complete. Results saved in 'output.json'.")

if __name__ == "__main__":
    main()
