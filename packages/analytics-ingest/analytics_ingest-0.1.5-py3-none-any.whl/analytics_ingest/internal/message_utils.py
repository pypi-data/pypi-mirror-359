from analytics_ingest.internal.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.mutations import GraphQLMutations


def create_message(executor: GraphQLExecutor, variables: dict) -> str:
    message_input = {
        "name": variables["messageName"],
        "networkName": variables["networkName"],
        "ecuName": variables.get("ecuName", ""),
        "arbId": variables.get("arbId", ""),
        "ecuId": variables.get("ecuId", ""),
        "fileId": variables.get("fileId", ""),
        "messageDate": variables.get("messageDate", ""),
        "requestCode": variables.get("requestCode", ""),
    }

    response = executor.execute(
        GraphQLMutations.create_message(), {"input": {"messages": [message_input]}}
    )

    messages = response["data"].get("createMessage", [])
    if not messages:
        raise RuntimeError("No messages created")

    return messages[0]["id"]
