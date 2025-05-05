from gradio_client import Client

client = Client("https://llm1-compute.cms.hu-berlin.de/")
result = client.predict(
    param_0="Hello!!",
    api_name="/chat"
)
print(result)
