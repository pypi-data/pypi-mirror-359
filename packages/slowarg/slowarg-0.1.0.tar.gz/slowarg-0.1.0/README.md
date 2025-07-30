# SlowArg

A deliberately slow CLI tool that demonstrates the performance impact of heavy imports on argparse tab completion.

## Purpose

This package is designed to simulate a real-world CLI application with heavy dependencies that slow down tab completion. It's useful for:

- Testing tab completion performance
- Demonstrating the benefits of fast completion libraries
- Benchmarking completion speed improvements
- Educational purposes for understanding CLI performance issues

## Installation

```bash
pip install slowarg
```

## Usage

After installation, you can use the `slowarg` command:

```bash
# Basic usage
slowarg --help

# Run foo command
slowarg foo --bar 42 --baz a

# Run data command
slowarg data --file input.csv --mode fast

# With tab completion (slow due to heavy imports)
slowarg <TAB>
```

## Features

- Multiple subcommands with various argument types
- Heavy dependencies (matplotlib, numpy, pandas, scikit-learn, requests, click)
- Deliberately slow import times (5-second delay) to demonstrate completion performance issues
- Full argparse integration with argcomplete
- Simple and clean command structure

## Commands

### `foo` command
- `--bar`: Integer value
- `--baz`: Choice between "a", "b", or "c"

### `data` command
- `--file`: Input file path
- `--mode`: Choice between "fast" or "slow"

## Performance Impact

This tool intentionally includes heavy imports and a 5-second delay to simulate real-world scenarios where CLI tools have slow startup times due to:

- Large dependency trees
- Complex initialization processes
- Heavy computational libraries
- Network or database connections

## Development

To install in development mode:

```bash
git clone https://github.com/udayayya/slowarg
cd slowarg
pip install -e '.[dev]'
```

## Testing

```bash
# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
