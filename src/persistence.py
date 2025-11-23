import boto3
import json
import pickle
import base64
from typing import Optional, Any, Dict, Iterator, Tuple, Sequence

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)


class DynamoDBSaver(BaseCheckpointSaver):
    """
    Connecteur personnalisé pour sauvegarder l'état de LangGraph dans DynamoDB.
    Compatible LangGraph v0.2+
    """

    def __init__(self, table_name: str):
        super().__init__()
        # On laisse boto3 trouver la région tout seul (celle de la Lambda)
        self.client = boto3.resource("dynamodb")
        self.table = self.client.Table(table_name)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Récupère le dernier état sauvegardé."""
        thread_id = config["configurable"]["thread_id"]

        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("thread_id").eq(
                thread_id
            ),
            ScanIndexForward=False,
            Limit=1,
        )

        if not response["Items"]:
            return None

        item = response["Items"][0]

        # Désérialisation
        checkpoint = pickle.loads(base64.b64decode(item["checkpoint"]))
        metadata = json.loads(item["metadata"])

        parent_config = None
        if item.get("parent_checkpoint_id"):
            parent_config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": item["parent_checkpoint_id"],
                }
            }

        return CheckpointTuple(
            config=config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
        )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        yield from []

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> RunnableConfig:
        """Sauvegarde le nouvel état."""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]

        pickled_checkpoint = base64.b64encode(pickle.dumps(checkpoint)).decode("utf-8")

        item = {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint": pickled_checkpoint,
            "metadata": json.dumps(metadata),
            "type": "checkpoint",
        }

        self.table.put_item(Item=item)

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    # --- C'EST CETTE FONCTION QUI MANQUAIT ---
    def put_writes(
        self, config: RunnableConfig, writes: Sequence[Tuple[str, Any]], task_id: str
    ) -> None:
        """
        Méthode requise par les nouvelles versions de LangGraph.
        Sert à stocker les résultats intermédiaires.
        Pour ce tutoriel, on peut la laisser vide (pass) pour éviter le crash.
        """
        pass
