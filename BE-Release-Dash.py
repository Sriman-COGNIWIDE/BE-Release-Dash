from flask import Flask, jsonify
from kubernetes import client
import urllib3
import re
import json
from flask_cors import CORS
import os
from functools import wraps
from collections import defaultdict
import time
from datetime import datetime
from botocore.exceptions import ClientError
import boto3
import ast
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public')
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "OPTIONS", "POST"], "allow_headers": ["Content-Type"]}})

CACHE_DURATIONS = ast.literal_eval(os.getenv("CACHE_DURATIONS"))
CLUSTERS = ast.literal_eval(os.getenv("CLUSTERS"))

k8s_clients = {env: {} for env in CLUSTERS.keys()}

class EnvironmentCache:
    def __init__(self, maxsize=256):
        self.maxsize = maxsize
        self.cache = defaultdict(dict)
        self.last_access_time = defaultdict(float)

    def get_cache_timestamp(self, env, current_time=None):
        if current_time is None:
            current_time = time.time()
        
        if not self.last_access_time[env]:
            self.last_access_time[env] = current_time
            return current_time
        
        time_elapsed = current_time - self.last_access_time[env]
        duration = CACHE_DURATIONS[env]
        intervals = int(time_elapsed / duration)
        
        return self.last_access_time[env] + (intervals * duration)

    def cache_clear(self, env=None):
        if env is None:
            self.cache.clear()
            self.last_access_time.clear()
        else:
            if env in self.cache:
                del self.cache[env]
                del self.last_access_time[env]

    def __call__(self, func):
        @wraps(func)
        def wrapper(cluster_name, env, timestamp):
            cache_key = (cluster_name, timestamp)
            current_time = time.time()
            cache_timestamp = self.get_cache_timestamp(env, current_time)
            
            if current_time > (cache_timestamp + CACHE_DURATIONS[env]):
                self.cache[env].clear()  
                self.last_access_time[env] = current_time  
                cache_timestamp = current_time
                cache_key = (cluster_name, cache_timestamp)
            
            if cache_key in self.cache[env]:
                return self.cache[env][cache_key]
            
            result = func(cluster_name, env, cache_timestamp)
            self.cache[env][cache_key] = result
            
            if len(self.cache[env]) > self.maxsize:
                oldest_key = min(self.cache[env].keys(), key=lambda k: k[1])
                self.cache[env].pop(oldest_key)
            
            return result
        return wrapper

cluster_cache = EnvironmentCache(maxsize=int(os.getenv("CACHE_MAX_SIZE", 256)))

def get_formatted_time():
    return datetime.now().strftime("%I:%M %p")

def get_formatted_date():
    return datetime.now().strftime("%d-%m-%Y")

def get_aws_credentials(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    
    response = client.get_secret_value(
        SecretId=secret_name
    )
    
    secret = json.loads(response['SecretString'])
    
    credentials = {
        'access_key': secret['AWS_ACCESS_KEY_ID'],
        'secret_key': secret['AWS_SECRET_ACCESS_KEY'],
        'session_token': secret['AWS_SESSION_TOKEN'],
        'region': secret['AWS_DEFAULT_REGION']
    }
    
    if not credentials['access_key'] or not credentials['secret_key']:
        raise ValueError("AWS credentials not found in secret")
    
    return credentials

def get_cluster_credentials(cluster_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=os.getenv("AWS_DEFAULT_REGION")
    )
    
    response = client.get_secret_value(
        SecretId=cluster_name
    )
    
    try:
        secret = json.loads(response['SecretString'])
    except json.JSONDecodeError:
        secret = json.loads(json.loads(response['SecretString']))
    
    endpoint = secret.get('cluster_api_endpoint', '')
    
    if 'secret key secret value' in endpoint.lower():
        endpoint = endpoint.lower().replace('secret key secret value', '').strip()
    
    endpoint = endpoint.strip().replace('\\', '').strip('"')
    
    if not endpoint.startswith('https://'):
        if endpoint.startswith('//'):
            endpoint = 'https:' + endpoint
        else:
            endpoint = 'https://' + endpoint
    
    endpoint = ''.join(char for char in endpoint if ord(char) >= 32)
    
    token = secret.get('bearer_token', '')
    if token:
        token = token.strip().replace('\\', '').strip('"')
    
    if not endpoint or not token:
        raise ValueError(f"Required cluster credentials not found in secret for cluster {cluster_name}")
            
    return {
        'endpoint': endpoint,
        'token': token
    }

def list_eks_clusters(secret_name):
    credentials = get_aws_credentials(secret_name)
    
    eks = boto3.client('eks',
        aws_access_key_id=credentials['access_key'],
        aws_secret_access_key=credentials['secret_key'],
        aws_session_token=credentials['access_key'],
        region_name=credentials['region']
    )
    
    response = eks.list_clusters()
    return response['clusters']

VERSION_PATTERN = re.compile(r':([^:@]+)(?:@sha256:.+)?$')

def extract_version_from_image(image_string):
    match = VERSION_PATTERN.search(image_string)
    if not match:
        return "None"
    return match.group(1)

def process_container_images(containers):
    if not containers:
        return []
    return [{
        "image": container.image,
        "version": extract_version_from_image(container.image)
    } for container in containers]

def initialize_k8s_clients(env):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    clusters_found = []
    
    if env in CLUSTERS:
        if not isinstance(k8s_clients[env], dict):
            k8s_clients[env] = {}
            
        for acc_name in CLUSTERS[env]:
            clusters = list_eks_clusters(acc_name)
            
            for cluster_name in clusters:
                cluster_creds = get_cluster_credentials(cluster_name)
                
                if cluster_creds and cluster_creds['endpoint']:
                    if not cluster_creds['endpoint'].startswith('https://'):
                        continue
                        
                    configuration = client.Configuration()
                    configuration.host = cluster_creds['endpoint']
                    configuration.verify_ssl = False
                    configuration.api_key = {"authorization": f"Bearer {cluster_creds['token']}"}
                    
                    try:
                        test_client = client.ApiClient(configuration)
                        test_api = client.CoreV1Api(test_client)
                        test_api.get_api_resources()
                        
                        k8s_clients[env][cluster_name] = {
                            "apps_v1": client.AppsV1Api(test_client),
                            "core_v1": test_api
                        }
                        clusters_found.append(cluster_name)
                    except Exception:
                        continue
        
        return clusters_found
    else:
        raise ValueError(f"Environment '{env}' not supported")

def get_cache_timestamp(env):
    return cluster_cache.get_cache_timestamp(env)

@cluster_cache
def get_cluster_info_cached(cluster_name, env, timestamp):
    return get_cluster_info(cluster_name, env, CACHE_DURATIONS[env], timestamp)

def get_cluster_info(cluster_name, env, cache_duration, cache_timestamp):
    if cluster_name not in k8s_clients[env]:
        return {
            "status": "error",
            "error": {
                "type": "ClusterNotFound",
                "message": f"Cluster '{cluster_name}' not found in {env} environment"
            }
        }
    
    clients = k8s_clients[env][cluster_name]
    cluster_info = []
    
    fetch_time = get_formatted_time()
    fetch_date = get_formatted_date()
    
    namespaces = clients["core_v1"].list_namespace()
    
    for ns in namespaces.items:
        namespace_name = ns.metadata.name
        deployments = clients["apps_v1"].list_namespaced_deployment(namespace_name)
        
        for deployment in deployments.items:
            deployment_info = {
                "deployment-name": deployment.metadata.name,
                "namespace": namespace_name,
                "cluster": cluster_name,
                "main-containers": process_container_images(deployment.spec.template.spec.containers),
                "init-containers": process_container_images(deployment.spec.template.spec.init_containers) if deployment.spec.template.spec.init_containers else [],
            }
            cluster_info.append(deployment_info)
    
    return {
        "status": "success", 
        "data": cluster_info, 
        "time": fetch_time, 
        "date": fetch_date
    }

@app.route('/api/all-envs', methods=['GET'])
def get_all_environments():
    try:
        environments = list(CLUSTERS.keys())
        current_date_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        
        return jsonify({
            "status": "success",
            "data": environments,
            "date_time": current_date_time
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": {
                "type": "EnvironmentListError",
                "message": str(e)
            }
        }), 500

