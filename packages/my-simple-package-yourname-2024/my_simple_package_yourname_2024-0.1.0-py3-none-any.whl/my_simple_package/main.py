def greet(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def main():
    """Main entry point."""
    print(greet("uv"))
    print(f"2 + 3 = {add_numbers(2, 3)}")

if __name__ == "__main__":
    main()