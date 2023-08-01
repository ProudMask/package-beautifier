import requests
import random

def check_package_existence(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    return response.status_code == 200

def generate_funny_name(package_name):
    funny_suffixes = ["py", "inator", "inator3000", "tron", "ware", "ify", "oodles", "licious"]
    return package_name + random.choice(funny_suffixes)

def main():
    while True:
        package_name = input("Enter the package name (or type 'exit' to quit): ").strip()
        
        if package_name.lower() == "exit":
            break

        if check_package_existence(package_name):
            print(f"The package '{package_name}' already exists.")
            choice = input("Would you like to generate a funny name instead? (yes/no): ").strip().lower()
            if choice == "yes":
                funny_name = generate_funny_name(package_name)
                print(f"How about '{funny_name}'?")
        else:
            print(f"The package name '{package_name}' is available! You can use it for your package.")

if __name__ == "__main__":
    main()
