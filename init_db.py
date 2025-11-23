import boto3


def setup_dynamo():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table_name = "ECommerceOrders"

    # 1. Create the  table
    try:
        print(f"Création table {table_name}...")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "order_id", "KeyType": "HASH"}
            ],  # Clé primaire
            AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        print("Table créée avec succès !")
    except Exception as e:
        print("La table existe déjà, on continue.")
        table = dynamodb.Table(table_name)

    # 2. Remplissage des données (Seed)
    print("Insertion des fausses données...")
    with table.batch_writer() as batch:
        batch.put_item(
            Item={
                "order_id": "CMD-123",
                "status": "shipped",
                "item": "Wireless Headphones",
                "price": 200,
            }
        )
        batch.put_item(
            Item={
                "order_id": "CMD-456",
                "status": "processing",
                "item": "Mechanical Keyboard",
                "price": 150,
            }
        )
        batch.put_item(
            Item={
                "order_id": "CMD-789",
                "status": "delivered",
                "item": "4K Monitor",
                "price": 400,
            }
        )

    print("Données insérées. Base de données prête.")


if __name__ == "__main__":
    setup_dynamo()
