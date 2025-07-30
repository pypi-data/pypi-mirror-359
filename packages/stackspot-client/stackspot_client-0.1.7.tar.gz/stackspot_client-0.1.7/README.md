# StackSpot Client Python

A Python client library for interacting with the StackSpot API. This library provides a simple and intuitive interface to authenticate, execute commands, and retrieve results from the StackSpot platform.

## Features

- 🔐 Automatic authentication handling
- 🔄 Automatic token refresh
- ⚡ Retry mechanism for failed requests
- 🛡️ Comprehensive error handling
- 📦 Support for different response types
- 🧪 Type hints for better IDE support

## Installation

You can install the package using pip:

```bash
pip install stackspot-client
```

## Quick Start

```python
import os

from dotenv import load_dotenv
from stackspot_client import StackSpotConfig, StackSpotError, QuickCommands

load_dotenv()

def main():
    # Configuração do cliente
    config = StackSpotConfig(base_url=os.getenv("base_url"),auth_url=os.getenv("auth_url"),
        client_id=os.getenv("client_id"),client_secret=os.getenv("client_secret")
    )

    try:

        command = QuickCommands(config)

        execution_id = command.execute_command(
            
         # Endpoint informed when creating the quick command
        '/v1/quick-commands/create-execution/ola-mundo-',
            ' O mundo é um moinho'
        )

        result = command.get_execution_result(execution_id)

        if result:
            print("\n📋 Resultado:")
            print("=" * 50)
            print(result['steps'][0]['step_result']['answer'])
        else:
            print("❌ Falha")

    except StackSpotError as e:
        print(f"\n❌ Erro: {str(e)}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        print("\nDetalhes do erro:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
```

## Configuration

The `StackSpotConfig` class accepts the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| base_url | str | Yes | - | Base URL for the StackSpot API |
| client_id | str | Yes | - | Your StackSpot client ID |
| client_secret | str | Yes | - | Your StackSpot client secret |
| auth_url | str | No | https://idm.stackspot.com/stackspot-freemium/oidc/oauth/token | Authentication URL |
| max_retries | int | No | 30 | Maximum number of retries for result polling |
| retry_interval | int | No | 5 | Interval between retries in seconds |
| request_delay | float | No | 0.0 | Delay in seconds before each request |
| proxies | dict | No | None | Proxy configuration for HTTP/HTTPS requests |

### Environment Variables & .env support

You can configure the client using environment variables for improved security and flexibility. The following variables are supported:

- `STACKSPOT_BASE_URL` (required)
- `STACKSPOT_CLIENT_ID` (required)
- `STACKSPOT_CLIENT_SECRET` (required)
- `STACKSPOT_AUTH_URL` (optional)
- `STACKSPOT_MAX_RETRIES` (optional)
- `STACKSPOT_RETRY_INTERVAL` (optional)
- `STACKSPOT_REQUEST_DELAY` (optional)
- `STACKSPOT_PROXY_HTTP` (optional)
- `STACKSPOT_PROXY_HTTPS` (optional)

You may use a `.env` file in your project root for local development:

```env
STACKSPOT_BASE_URL=https://genai-code-buddy-api.stackspot.com
STACKSPOT_CLIENT_ID=your_client_id
STACKSPOT_CLIENT_SECRET=your_client_secret
STACKSPOT_AUTH_URL=https://idm.stackspot.com/stackspot-freemium/oidc/oauth/token
STACKSPOT_MAX_RETRIES=30
STACKSPOT_RETRY_INTERVAL=5
STACKSPOT_REQUEST_DELAY=0.0
STACKSPOT_PROXY_HTTP=http://proxy.example.com:8080
STACKSPOT_PROXY_HTTPS=https://proxy.example.com:8080
```

#### Example: Loading from environment

```python
from stackspot_client import StackSpotConfig, StackSpotClient

# Optionally load .env file (requires python-dotenv)
from dotenv import load_dotenv
load_dotenv()

config = StackSpotConfig.from_env()
client = StackSpotClient(config)
```

#### Example: Using proxies

