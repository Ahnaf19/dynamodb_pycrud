from typing import Optional


# Validation for schema
def validate_keys(
    table_description: dict, partition_key: str, sort_key: Optional[str]
) -> bool:
    """
    Validates that the partition and sort keys match the schema in the table description.
    """

    key_schema = table_description["KeySchema"]

    # Check if the sort key is required but missing
    if len(key_schema) > 1 and not sort_key:
        print(f"[-] Missing sort key, required to match with table schema.")
        return False

    # Validate partition key
    partition_key_exists = any(
        key["AttributeName"] == partition_key and key["KeyType"] == "HASH"
        for key in key_schema
    )
    if not partition_key_exists:
        print(
            f"[-] Invalid partition key '{partition_key}'. It does not match the table schema."
        )
        return False

    # Validate sort key if provided
    if sort_key:
        sort_key_exists = any(
            key["AttributeName"] == sort_key and key["KeyType"] == "RANGE"
            for key in key_schema
        )
        if not sort_key_exists:
            print(
                f"[-] Invalid sort key '{sort_key}'. It does not match the table schema."
            )
            return False

    return True


# Check required keys in item
def check_item_keys(item: dict, partition_key: str, sort_key: Optional[str]) -> bool:
    """
    Ensures that the item contains the required partition and optional sort key.
    """
    if partition_key not in item:
        print(f"[-] Item is missing partition key: '{partition_key}'")
        return False
    if sort_key and sort_key not in item:
        print(f"[-] Item is missing sort key: '{sort_key}'")
        return False
    return True


def convert_to_dynamodb_format(item: dict) -> dict:
    """
    Converts a dictionary to the DynamoDB item format with type specifications.
    """
    dynamodb_item = {}
    for key, value in item.items():
        if isinstance(value, str):
            dynamodb_item[key] = {"S": value}
        elif isinstance(value, bool):  # must be over int check otherwise error
            dynamodb_item[key] = {"BOOL": value}
        elif isinstance(value, int):
            dynamodb_item[key] = {"N": str(value)}
        elif isinstance(value, float):
            dynamodb_item[key] = {"N": str(value)}
        elif isinstance(value, list):
            dynamodb_item[key] = {
                "L": [convert_to_dynamodb_format({"item": v})["item"] for v in value]
            }
        elif isinstance(value, dict):
            dynamodb_item[key] = {"M": convert_to_dynamodb_format(value)}
        else:
            raise TypeError(f"[-] Unsupported data type for DynamoDB: {type(value)}")
    return dynamodb_item
