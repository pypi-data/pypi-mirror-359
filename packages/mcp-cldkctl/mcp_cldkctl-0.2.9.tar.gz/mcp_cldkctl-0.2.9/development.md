# Development Guide for mcp-cldkctl

## Setting Up for Development

1. Clone the repository:
   ```sh
   git clone https://github.com/cloudeka/mcp-cldkctl.git
   cd mcp-cldkctl
   ```
2. Install dependencies:
   ```sh
   pip install -e .[dev]
   ```
3. Run tests:
   ```sh
   pytest
   ```

## Code Style
- Follows Black and isort formatting.
- Type checking with mypy.

## Building and Publishing
- Build: `python build_and_publish.py`
- Publish: Follow instructions in DEPLOYMENT.md

## Debugging
- Use `debug_auth.py` and `debug_production_vs_staging.py` for troubleshooting.

## Contributing
- Please open issues or pull requests for any changes or suggestions. 