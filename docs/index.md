# RELEASE DASHBOARD PAIRPOINT

### DESCRIPTION

The Release Dashboard backend tracks container image deployments across AWS EKS clusters, providing real-time visibility by namespace and cluster. Its centralized inventory helps teams verify application versions and ensure consistency across environments through platform-specific and customer solution dashboards.  

Access is secured with authentication controls, and environment configurations manage sensitive details like cluster credentials. A documented dependency file ensures consistent deployment, making it a reliable solution for managing containerized applications at scale.

## Backend Directory

The backend portion of the EKS-POC project is organized as follows:

### Core Files
- `app.py` - Main application entry point. It initializes and runs the Flask app, ensuring the required modules are loaded.  
- `.env` - Environment configuration file that stores sensitive information like database credentials and API keys.  
- `requirements.txt` - Contains dependencies such as `Flask`, `Flask-SQLAlchemy`, `psycopg2`, `boto3`, and `requests`. Install them using `pip install -r requirements.txt`.  


### Application Modules
- `login.py` - Handles authentication with routes for login, signup, and email verification. Stores user details like hashed passwords, OTPs, and verification status. Includes functions for generating OTPs, sending verification emails, and validating user credentials.  
- `inventory.py` - Handles Kubernetes cluster information retrieval and caching for multiple environments. Provides routes for fetching cluster deployments, refreshing and clearing cache, and managing environment configurations. Ensures efficient data retrieval with caching and supports multiple environments specified in `.env`.  
- `custsol_dash.py` - Manages the retrieval and caching of deployment information for customer solution clusters across multiple environments (dev, stg, prod). Provides routes for fetching customer solution data, refreshing caches, and organizing deployment versions for microservices. Integrates with Kubernetes and AWS to gather and manage deployment details.  
- `platform_dash.py` - Manages the retrieval and caching of deployment information for platform clusters across multiple environments (dev, lit, shared, stg, prod). Provides routes for fetching platform data, refreshing caches, and organizing deployment versions for microservices. Integrates with Kubernetes and AWS to gather and manage deployment details.  

### Configuration
- `__init__.py` - This file sets up the Flask application, initializes the database and mail configurations, and ensures that the necessary database is created if it doesn't already exist. It also sets up CORS for the application and registers blueprints for different modules including inventory, platform dashboard, customer solution dashboard, and login. It uses environment variables for sensitive configuration like database credentials and mail settings.  

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
