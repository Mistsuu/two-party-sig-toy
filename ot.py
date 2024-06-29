from group import Group
from random import randint
from Crypto.Util.strxor import strxor

"""
    Every protocol starts from Sender -> Receiver.

    Sender Round 1 -----> Receiver Round 1 -----> Sender Round 2 -----> Receiver Round 2 -----> So on...
"""

class OTSender:
    group = Group()

    def __init__(self):        
        self.dataStateRound = {}
        self.toOtherRound = {}

        # Random element for receiver to choose
        self.α = [
            self.group.random_scalar(),
            self.group.random_scalar(),
        ]

    def doRound1(self):
        group = self.group

        b = group.random_scalar()
        B = b * group.generator()

        self.dataStateRound[1] = {
            "b": b,
            "B": B,
        }
        self.toOtherRound[1] = {
            "B": B
        }

    def doRound2(self, OTReceiverRound1Msg):
        A = OTReceiverRound1Msg["A"]
        B = self.dataStateRound[1]["B"]
        b = self.dataStateRound[1]["b"]

        group = self.group

        ρ0 = group.hash_to_scalar(b*A)
        ρ1 = group.hash_to_scalar(b*(A - B))

        HHρ0 = group.hash_to_bytes(group.hash_to_bytes(int(ρ0)))
        HHρ1 = group.hash_to_bytes(group.hash_to_bytes(int(ρ1)))
        ξ    = strxor(HHρ0, HHρ1)

        self.dataStateRound[2] = {
            "ρ0": ρ0,
            "ρ1": ρ1,
            "ξ": ξ,
        }
        self.toOtherRound[2] = {
            "ξ": ξ,
        }

    def doRound3(self, OTReceiverRound2Msg):
        HHρ0_ = OTReceiverRound2Msg["HHρ0_"]
        ρ0    = self.dataStateRound[2]["ρ0"]
        ρ1    = self.dataStateRound[2]["ρ1"]

        group = self.group

        Hρ0  = group.hash_to_bytes(int(ρ0))
        Hρ1  = group.hash_to_bytes(int(ρ1))
        HHρ0 = group.hash_to_bytes(Hρ0)
        if HHρ0_ != HHρ0:
            raise ValueError("Round 3 OT sender check failed!")
        
        self.dataStateRound[3] = {}
        self.toOtherRound[3] = {
            "Hρ0": Hρ0,
            "Hρ1": Hρ1,
        }

    def doRound4(self, OTReceiverRound3Msg):
        ρ0 = self.dataStateRound[2]["ρ0"]
        ρ1 = self.dataStateRound[2]["ρ1"]

        α0, α1 = self.α
        α̅0 = α0 + ρ0
        α̅1 = α1 + ρ1

        self.dataStateRound[4] = {}
        self.toOtherRound[4] = {
            "α̅0": α̅0,
            "α̅1": α̅1,
        }
        

class OTReceiver:
    group = Group()

    def __init__(self) -> None:
        self.dataStateRound = {}
        self.toOtherRound = {}

        # Choose bit to select which element
        # in α of sender we'll choose.
        self.ω = randint(0, 1)


    def doRound1(self, OTSenderRound1Msg: dict):
        group = self.group

        B = OTSenderRound1Msg["B"]
        a = group.random_scalar()
        G = group.generator()
        ω = self.ω

        A  = a*G + ω*B
        ρω = group.hash_to_scalar(a*B)

        self.dataStateRound[1] = {
            "a": a,
            "A": A,
            "ρω": ρω,
        }
        self.toOtherRound[1] = {
            "A": A,
        }

    def doRound2(self, OTSenderRound2Msg: dict):
        ρω = self.dataStateRound[1]["ρω"]
        ξ  = OTSenderRound2Msg["ξ"]

        group = self.group

        Hρω  = group.hash_to_bytes(int(ρω))
        HHρω = group.hash_to_bytes(Hρω)
        if self.ω == 1:
            HHρ0_ = strxor(HHρω, ξ)
        else:
            HHρ0_ = HHρω

        self.dataStateRound[2] = {
            "HHρ0_": HHρ0_,
            "ξ":     ξ,
        }
        self.toOtherRound[2] = {
            "HHρ0_": HHρ0_
        }

    def doRound3(self, OTSenderRound3Msg: dict):
        Hρ0 = OTSenderRound3Msg["Hρ0"]
        Hρ1 = OTSenderRound3Msg["Hρ1"]
        ξ   = self.dataStateRound[2]["ξ"]

        group = self.group

        HHρ0 = group.hash_to_bytes(Hρ0)
        HHρ1 = group.hash_to_bytes(Hρ1)
        if strxor(HHρ0, HHρ1) != ξ:
            raise ValueError("Round 3 OT receiver check failed!")

        self.dataStateRound[3] = {}
        self.toOtherRound[3]   = {}

    def doRound4(self, OTSenderRound4Msg: dict):
        α̅ = [
            OTSenderRound4Msg["α̅0"],
            OTSenderRound4Msg["α̅1"],
        ]
        ρω = self.dataStateRound[1]["ρω"]

        ω  = self.ω
        αω = α̅[ω] - ρω

        self.dataStateRound[4] = {
            "αω": αω
        }
        self.toOtherRound[4] = {}


if __name__ == '__main__':
    sender = OTSender()
    recver = OTReceiver()

    sender.doRound1()
    recver.doRound1(sender.toOtherRound[1])
    sender.doRound2(recver.toOtherRound[1])
    recver.doRound2(sender.toOtherRound[2])
    sender.doRound3(recver.toOtherRound[2])
    recver.doRound3(sender.toOtherRound[3])
    sender.doRound4(recver.toOtherRound[3])
    recver.doRound4(sender.toOtherRound[4])

    recver_αω = recver.dataStateRound[4]["αω"]
    print(f"{sender.α = }")
    print(f"{recver.ω = }")
    print(f'recver.α[ω] = {recver_αω}')
