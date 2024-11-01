import json
from customer import Customer
import time

def main():
    with open('input.json') as f:
        data = json.load(f)

    customers = []
    withdraw_responses = []

    # Process all entries in order (deposits will come first, then withdraws)
    for entry in data:
        if entry["type"] == "customer":
            customer = Customer(entry["id"], entry["events"])
            print(f"Serving customer {customer.id}")
            customer.createStub()
            customer.executeEvents()
            
            # If this is a withdraw operation (second half of customers in input), save response
            if "withdraw" in str(entry["events"]):
                withdraw_responses.append({
                    "id": customer.id,
                    "recv": customer.recvMsg
                })
            time.sleep(0.1)  # Ensure propagation

    # Sort withdraw responses by customer ID
    withdraw_responses.sort(key=lambda x: x["id"])

    # Write only withdraw responses to output
    with open('output.json', 'w') as f:
        json.dump(withdraw_responses, f, indent=4)

if __name__ == "__main__":
    main()