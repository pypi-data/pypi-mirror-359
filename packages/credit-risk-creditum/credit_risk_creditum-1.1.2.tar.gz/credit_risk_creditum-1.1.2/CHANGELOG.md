# Changelog

All notable changes to the credit-risk-creditum package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2025-01-01

### Fixed
- **Decision Response**: Fixed missing `risk_category` and `max_loan_amount` fields in rejected applications
- **NumPy Compatibility**: Added NumPy version constraint (<2.0.0) to prevent compatibility issues
- **API Consistency**: Ensured all decision responses have consistent field structure

### Enhanced
- **Error Handling**: Better handling of validation failures with complete response structure

## [1.1.1] - 2025-01-01

### Fixed
- **Package URLs**: Updated PyPI package URLs to point to working GitHub repository instead of non-accessible website
- **Documentation Links**: Fixed broken documentation links in package metadata

### Changed
- **Homepage URL**: Now points to GitHub repository for better accessibility
- **Documentation URL**: Now points to GitHub README documentation section

## [1.1.0] - 2025-01-01

### Added
- **Command-Line Interface**: Full-featured CLI with `credit-risk` command
  - `assess` command for individual and corporate credit assessment
  - `stress-test` command for comprehensive stress testing
  - `scenarios` command to list available stress scenarios
  - Support for JSON input files and multiple output formats
- **Comprehensive Test Suite**: 80%+ code coverage with pytest
  - Unit tests for all core components
  - Integration tests for complete workflows
  - Mock fixtures for reliable testing
- **Advanced Configuration Management**: Flexible configuration system
  - Environment variable support
  - JSON configuration files
  - Runtime configuration updates
  - Configuration validation
- **Professional Logging**: Structured logging with multiple levels
  - Configurable log levels and formats
  - File and console output options
  - JSON logging support for production
- **Custom Exception Classes**: Specific exceptions for better error handling
- **Type Annotations**: Full type hint support for better IDE experience
- **Development Tools**: Pre-commit hooks, code formatting, and quality checks
- **Documentation**: Comprehensive examples and CLI usage guides

### Enhanced
- **Risk Assessment Models**: Improved accuracy and feature transformation
  - Better handling of edge cases (zero income, extreme values)
  - More sophisticated risk factor calculations
  - Industry-specific risk adjustments for corporate assessments
- **Economic Indicators**: Enhanced economic risk factor calculations
  - Better risk transformation algorithms
  - More accurate industry growth impact
  - Improved stress scenario definitions
- **Stress Testing**: More robust stress testing framework
  - Better scenario restoration
  - Improved summary statistics
  - More detailed stress test results

### Changed
- **Package Structure**: Modernized package layout with src/ structure
- **Dependencies**: Updated to latest stable versions
  - scikit-learn >= 1.0.0
  - pandas >= 1.3.0
  - numpy >= 1.21.0
- **Configuration**: Moved from setup.py to pyproject.toml for modern packaging
- **Repository URLs**: Updated all links to point to public repository

### Fixed
- **Risk Score Calculation**: Fixed issue where risk scores were always returning 0.0
- **Feature Transformation**: Improved application data to risk factor mapping
- **Economic Factor Integration**: Better integration of economic conditions into risk scores

### Security
- **Input Validation**: Enhanced validation for all input data
- **Error Handling**: Improved error messages without exposing sensitive information
- **Dependencies**: Updated all dependencies to address security vulnerabilities

## [0.1.1] - 2024-12-15

### Added
- Basic credit risk assessment for individuals and corporations
- Simple economic indicators integration
- Initial stress testing capabilities

### Fixed
- Minor bug fixes in risk calculation
- Improved error handling

## [0.1.0] - 2024-11-01

### Added
- Initial release
- Basic credit scoring functionality
- Simple economic data integration
- Core risk assessment models

---

## Planned for Future Releases

### [1.2.0] - Planned Q1 2025
- REST API integration capabilities
- Real-time economic data fetching
- Enhanced machine learning models
- Performance optimizations
- Docker containerization support

### [1.3.0] - Planned Q2 2025
- Advanced analytics and reporting
- Custom model training capabilities
- Regulatory compliance features
- Multi-language support
- Enhanced visualization tools

### [2.0.0] - Planned Q3 2025
- Breaking changes for improved API design
- Advanced AI/ML integration
- Cloud-native features
- Real-time streaming capabilities
- Enterprise security features

---

## Migration Guide

### Upgrading from 0.1.x to 1.1.0

#### Breaking Changes
- **Import Changes**: Main classes now available directly from package root
  ```python
  # Old way
  from credit_risk.core.application import CreditApplication
  
  # New way (recommended)
  from credit_risk import CreditApplication
  ```

#### New Features
- **CLI Usage**: New command-line interface
  ```bash
  # Install and use CLI
  pip install credit-risk-creditum
  credit-risk assess --type individual --data '{"credit_score": 720, ...}'
  ```

- **Configuration**: New configuration system
  ```python
  from credit_risk.config import get_config
  config = get_config()
  config.set('credit_application', 'min_credit_score', 650)
  ```

- **Logging**: Enhanced logging capabilities
  ```python
  from credit_risk.logging_config import setup_logging, get_logger
  setup_logging(log_level='INFO')
  logger = get_logger('my_module')
  ```

#### Deprecated Features
- None in this release, but future releases may deprecate some APIs

---

## Support

- **Documentation**: [https://crcreditum.com/documentation](https://crcreditum.com/documentation)
- **Issues**: [https://github.com/credit-risk-creditum/creditum/issues](https://github.com/credit-risk-creditum/creditum/issues)
- **Discussions**: [https://github.com/credit-risk-creditum/creditum/discussions](https://github.com/credit-risk-creditum/creditum/discussions)