import grpc
import banks_pb2
import banks_pb2_grpc
from concurrent import futures

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

    # attempting to force wait with a while loop
    def MsgDelivery(self, request, context):
        if request.interface == "deposit":
            while not all(self.propagate_deposit(request.money, stub) for stub in self.stubList):
                continue
            self.balance += request.money
            return banks_pb2.Response(result="success")

        elif request.interface == "withdraw":
            if self.balance >= request.money:
                while not all(self.propagate_withdraw(request.money, stub) for stub in self.stubList):
                    continue
                self.balance -= request.money
                return banks_pb2.Response(result="success")
            return banks_pb2.Response(result="fail")

        elif request.interface == "query":
            return banks_pb2.Response(balance=self.balance)

    def propagate_deposit(self, amount, stub):
        try:
            response = stub.Propagate_Deposit(
                banks_pb2.Request(interface="deposit", money=amount)
            )
            return response.result == "success"
        except Exception as e:
            print(f"Deposit propagation failed: {e}")
            return False

    def propagate_withdraw(self, amount, stub):
        try:
            response = stub.Propagate_Withdraw(
                banks_pb2.Request(interface="withdraw", money=amount)
            )
            return response.result == "success"
        except Exception as e:
            print(f"Withdraw propagation failed: {e}")
            return False

    def Propagate_Deposit(self, request, context):
        self.balance += request.money
        return banks_pb2.Response(result="success")

    def Propagate_Withdraw(self, request, context):
        if self.balance >= request.money:
            self.balance -= request.money
            return banks_pb2.Response(result="success")
        return banks_pb2.Response(result="fail")