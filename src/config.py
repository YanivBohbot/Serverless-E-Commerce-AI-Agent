import boto3
from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="amazon.nova-micro-v1:0",  # L'ID exact du modèle Sonnet 3.5
    model_kwargs=dict(
        temperature=0
    ),  # 0 = réponse très factuelle et stable, idéal pour un agent
    region_name="us-east-1",  # Remplace par ta région (ex: eu-central-1 ou us-east-1)
)
