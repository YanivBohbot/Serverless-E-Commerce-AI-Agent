import boto3


def create_checkpoint_table():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table_name = "AgentCheckpoints"  # Nom de la table mémoire

    print(f"Création de la table de checkpoints : {table_name}...")
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "thread_id", "KeyType": "HASH"},
                {"AttributeName": "checkpoint_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "thread_id", "AttributeType": "S"},
                {"AttributeName": "checkpoint_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        print("✅ Table de mémoire créée avec succès !")
    except Exception as e:
        print(f"Info : {e}")


if __name__ == "__main__":
    create_checkpoint_table()
