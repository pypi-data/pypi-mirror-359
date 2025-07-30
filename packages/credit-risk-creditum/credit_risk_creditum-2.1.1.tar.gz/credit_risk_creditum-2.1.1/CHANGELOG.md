# Changelog

All notable changes to the credit-risk-creditum package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-03

### ✨ New Features
- **Professional Tooltip System**: Enhanced contextual help with styled tooltips across all simulator panes
- **Economic Indicator Tooltips**: Detailed explanations for economic weights and rationales with visual indicators
- **Risk Factor Tooltips**: Comprehensive explanations for individual and corporate risk factors with calculation details
- **Modern Header Design**: Gradient backgrounds and enhanced visual hierarchy matching Solutions page quality
- **Improved User Experience**: Separated header section from simulator panes for better visual organization

### 🔧 Technical Improvements
- **Tooltip Consistency**: Unified tooltip format across EconomicIndicatorsChart and SimulatePage components
- **Code Cleanup**: Removed unused imports and fixed validation schema duplications
- **Enhanced Styling**: Professional CSS-based tooltips with hover effects and color-coded indicators
- **Component Architecture**: Better separation of concerns between header and main content areas

### 🎨 UI/UX Enhancements
- **Visual Polish**: Added gradient backgrounds, shadow effects, and modern animations
- **Information Architecture**: Clear hierarchical information display with contextual help
- **Accessibility**: Improved hover states and visual feedback for interactive elements

## [2.0.0] - 2025-01-02

### 🎉 Major Features
- **Comprehensive Stress Testing**: Full economic scenario analysis with side-by-side normal vs stressed result comparisons
- **Dynamic Recommendations Engine**: Personalized, decision-specific action plans that adapt to APPROVED/DECLINED/CONDITIONAL outcomes
- **Enhanced AI Explainability**: Intelligent text parsing with visual formatting, section recognition, and metric highlighting
- **Priority-Based Action Items**: Timeline and impact-driven recommendation system with HIGH/MEDIUM/LOW priority classifications

### 🔧 Technical Improvements
- **Dynamic Model Performance Metrics**: Eliminated hardcoded values, now uses real API data for precision, recall, F1-score, and AUC-ROC
- **Intelligent AI Explanation Parsing**: Advanced regex-based section recognition and content formatting
- **Decision-Specific Content Generation**: Unique experiences for APPROVED, DECLINED, and CONDITIONAL decisions
- **Stress Scenario Context**: Comprehensive stress test indicators throughout the entire user experience
- **Enhanced Data Flow**: Improved null-safe access patterns and API response handling

### 💔 Breaking Changes
- **Frontend API Integration**: Now expects additional optional response fields (model_performance, breakdown, recommendations)
- **Recommendation Structure**: API responses should include priority, timeline, and impact fields for optimal experience
- **UI Components**: Major interface changes require updated integration patterns

### 🎯 User Experience Enhancements
- **Visual Differentiation**: Clear distinction between normal and stressed economic scenarios
- **Complementary Sections**: Eliminated overlap between decision explanations and improvement recommendations
- **Interactive Checklists**: Quick-start action items for immediate user engagement
- **Educational Content**: Comprehensive explanations of stress testing and economic impact

### 📚 Documentation Updates
- **Feature Status**: Explainability now marked as fully implemented (removed "planned" status)
- **Comprehensive Guides**: Added stress testing tutorials and recommendation interpretation guides
- **API Documentation**: Updated with new response field structures and examples

## [1.1.6] - 2025-01-02

### Improved
- **Clean Code Examples**: Removed emojis from all code examples and print statements
- **Professional Output**: Code examples now produce clean, emoji-free output
- **Better Copy-Paste**: Examples can be copied and used in professional environments
- **Documentation Clarity**: Maintained emojis in documentation headers but cleaned code

## [1.1.5] - 2025-01-02

### Fixed
- **Risk Score Formatting**: Fixed TypeError when risk_score is None in rejected applications
- **Google Colab Compatibility**: Updated examples to handle None risk scores gracefully
- **Documentation Examples**: Added safe formatting for all risk score displays

### Enhanced
- **Rejected Applications**: Now return risk_score=1.0 instead of None for consistency
- **Error Handling**: Better handling of pre-screening rejections

## [1.1.4] - 2025-01-01

### Added
- **Comprehensive Documentation**: Enhanced README with 470+ lines of documentation
- **Real-World Examples**: Banking integration, fintech APIs, portfolio management
- **Google Colab Guide**: Complete guide with working examples and troubleshooting
- **CLI Documentation**: Detailed command-line interface usage
- **Performance Metrics**: Added speed, accuracy, and reliability metrics

### Enhanced
- **PyPI Page**: Dramatically improved package presentation and documentation
- **Examples**: Added extensive real-world use cases and integration patterns

## [1.1.3] - 2025-01-01

### Added
- **Comprehensive Documentation**: Complete Sphinx documentation with examples, tutorials, and API reference
- **Google Colab Guide**: Detailed guide for using the package in Google Colab with troubleshooting
- **Stress Testing Guide**: In-depth guide covering all stress testing scenarios and best practices
- **GitHub Pages**: Automated documentation deployment at https://credit-risk-creditum.github.io/creditum/

### Enhanced
- **Examples**: Extensive examples covering real-world use cases and scenario comparisons
- **Installation Guide**: Comprehensive installation instructions for all environments
- **Quick Start**: 5-minute setup guide for immediate productivity

### Changed
- **Documentation URL**: Updated package metadata to point to hosted documentation

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