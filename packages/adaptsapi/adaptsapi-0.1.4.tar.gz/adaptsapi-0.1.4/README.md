# AdaptsAPI CLI

A command-line interface for triggering documentation generation via the Adapts API Gateway → SNS.

[![PyPI version](https://badge.fury.io/py/adaptsapi.svg)](https://badge.fury.io/py/adaptsapi)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## Features

- 🚀 **Simple CLI** for triggering Adapts API endpoints
- 🔑 **Secure token management** with environment variables or local config
- 📄 **Flexible payload support** via JSON files or inline data
- 🔧 **Configurable endpoints** with default endpoint support
- ✅ **Built-in payload validation** for documentation generation requests
- 🤖 **GitHub Actions integration** for automated wiki documentation

## Installation

### From PyPI

```bash
pip install adaptsapi
```

### From Source

```bash
git clone https://github.com/adaptsai/adaptsapi.git
cd adaptsapi
pip install -e .
```

## Quick Start

### 1. Set up your API token

You can provide your API token in three ways (in order of precedence):

1. **Environment variable** (recommended for CI/CD):
   ```bash
   export ADAPTS_API_TOKEN="your-api-token-here"
   ```

2. **Local config file** (`config.json` in current directory):
   ```json
   {
     "token": "your-api-token-here",
     "endpoint": "https://your-api-endpoint.com/prod/generate_wiki_docs"
   }
   ```

3. **Interactive prompt** (first-time setup):
   ```bash
   adaptsapi --data '{"test": "payload"}'
   # CLI will prompt for token and save to config.json
   ```

### 2. Make your first API call

**Using inline JSON data:**
```bash
adaptsapi \
  --endpoint "https://api.adapts.ai/prod/generate_wiki_docs" \
  --data '{"email_address": "user@example.com", "user_name": "john_doe", "repo_object": {...}}'
```

**Using a JSON payload file:**
```bash
adaptsapi \
  --endpoint "https://api.adapts.ai/prod/generate_wiki_docs" \
  --payload-file payload.json
```

## Usage

### Command Line Options

```bash
adaptsapi [OPTIONS]
```

| Option | Description | Required |
|--------|-------------|----------|
| `--endpoint URL` | Full URL of the API endpoint | Yes (unless set in config.json) |
| `--data JSON` | Inline JSON payload string | Yes (or --payload-file) |
| `--payload-file FILE` | Path to JSON payload file | Yes (or --data) |
| `--timeout SECONDS` | Request timeout in seconds (default: 30) | No |

### Payload Structure

For documentation generation, your payload should follow this structure:

```json
{
  "email_address": "user@example.com",
  "user_name": "github_username",
  "repo_object": {
    "repository_name": "my-repo",
    "source": "github",
    "repository_url": "https://github.com/user/my-repo",
    "branch": "main",
    "size": "12345",
    "language": "python",
    "is_private": false,
    "git_provider_type": "github",
    "refresh_token": "github_token_here"
  }
}
```

#### Required Fields

- `email_address`: Valid email address
- `user_name`: Username string
- `repo_object.repository_name`: Repository name
- `repo_object.repository_url`: Full repository URL
- `repo_object.branch`: Branch name
- `repo_object.size`: Repository size as string
- `repo_object.language`: Primary programming language
- `repo_object.source`: Source platform (e.g., "github")

#### Optional Fields

- `repo_object.is_private`: Boolean indicating if repo is private
- `repo_object.git_provider_type`: Git provider type
- `repo_object.installation_id`: Installation ID (for GitHub Apps)
- `repo_object.refresh_token`: Refresh token for authentication

## GitHub Actions Integration

This package is designed to work seamlessly with GitHub Actions for automated documentation generation. Here's an example workflow:

```yaml
name: Generate Wiki Docs

on:
  pull_request:
    branches: [ main ]
    types: [ closed ]

jobs:
  call-adapts-api:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          
      - name: Install adaptsapi
        run: pip install adaptsapi
        
      - name: Generate documentation
        env:
          ADAPTS_API_KEY: ${{ secrets.ADAPTS_API_KEY }}
        run: |
          python -c "
          import os
          from adaptsapi.generate_docs import post
          
          payload = {
              'email_address': '${{ github.actor }}@users.noreply.github.com',
              'user_name': '${{ github.actor }}',
              'repo_object': {
                  'repository_name': '${{ github.event.repository.name }}',
                  'source': 'github',
                  'repository_url': '${{ github.event.repository.html_url }}',
                  'branch': 'main',
                  'size': '0',
                  'language': 'python',
                  'is_private': False,
                  'git_provider_type': 'github',
                  'refresh_token': '${{ secrets.GITHUB_TOKEN }}'
              }
          }
          
          resp = post(
              'https://your-api-endpoint.com/prod/generate_wiki_docs',
              os.environ['ADAPTS_API_KEY'],
              payload
          )
          resp.raise_for_status()
          print('✅ Documentation generated successfully')
          "
```

### Setting up GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add `ADAPTS_API_KEY` with your API token value

## Configuration

### Config File Format

The `config.json` file in your current working directory can contain:

```json
{
  "token": "your-api-token-here",
  "endpoint": "https://your-default-endpoint.com/prod/generate_wiki_docs"
}
```

### Environment Variables

- `ADAPTS_API_TOKEN`: Your API authentication token

## Error Handling

The CLI provides clear error messages for common issues:

- **Missing token**: Prompts for interactive token input
- **Invalid JSON**: Shows JSON parsing errors
- **API errors**: Displays HTTP status codes and error messages
- **Payload validation**: Shows specific validation failures

## Development

### Prerequisites

- Python 3.10+
- pip

### Setup Development Environment

```bash
git clone https://github.com/adaptsai/adaptsapi.git
cd adaptsapi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

## API Reference

### Functions

#### `post(endpoint, auth_token, payload, timeout=30)`

Make a POST request to the Adapts API.

**Parameters:**
- `endpoint` (str): The API endpoint URL
- `auth_token` (str): Authentication token
- `payload` (dict): JSON payload to send
- `timeout` (int): Request timeout in seconds

**Returns:**
- `requests.Response`: The HTTP response object

**Raises:**
- `PayloadValidationError`: If payload validation fails
- `requests.RequestException`: If the HTTP request fails

## License

This software is licensed under the Adapts API Use-Only License v1.0. See [LICENSE](LICENSE) for details.

**Key restrictions:**
- ✅ Use the software as-is
- ❌ No modifications allowed
- ❌ No redistribution allowed
- ❌ Commercial use restrictions apply

## Support

- 📧 Email: dev@adapts.ai
- 🐛 Issues: [GitHub Issues](https://github.com/adaptsai/adaptsapi/issues)
- 📖 Documentation: This README

## Changelog

### v0.1.4 (Latest)
- Current release

### v0.1.3
- Patch updates

### v0.1.2
- Initial stable release

---

© 2025 AdaptsAI All rights reserved.