import asyncio
from dataclasses import dataclass

from dabeaz.network import NetworkManager


@dataclass
class Dummy:
    id: str

    async def echo(self, sender: str, msg: str) -> str:
        return msg


def test_rpc():
    async def run():
        net = NetworkManager()
        a = Dummy("a")
        b = Dummy("b")
        net.register(a)
        net.register(b)
        return await net.rpc("a", "b", "echo", "hi")

    assert asyncio.run(run()) == "hi"
