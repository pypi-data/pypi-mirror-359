import aiohttp
import pytest


class ApiForwarder:
    def __init__(self, server_hub_url: str,):
        """
        Initialize an ApiForwarder object.
        :param server_hub_url: http(s)://some-domen:xxxx/route
        """
        self.server_hub_url = server_hub_url
        # self.server_hub_port = server_hub_port
        # self.fetch_route = fetch_route

    async def forward(self, message: str) -> str:
        """

        :return:
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.server_hub_url,
                    json={"message": message}
            ) as resp:
                response_json = await resp.json()
                print(response_json)
        # resp = requests.post(self.server_hub_url, json={"message": message})
        # print(resp.json())
        return "It was successful"
