import requests



class ApiForwarder:
    def __init__(self, server_hub_url: str,):
        """
        Initialize an ApiForwarder object.
        :param server_hub_url: http(s)://some-domen:xxxx/route
        """
        self.server_hub_url = server_hub_url
        # self.server_hub_port = server_hub_port
        # self.fetch_route = fetch_route

    def forward(self, message: str) -> str:
        """

        :return:
        """
        resp = requests.post(self.server_hub_url, json={"message": message})
        print(resp.json())
        return "It was successful"
