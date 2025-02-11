# RELEASE DASHBOARD PAIRPOINT

### DESCRIPTION

The Release Dashboard backend tracks container image deployments across AWS EKS clusters, providing real-time visibility by namespace and cluster. Its centralized inventory helps teams verify application versions and ensure consistency across environments through platform-specific and customer solution dashboards.  

Access is secured with authentication controls, and environment configurations manage sensitive details like cluster credentials. A documented dependency file ensures consistent deployment, making it a reliable solution for managing containerized applications at scale.

## Backend Directory

The backend portion of the EKS-POC project is organized as follows:

### Core Files
- **`app.py`** - Main application entry point. It initializes and runs the Flask app, ensuring the required modules are loaded.  
- **`.env`** - Environment configuration file that stores sensitive information like database credentials and API keys.  
- **`requirements.txt`** - Contains dependencies such as `Flask`, `Flask-SQLAlchemy`, `psycopg2`, `boto3`, and `requests`. Install them using `pip install -r requirements.txt`.  


### Application Modules
- **`login.py`** - Handles authentication with routes for login, signup, and email verification. Stores user details like hashed passwords, OTPs, and verification status. Includes functions for generating OTPs, sending verification emails, and validating user credentials.  
- **`inventory.py`** - Handles Kubernetes cluster information retrieval and caching for multiple environments. Provides routes for fetching cluster deployments, refreshing and clearing cache, and managing environment configurations. Ensures efficient data retrieval with caching and supports multiple environments specified in `.env`.  
- **`custsol_dash.py`** - Manages the retrieval and caching of deployment information for customer solution clusters across multiple environments (dev, stg, prod). Provides routes for fetching customer solution data, refreshing caches, and organizing deployment versions for microservices. Integrates with Kubernetes and AWS to gather and manage deployment details.  
- **`platform_dash.py`** - Manages the retrieval and caching of deployment information for platform clusters across multiple environments (dev, lit, shared, stg, prod). Provides routes for fetching platform data, refreshing caches, and organizing deployment versions for microservices. Integrates with Kubernetes and AWS to gather and manage deployment details.  

### Configuration
- **`__init__.py`** - This file sets up the Flask application, initializes the database and mail configurations, and ensures that the necessary database is created if it doesn't already exist. It also sets up CORS for the application and registers blueprints for different modules including inventory, platform dashboard, customer solution dashboard, and login. It uses environment variables for sensitive configuration like database credentials and mail settings.  

# Environment Variables (`.env`)

This document outlines the essential environment variables required for the application. These variables configure general settings, database connections, mail server details, cache durations, cluster mappings, and cluster labels.

## General Settings
These variables define the core application configurations, such as AWS region, application port, and cache size, ensuring smooth operation and scalability.
```
AWS_DEFAULT_REGION="<your-region>"
PORT=<your-port>
CACHE_MAX_SIZE=<your-cache-size>
```

## Database Configuration
The database configuration variables provide authentication credentials and connection details. These ensure secure communication between the application and the database, facilitating data storage and retrieval.
```
DB_USER="<your-db-user>"
DB_PWD="<your-db-password>"
DB_ENDP="<your-db-endpoint>"
DB_PORT=<your-db-port>
DB_NAME="<your-db-name>"
```

## Mail Server Configuration
Mail server settings allow the application to send emails, such as notifications and user verifications. These variables include details about the SMTP server, authentication credentials, and the default sender address.
```
MAIL_SERVER="<your-mail-server>"
MAIL_PORT=<your-mail-port>
MAIL_USERNAME="<your-mail-username>"
MAIL_PASSWORD="<your-mail-password>"
MAIL_DEFAULT_SENDER="<your-mail-sender>"
```

## Cache Durations
Cache duration settings define the expiration time for cached data in different environments. This helps improve application performance by reducing redundant database queries and speeding up responses.
```
CACHE_DURATIONS={
    "dev": 120,
    "lit": 120,
    "staging": 120,
    "prod": 120,
    "dab-platform-loe": 120,
    "dab-platform-stg": 120,
    "dab-platform-prod": 120,
    "dab-custsol-loe": 120,
    "dab-custsol-staging": 120,
    "dab-custsol-prod": 120
}
```

## Clusters and Account Names
These variables list the Kubernetes clusters associated with different environments. They help in managing deployments, ensuring resources are correctly allocated to the appropriate clusters.
```
CLUSTERS={
    "dab-platform-loe": [
        "eks-microservices-dab-dev",
        "eks-microservices-dab-lit",
        "eks-dmz-dab-shared",
        "eks-sh-dab-shared",
        "eks-corda-dab-dev"
    ],
    "dab-platform-stg": [
        "eks-microservices-dab-stg",
        "eks-corda-dab-stg",
        "eks-dmz-dab-stg"
    ],
    "dab-platform-prod": [
        "eks-microservices-dab-prod",
        "eks-corda-dab-prod",
        "eks-dmz-dab-prod"
    ],
    "dab-custsol-loe": [
        "eks-microservices-cs-dev",
        "eks-dmz-cs-dev"
    ],
    "dab-custsol-staging": [
        "eks-microservices-dab-csstg",
        "eks-dmz-dab-csstg"
    ],
    "dab-custsol-prod": [
        "eks-microservices-dab-csprod",
        "eks-dmz-dab-csprod"
    ]
}
```

## Cluster Labels
Cluster labels categorize and identify clusters based on their environment and purpose. These labels assist in filtering and managing deployments efficiently.
```
PLT_DEV_LABEL="app.kubernetes.io/component=dab"
PLT_DEV_LABEL_KEY="app.kubernetes.io/component"
PLT_DEV_LABEL_VALUE="dab"
CS_DEV_LABEL_KEY="app.kubernetes.io/component"
CS_DEV_LABEL_VALUE="dab"
PLT_LABELLED_CLUSTER="eks-microservices-dab-dev"
CS_LABELLED_CLUSTER="eks-microservices-cs-dev"
```

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
