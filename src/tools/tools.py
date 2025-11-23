from langchain_core.tools import tool
import boto3
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_aws import AmazonKnowledgeBasesRetriever

os.environ = os.getenv("TAVILY_API_KEY")


# Connexion à DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("ECommerceOrders")


@tool
def get_order_status(order_id: str):
    """
    Retrieves order status from DynamoDB. Input: order ID (CMD-xxx).
    """

    try:
        response = table.get_item(Key={"order_id": order_id})
        item = response.get("Item")
        if item:
            return f"Order Data: {item}"
        return f"Error: Order {order_id} not found in database."
    except Exception as e:
        return f"System Error: {str(e)}"


@tool
def initiate_refund(order_id: str):
    """
    Initiates a refund. Validation: Order must be 'delivered'.
    """

    try:
        response = table.get_item(Key={"order_id": order_id})
        item = response.get("Item")
        if not item:
            return "Order not found."

        if item["status"] != "delivered":
            return f"Refund failed: Status is '{item['status']}'. Must be 'delivered'."

        # 2. Simulation de l'écriture (Update)
        # Dans un vrai cas, on changerait le statut en 'refunded'
        return f"Success: Refund processed for {order_id}. Money sent to bank."
    except Exception as e:
        return f"Error: {str(e)}"


# --- NOUVEAUX OUTILS (RAG & WEB) ---

# Outil de Recherche Web (Tavily)
tavily_tool = TavilySearchResults(max_results=2)
tavily_tool.name = "web_search"
tavily_tool.description = (
    "Utilise cet outil pour chercher des informations ACTUELLES sur internet news tech."
)


# Outil RAG (Bedrock Knowledge Base)
@tool
def lookup_policy(query: str):
    """
    Utilise cet outil pour consulter la POLITIQUE DE RETOUR, la GARANTIE ou la FAQ technique interne.
    """
    try:
        # On configure le retriver AWS
        retriever = AmazonKnowledgeBasesRetriever(
            knowledge_base_id="E0IN6VZ3M9",
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 3}},
        )
        # On lance la recherche
        docs = retriever.invoke(query)

        if not docs:
            return "Aucune information trouvée dans la base de connaissance interne."

        # On concatène les morceaux de textes trouvés pour les donner à l'IA
        return "\n\n".join([doc.page_content for doc in docs])

    except Exception as e:
        return f"Erreur RAG: {str(e)}"


# Export list
SAFE_TOOLS = [get_order_status, tavily_tool, lookup_policy]
RISKY_TOOLS = [initiate_refund]

# Liste complète pour le LLM (il doit connaître les deux)
ALL_TOOLS_LIST = SAFE_TOOLS + RISKY_TOOLS
