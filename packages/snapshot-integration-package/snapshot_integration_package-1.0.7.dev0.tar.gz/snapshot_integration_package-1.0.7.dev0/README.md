# snapshot_integration

snapshot_integration_package is a Python library designed to provide high-performance computations using pre-compiled `.pyd` modules. It offers efficient functionalities for data mapping, configuration management, and more.

## Features

- Fast execution with optimized `.pyd` modules
- Easy integration with Python projects
- Modular architecture for scalability

## Installation

You can install the package using pip:

```bash
pip install snapshot_integration_package
```

## Modules Included

### Modules:
- **`semiauto_main`**: 
- **`semiauto_misc`**: 
- **`semiauto_ps`**: 
- **`semiauto_rc`**: 



## Requirements

- Python 3.9 (Windows, 32-bit)
- Python 3.9 (Windows, 64-bit)
- Python 3.11 (Windows, 64-bit)

## License

This project is licensed under a **Proprietary License**. All rights are reserved. Unauthorized copying, modification, distribution, or use of this software, in whole or in part, is strictly prohibited without explicit permission from the author.

## Author

Pritesh Patel - [pritesh.patel@varchassolutions.com.au](mailto:pritesh.patel@varchassolutions.com.au)

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements. All contributions are subject to review and approval by the author.

---

*For any issues or support, please contact [pritesh.patel@varchassolutions.com.au](mailto:pritesh.patel@varchassolutions.com.au).*



# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2025-06-18
### Tested
-internal test

## [1.0.1] - 2025-06-18
### Tested
-internal test

## [1.0.2] - 2025-06-18
### Tested
-internal test

## [1.0.3] - 2025-06-18
### Added
- Initial release of `snapshot_integration_package`
- Core integration functionality with `.pyd` performance modules

## [1.0.4] - 2025-06-19
### Added
- Machine, Fixed Shunt, Switched Shunt, Load - quantites with MW and MVAR multiplied with 100 to reflect correct mapping.

## [1.0.5] - 2025-06-20
### Added
- folder structure improved
- generators modified to reflect Qmax and Qmin properly.

## [1.0.6] - 2025-06-20
### Added
- all being added machines are now being updated with original Qgen, Qmax and Qmin limits (due to being out of serrvice, machines Qlimits were orverwritten by a garbage value during load flow).
- automation now generates txt file in parent directory folders of the case to be added for the unsolved and/or unattempted generating system. those generating systems should be resolved manually.