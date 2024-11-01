import json
from customer import Customer
import time

def main():
    with open('input.json') as f:
        data = json.load(f)

    deposit_responses = []

    for entry in data:
        if entry["type"] == "customer":
            customer = Customer(entry["id"], entry["events"])
            print(f"Serving customer {customer.id}")
            customer.createStub()
            customer.executeEvents()
            
            # If this is a deposit operation (first half of operations), save response
            if "deposit" in str(entry["events"]):
                deposit_responses.append({
                    "id": customer.id,
                    "recv": customer.recvMsg
                })
            time.sleep(0.1)  # Ensure propagation

    # Sort deposit responses by customer ID
    deposit_responses.sort(key=lambda x: x["id"])

    # Write only deposit responses to output
    with open('output.json', 'w') as f:
        json.dump(deposit_responses, f, indent=4)

if __name__ == "__main__":
    main()