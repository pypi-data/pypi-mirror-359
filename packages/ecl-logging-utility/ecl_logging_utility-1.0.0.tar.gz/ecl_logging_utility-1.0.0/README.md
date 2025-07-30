# Structured Logging Utilities for ECL microservices

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-lightgrey)

Internal package for consistent structured logging across ECL microservices. Features JSON formatting, automatic metadata capture, and environment-based configuration.

## Features

- 📝 **Structured JSON logs** with consistent schema
- 🕒 **Automatic timestamping** in ISO 8601 format
- 📍 **Complete source location** (file path, line number, module, function)
- 🔍 **Query-ready fields** (transaction_id, request_ip, service_name)
- ⚙️ **Environment-controlled** log levels
- 🔗 **Request context propagation** across services
- 🛡 **Private package** for internal use only

## Installation

```bash
pip install ecl-logging-utility
```

## Version History  
See [CHANGELOG.md](CHANGELOG.md) for release notes.  