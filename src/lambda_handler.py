import json
import traceback  # <--- L'outil indispensable pour debugger
from langchain_core.messages import HumanMessage
from src.graph import graph


def lambda_handler(event, context):
    print(f"Event reçu: {json.dumps(event)}")

    try:
        # 1. Parsing
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        user_message = body.get("message", "")
        thread_id = body.get("thread_id", "default_user")
        command = body.get("command", None)

        print(f"Traitement pour thread_id: {thread_id}")  # Debug log

        config = {"configurable": {"thread_id": thread_id}}

        # 2. Exécution du Graph
        response = None
        if command == "RESUME":
            print("Commande RESUME détectée...")
            response = graph.invoke(None, config)

        elif user_message:
            print(f"Message utilisateur: {user_message}")
            response = graph.invoke(
                {"messages": [HumanMessage(content=user_message)]}, config
            )
        else:
            return {"statusCode": 400, "body": "Input invalide"}

        # 3. Extraction Réponse
        ai_content = "PAUSED_FOR_VALIDATION"

        if response and "messages" in response and len(response["messages"]) > 0:
            last_message = response["messages"][-1]
            ai_content = last_message.content

            if isinstance(ai_content, list):
                ai_content = "".join(
                    [item["text"] for item in ai_content if "text" in item]
                )

        print(f"Réponse générée : {ai_content}")  # Debug log

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "response": ai_content,
                    "thread_id": thread_id,
                    "is_paused": ai_content == "PAUSED_FOR_VALIDATION",
                }
            ),
        }

    except Exception as e:
        print("❌ CRASH REPORT ❌")
        traceback.print_exc()  # Affiche tout le détail dans CloudWatch
        print(f"Message d'erreur court : {e}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": "Voir les logs CloudWatch pour le détail",
                    "short_error": str(e),
                }
            ),
        }