@app.route('/api/<env>', methods=['GET'])
def get_deployments_by_env(env):
    response_time = get_formatted_time()
    response_date = get_formatted_date()
    
    try:
        env = env.lower()
        if env not in CLUSTERS:
            return jsonify({
                "status": "error",
                "error": {
                    "type": "InvalidEnvironment",
                    "message": f"Environment '{env}' not supported"
                },
                "date_time": f"{response_date} {response_time}"
            }), 404

        if not k8s_clients.get(env, False):
            clusters = initialize_k8s_clients(env)
            if clusters:
                timestamp = get_cache_timestamp(env)
                all_cluster_details = []
                
                for cluster_name in clusters:
                    result = get_cluster_info_cached(cluster_name, env, timestamp)
                    if result.get("status") == "success":
                        all_cluster_details.extend(result["data"])
                        response_time = result.get("time", response_time)
                        response_date = result.get("date", response_date)
                
                return jsonify({
                    "status": "success",
                    "data": all_cluster_details,
                    "date_time": f"{response_date} {response_time}"
                })
            
            return jsonify({
                "status": "warning",
                "message": f"No clusters found for environment: {env}",
                "data": [],
                "date_time": f"{response_date} {response_time}"
            })
        
        timestamp = get_cache_timestamp(env)
        all_cluster_details = []
        
        for cluster_name in k8s_clients[env].keys():
            result = get_cluster_info_cached(cluster_name, env, timestamp)
            if result.get("status") == "success":
                all_cluster_details.extend(result["data"])
                response_time = result.get("time", response_time)
                response_date = result.get("date", response_date)
        
        return jsonify({
            "status": "success",
            "data": all_cluster_details,
            "date_time": f"{response_date} {response_time}"
        })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": {
                "type": "GeneralException",
                "message": str(e)
            },
            "date_time": f"{response_date} {response_time}"
        }), 500
    
@app.route('/api/cache/refresh/<env>', methods=['POST'])
def refresh_env_cache(env):
    try:
        env = env.lower()
        if env not in CLUSTERS:
            return jsonify({
                "status": "error",
                "error": {
                    "type": "InvalidEnvironment",
                    "message": f"Environment '{env}' not supported"
                }
            }), 404

        cluster_cache.cache_clear(env)
        
        if env in k8s_clients:
            k8s_clients[env].clear()
        
        clusters = initialize_k8s_clients(env)
        if not clusters:
            return jsonify({
                "status": "warning",
                "message": f"No clusters found for {env} environment"
            })

        all_deployments = []
        current_date_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        for cluster_name in clusters:
            result = get_cluster_info_cached(cluster_name, env, time.time())
            if result.get("status") == "success":
                all_deployments.extend(result["data"])

        return jsonify({
            "status": "success",
            "message": f"Cache refreshed for {env} environment",
            "data": all_deployments,
            "date_time":current_date_time
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    try:
        cluster_cache.cache_clear()
        
        for env in k8s_clients:
            k8s_clients[env].clear()
        
        return jsonify({
            "status": "success",
            "message": "Cache cleared successfully",
            "time": get_formatted_time(),
            "date": get_formatted_date()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    app.run(host='0.0.0.0', port=port, debug=True)
    