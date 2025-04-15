import requests
import json
import sys
import time
import argparse
from datetime import datetime

def update_cluster_status(cluster_id, status, server_url="http://localhost:8000"):
    """Send a request to update cluster status.
    
    Args:
        cluster_id: ID of the cluster to update
        status: New status string for the cluster
        server_url: API server URL
        
    Returns:
        tuple: (success, response_data)
    """
    url = f"{server_url}/v1/public/cluster-status"
    
    payload = {
        "id": cluster_id,
        "status": status
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.patch(url, json=payload, headers=headers)
        request_time = time.time() - start_time
        
        print(f"Request completed in {request_time:.3f} seconds")
        print(f"Status code: {response.status_code}")
        
        response_data = response.json()
        print(json.dumps(response_data, indent=2))
        
        return response.ok, response_data
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return False, None
    except json.JSONDecodeError:
        print("Error: Response was not valid JSON")
        print(f"Raw response: {response.text}")
        return False, None

def simulate_cluster_lifecycle(cluster_id, server_url="http://localhost:8000"):
    """Simulate a complete cluster lifecycle with status updates."""
    statuses = [
        ("Creating", 2),
        ("Initializing", 3),
        ("Provisioning", 4),
        ("Running", 5),
        ("Upgrading", 4),
        ("Running", 3),
        ("Terminating", 2),
        ("Terminated", 0)
    ]
    
    for status, delay in statuses:
        print(f"\n=== Updating cluster {cluster_id} to '{status}' state ===")
        success, _ = update_cluster_status(cluster_id, status, server_url)
        
        if not success:
            print("Failed to update status, aborting simulation")
            return False
            
        if delay > 0:
            print(f"Waiting {delay} seconds before next status update...")
            time.sleep(delay)
    
    print("\nCluster lifecycle simulation completed!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update cluster status or simulate lifecycle')
    parser.add_argument('cluster_id', help='ID of the cluster to update')
    parser.add_argument('--status', '-s', help='New status for the cluster')
    parser.add_argument('--server', '-u', default='http://localhost:8000', help='API server URL')
    parser.add_argument('--simulate', '-sim', action='store_true', help='Simulate full cluster lifecycle')
    
    args = parser.parse_args()
    
    if args.simulate:
        print(f"Simulating cluster lifecycle for cluster {args.cluster_id}")
        simulate_cluster_lifecycle(args.cluster_id, args.server)
    elif args.status:
        print(f"Updating cluster {args.cluster_id} to status: {args.status}")
        success, _ = update_cluster_status(args.cluster_id, args.status, args.server)
        
        if success:
            print("Status update sent successfully!")
        else:
            print("Failed to update cluster status")
            sys.exit(1)
    else:
        print("Error: Please provide either --status or --simulate option")
        parser.print_help()
        sys.exit(1)
