import json
from customer import Customer
import time

def main():
    with open('input.json') as f:
        data = json.load(f)

    all_responses = []

    for entry in data:
        if entry["type"] == "customer":
            customer = Customer(entry["id"], entry["events"])
            print(f"Serving customer {customer.id}")
            customer.createStub()
            customer.executeEvents()
            
            # Save every customer response (both deposits and withdrawals)
            all_responses.append({
                "id": customer.id,
                "recv": customer.recvMsg
            })
    # Write all responses to output
    with open('output.json', 'w') as f:
        json.dump(all_responses, f, indent=4)

if __name__ == "__main__":
    main()