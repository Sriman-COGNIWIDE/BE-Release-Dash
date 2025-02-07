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
