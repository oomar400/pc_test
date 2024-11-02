import grpc
import banks_pb2
import banks_pb2_grpc
import time

class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.stub = None

    def createStub(self):
        port = 30000 + self.id
        try:
            channel = grpc.insecure_channel(f'localhost:{port}')
            self.stub = banks_pb2_grpc.BankServiceStub(channel)
        except Exception as e:
            print(f"Failed to create stub for customer {self.id}: {e}")

    def executeEvents(self):
        for event in self.events:
            try:
                # Create request
                request = banks_pb2.Request(
                    id=event["id"],
                    interface=event["interface"],
                    money=event.get("money", 0)
                )
                # Execute request
                response = self.stub.MsgDelivery(request)

                # Process response
                if event["interface"] == "query":
                    time.sleep(3)
                    self.recvMsg.append({
                        "interface": "query",
                        "balance": response.balance
                    })
                else:
                    self.recvMsg.append({
                        "interface": event["interface"],
                        "result": response.result
                    })


            except Exception as e:
                print(f"Error executing event {event['id']} for customer {self.id}: {e}")
                self.recvMsg.append({
                    "interface": event["interface"],
                    "result": "fail"
                })