```python
from stackspot_client import StackSpotConfig, StackSpotClient

# Configure proxies directly
config = StackSpotConfig(
    base_url="https://genai-code-buddy-api.stackspot.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    proxies={
        'http': 'http://proxy.example.com:8080',
        'https': 'https://proxy.example.com:8080'
    }
)

# Or configure via environment variables
# STACKSPOT_PROXY_HTTP=http://proxy.example.com:8080
# STACKSPOT_PROXY_HTTPS=https://proxy.example.com:8080
config = StackSpotConfig.from_env()

client = StackSpotClient(config)
```

| client_id | str | Yes | - | Your StackSpot client ID |
| client_secret | str | Yes | - | Your StackSpot client secret |
| auth_url | str | No | https://idm.stackspot.com/stackspot-freemium/oidc/oauth/token | Authentication URL |
| max_retries | int | No | 30 | Maximum number of retries for result polling |
| retry_interval | int | No | 5 | Interval between retries in seconds |

## Usage Examples

## Knowledge Source Upload Examples

Below are usage examples for the upload methods available in the `KnowledgeSources` class:

```python
from stackspot_client import StackSpotConfig, StackSpotClient
from stackspot_client.knowledge_sources import KnowledgeSources

# It is recommended to configure your credentials using environment variables or a .env file:
# STACKSPOT_BASE_URL, STACKSPOT_CLIENT_ID, STACKSPOT_CLIENT_SECRET, STACKSPOT_AUTH_URL (optional)
config = StackSpotConfig.from_env()

# If needed, you can override any parameter manually:
# config.base_url = 'https://another-endpoint.com'

client = StackSpotClient(config)
ks = KnowledgeSources(client)
ks_slug = 'my-ks'
file_path = '/path/to/file.pdf'

# 1. Direct file upload (without Docling processing)
ks.upload_file(file_path, ks_slug)

> **Note:** Supported files for direct upload: `.json`, `.yml`, `.yaml`, `.md`, `.txt`, `.pdf`, `.zip` (the `.zip` file must contain only the supported file types listed). Maximum size: **10MB per file**. Other formats must be processed with Docling.

# 2. Upload content extracted from a URL (processed by Docling to Markdown)
ks.upload_from_url('https://example.com/article', ks_slug)

# 3. Upload a local file processed by Docling (generates Markdown before upload)
ks.upload_file_with_docling(file_path, ks_slug)

> **Note:** When using Docling (with `upload_from_url` or `upload_file_with_docling`), a wide range of file formats is supported. For the complete list, see the [Docling Supported Formats documentation](https://docling-project.github.io/docling/usage/supported_formats/).

# Delete all files from a knowledge source
success = ks.delete_all_files("my-knowledge-source")
```

## Response Format

The `get_execution_result` method returns a dictionary with the following structure:

```python
{
    'status': 'COMPLETED',  # or 'FAILED', 'RUNNING'
    'answer': '...',       # The actual response
    'progress': {          # Optional progress information
        'status': 'COMPLETE',
        'percentage': 100
    }
}
```

## Error Types

The library provides several error types for better error handling:

- `StackSpotError`: Base exception class
- `AuthenticationError`: Raised when authentication fails
- `APIError`: Raised when API calls fail

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support with the StackSpot API, please refer to the [official documentation](https://docs.stackspot.com).

## Changelog

### 0.1.7
- Added proxy support for HTTP/HTTPS requests
- New `proxies` parameter in `StackSpotConfig` for direct proxy configuration
- Environment variables support: `STACKSPOT_PROXY_HTTP` and `STACKSPOT_PROXY_HTTPS`
- Proxy configuration applies to both authentication and API requests
- Updated documentation with proxy usage examples

### 0.1.4
- Environment-based configuration as default (with `.env` support)
- File upload validation: allowed formats and max size (10MB)
- Integration with Docling for file and URL uploads (Markdown conversion)
- Added `ValidationError` for input validation
- Maintainer metadata (`eltonjosesouza`) in setup.py
- General code and documentation cleanup

### 0.1.2
- Added support for Knowledge Sources management
- Implemented knowledge source creation functionality
- Added support for file uploads
- Implemented URL content upload functionality
- Added functionality to delete all files from a knowledge source

### 0.1.0
- Initial release
- Basic authentication and command execution
- Result polling with retry mechanism
- Comprehensive error handling