import sys

def greet(name="World"):
    """Greets the given name, or 'World' if no name is provided."""
    print(f"Hello, {name}!")

if __name__ == "__main__":
    # Get the name from command-line arguments, if provided
    if len(sys.argv) > 1:
        greet(sys.argv[1])
    else:
        greet()
