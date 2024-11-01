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
        if request.interface == "deposit":
            self.propagate_to_other_branches("deposit", request.money)
            return banks_pb2.Response(result="success")
        
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.propagate_to_other_branches("withdraw", request.money)
                return banks_pb2.Response(result="success")
            return banks_pb2.Response(result="fail")
        
        elif request.interface == "query":
            time.sleep(0.5)
            return banks_pb2.Response(balance=self.balance)

    def propagate_to_other_branches(self, action, amount):
        for stub in self.stubList:
            try:
                request = banks_pb2.Request(interface=action, money=amount)
                if action == "deposit":
                    stub.Propagate_Deposit(request)
                else:  # withdraw
                    stub.Propagate_Withdraw(request)
            except Exception as e:
                print(f"Propagation failed: {e}")

    def Propagate_Deposit(self, request, context):
        self.balance += request.money
        return banks_pb2.Response(result="success")

    def Propagate_Withdraw(self, request, context):
        if self.balance >= request.money:
            self.balance -= request.money
            return banks_pb2.Response(result="success")
        return banks_pb2.Response(result="fail")