# How To Use mcp-cldkctl

## Installation

```sh
pip install mcp-cldkctl
# or
uvx mcp-cldkctl
```

## Authentication

Set your token and base URL:
```sh
export CLDKCTL_TOKEN="your_token_here"
export CLDKCTL_BASE_URL="https://ai.cloudeka.id"
```

## Basic Usage

List projects:
```sh
mcp-cldkctl project list
```

Check balance:
```sh
mcp-cldkctl balance detail --project-id <your_project_id>
```

Switch environment:
```sh
mcp-cldkctl switch-environment --env staging
```

## More Information
- See the README.md for full documentation.
- For development, see development.md. 