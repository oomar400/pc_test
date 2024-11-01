import json
from customer import Customer
def main():
    with open('input.json') as f:
        data = json.load(f)

    customers = []
    for entry in data:
        if entry["type"] == "customer":
            customer = Customer(entry["id"], entry["events"])
            print("Serving customer : ", customer.id)
            customer.createStub()
            customer.executeEvents()
            customers.append(customer)

    # Collect results (recvMsg) for each customer and save or print
    output = [{"id": customer.id, "recv": customer.recvMsg} for customer in customers]
    with open('output.json', 'w') as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
