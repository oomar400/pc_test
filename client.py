import json
from customer import Customer
import time

def main():
    with open('input.json') as f:
        data = json.load(f)

    customer_responses = []
    
    # Process all customers in sequence
    for entry in data:
        if entry["type"] == "customer":
            customer = Customer(entry["id"], entry["events"])
            print(f"Serving customer {customer.id}")
            customer.createStub()
            customer.executeEvents()
            
            # Store each customer's operation + query results
            customer_responses.append({
                "id": customer.id,
                "recv": customer.recvMsg
            })
            time.sleep(0.1)  # Ensure propagation

    # Sort by customer ID and write to output
    customer_responses.sort(key=lambda x: x["id"])
    with open('output.json', 'w') as f:
        json.dump(customer_responses, f, indent=4)

if __name__ == "__main__":
    main()