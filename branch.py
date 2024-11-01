import grpc
import banks_pb2
import banks_pb2_grpc
from concurrent import futures
import time

class Branch(banks_pb2_grpc.BankServiceServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.stubList = []
        self.recvMsg = []
        self.createStubs()

    def createStubs(self):
        for branch_id in self.branches:
            if branch_id != self.id:
                port = 30000 + branch_id
                try:
                    channel = grpc.insecure_channel(f'localhost:{port}')
                    stub = banks_pb2_grpc.BankServiceStub(channel)
                    self.stubList.append(stub)
                except Exception as e:
                    print(f"Failed to connect to Branch {branch_id}: {e}")

    def MsgDelivery(self, request, context):
        """Handle customer requests and ensure proper propagation."""
        if request.interface == "deposit":
            # First update local balance
            self.balance += request.money
            # Then propagate to other branches
            success = True
            for stub in self.stubList:
                try:
                    response = stub.Propagate_Deposit(banks_pb2.Request(
                        interface="deposit",
                        money=request.money
                    ))
                    if response.result != "success":
                        success = False
                        break
                except Exception as e:
                    print(f"Failed to propagate deposit: {e}")
                    success = False
                    break
            
            return banks_pb2.Response(result="success" if success else "fail")

        elif request.interface == "withdraw":
            if self.balance >= request.money:
                # First update local balance
                self.balance -= request.money
                # Then propagate to other branches
                success = True
                for stub in self.stubList:
                    try:
                        response = stub.Propagate_Withdraw(banks_pb2.Request(
                            interface="withdraw",
                            money=request.money
                        ))
                        if response.result != "success":
                            success = False
                            break
                    except Exception as e:
                        print(f"Failed to propagate withdraw: {e}")
                        success = False
                        break
                
                return banks_pb2.Response(result="success" if success else "fail")
            return banks_pb2.Response(result="fail")

        elif request.interface == "query":
            # Add small delay before query to ensure propagation is complete
            time.sleep(0.1)
            return banks_pb2.Response(balance=self.balance)

    def Propagate_Deposit(self, request, context):
        """Handle deposit propagation from other branches."""
        try:
            self.balance += request.money
            return banks_pb2.Response(result="success")
        except Exception as e:
            print(f"Failed to process deposit propagation: {e}")
            return banks_pb2.Response(result="fail")

    def Propagate_Withdraw(self, request, context):
        """Handle withdraw propagation from other branches."""
        try:
            if self.balance >= request.money:
                self.balance -= request.money
                return banks_pb2.Response(result="success")
            return banks_pb2.Response(result="fail")
        except Exception as e:
            print(f"Failed to process withdraw propagation: {e}")
            return banks_pb2.Response(result="fail")