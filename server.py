import json
import grpc
import time
from concurrent import futures
import banks_pb2_grpc
from branch import Branch

# Define constants
BASE_PORT = 30000  # Starting port for branches

def load_branches(filename):
    """Parse input JSON file to get branch configurations."""
    with open(filename) as f:
        data = json.load(f)

    branches = []
    for entry in data:
        if entry["type"] == "branch":
            branch = {
                "id": entry["id"],
                "balance": entry["balance"],
                "branches": [b["id"] for b in data if b["type"] == "branch"]
            }
            branches.append(branch)
    return branches

def serve_branch(branch_info):
    """Run a gRPC server for a single branch."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch = Branch(branch_info["id"], branch_info["balance"], branch_info["branches"])
    banks_pb2_grpc.add_BankServiceServicer_to_server(branch, server)
    port = BASE_PORT + branch_info["id"]
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Branch {branch_info['id']} started on port {port} with balance {branch_info['balance']}")
    server.wait_for_termination()

def main():
    branches = load_branches("input.json")

    # Start each branch in a separate thread and ensure all are up before customers connect
    branch_threads = []
    for branch_info in branches:
        thread = futures.ThreadPoolExecutor().submit(serve_branch, branch_info)
        branch_threads.append(thread)
        time.sleep(0.1)  # Small delay to avoid simultaneous port binding issues

    # Join all threads to keep the main process running
    for thread in branch_threads:
        thread.result()

if __name__ == "__main__":
    main()
