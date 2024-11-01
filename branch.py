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

    def MsgDelivery(self, request, context):
        if request.interface == "deposit":
            self.balance += request.money
            success = True
            for stub in self.stubList:
                try:
                    response = stub.Propagate_Deposit(request)
                    if response.result != "success":
                        success = False
                except Exception as e:
                    print(f"Propagation failed: {e}")
                    success = False
            return banks_pb2.Response(result="success" if success else "fail")
        
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.balance -= request.money
                success = True
                for stub in self.stubList:
                    try:
                        response = stub.Propagate_Withdraw(request)
                        if response.result != "success":
                            success = False
                    except Exception as e:
                        print(f"Propagation failed: {e}")
                        success = False
                return banks_pb2.Response(result="success" if success else "fail")
            return banks_pb2.Response(result="fail")
        
        elif request.interface == "query":
            return banks_pb2.Response(balance=self.balance)

    def Propagate_Deposit(self, request, context):
        self.balance += request.money
        return banks_pb2.Response(result="success")

    def Propagate_Withdraw(self, request, context):
        if self.balance >= request.money:
            self.balance -= request.money
            return banks_pb2.Response(result="success")
        return banks_pb2.Response(result="fail")