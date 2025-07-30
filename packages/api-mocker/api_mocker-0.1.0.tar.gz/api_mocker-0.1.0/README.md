# api-mocker

The industry-standard, production-ready, free API mocking and development acceleration tool.

## Project Mission
Create the most comprehensive, user-friendly, and feature-rich API mocking solution to eliminate API dependency bottlenecks and accelerate development workflows for all developers.

## Features
- Robust HTTP mock server supporting all HTTP methods
- Dynamic and static response generation
- OpenAPI/Swagger/Postman import/export
- CLI and Python API interfaces
- Hot-reloading, config file support (JSON/YAML/TOML)
- Request recording, replay, and proxy mode
- Schema-based data generation and validation
- Advanced routing, middleware, and authentication simulation
- Data persistence, state management, and in-memory DB
- Performance, monitoring, and analytics tools
- Framework integrations (Django, Flask, FastAPI, Node.js, etc.)
- Docker, CI/CD, and cloud deployment support
- Team collaboration and plugin architecture

## Installation
```bash
pip install api-mocker
```

## Quick Start
```bash
api-mocker start --config api-mock.yaml
```
Or use as a Python library:
```python
from api_mocker import MockServer
server = MockServer(config_path="api-mock.yaml")
server.start()
```

## Documentation
See [Full Documentation](https://github.com/Sherin-SEF-AI/api-mocker#documentation) for guides, API reference, and examples.

## Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT License

---
© 2024 sherin joseph roy 