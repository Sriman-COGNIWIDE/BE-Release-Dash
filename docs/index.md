# RELEASE DASHBOARD PAIRPOINT

## Description

The Release Dashboard backend system is a comprehensive solution designed to manage and monitor multiple AWS EKS clusters across different account types. The system integrates platform-specific and customer solution dashboards to provide detailed cluster information and management capabilities. Through its platform dashboard, administrators can monitor and manage platform account clusters, while the customer solution dashboard offers dedicated visibility into customer-specific deployments.

The system incorporates a centralized inventory management system that tracks resources across all accounts, ensuring efficient resource utilization and management. Access to these features is controlled through a robust authentication system that manages user permissions and access controls. The backend service is initialized and orchestrated through a main application component, which coordinates the interactions between different modules.

To maintain security and flexibility, the system utilizes environment configurations for managing sensitive information such as credentials and connection details. All required dependencies are clearly documented in the dependency management file, facilitating consistent deployment and maintenance of the system.

This architecture enables comprehensive management of EKS clusters while maintaining security and operational efficiency, making it an effective solution for organizations managing multiple AWS EKS environments.

## Backend Directory

The backend portion of the EKS-POC project is organized as follows:

### Core Files
- `app.py` - Main application entry point
- `.env` - Environment configuration file
- `requirements.txt` - Python dependencies

### Application Modules
- `login.py` - Authentication and user management
- `inventory.py` - Inventory management functionality
- `custsol_dash.py` - Customer solutions dashboard
- `platform_dash.py` - Platform dashboard implementation

### Configuration
- `__init__.py` - Python package initialization

## File Organization

```
EKS-POC/
└── Backend/
    ├── __init__.py
    ├── .env
    ├── app.py
    ├── custsol_dash.py
    ├── inventory.py
    ├── login.py
    ├── platform_dash.py
    └── requirements.txt
```
