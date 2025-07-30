from src.ha_conversation_api_forwarder.api_forwarder import ApiForwarder

class TestApiForwarder:
    def test_init(self):
        api_forwarder = ApiForwarder(server_hub_url="http://localhost:8080")

    async def test_forward(self):
        api_forwarder = ApiForwarder(server_hub_url="http://localhost:8080")
        await api_forwarder.forward(message="Test message")