from typing import Optional, Literal
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from .dynamodb_pycrud_helpers import (
    validate_keys,
    check_item_keys,
    convert_to_dynamodb_format,
)


class DynamoCrud:

    def __init__(self, region_name: Optional[str] = None) -> None:
        """
        Initializes a DynamoDB client session. Checks for AWS credentials and handles
        missing or incomplete credentials.

        Parameters:
        - region_name (Optional[str]): AWS region name. Uses default session region if not provided.

        Raises:
        - NoCredentialsError: If no credentials are available.
        - PartialCredentialsError: If only partial credentials are found.
        """

        try:
            # Use the explicit region if provided, otherwise use the default session configuration
            self.session = boto3.Session(region_name=region_name)
            self.dynamodb = self.session.client("dynamodb")
            print("[+] DynamoDB client initialized successfully.")

        except NoCredentialsError:
            print("[-] No AWS credentials found. Please configure your credentials.")
            raise

        except PartialCredentialsError:
            print(
                "[-] Incomplete AWS credentials. Ensure both Access Key and Secret Key are set."
            )
            raise

        except Exception as e:
            print(f"[-] An unexpected error occurred during initialization: {e}")
            raise

    def list_tables(self) -> list:
        """
        Lists all available DynamoDB tables in the configured AWS region.

        Returns:
            List[str]: A list of table names as strings if retrieval is successful.
                    Returns an empty list if an error occurs.
        """

        try:
            # list all available tables in the region
            response = self.dynamodb.list_tables()
            print(f"[+] table names collected.")
            return response.get("TableNames", [])

        except ClientError as e:
            error_message = (
                f"[-] Unexpected error occurred: {e.response['Error']['Message']}"
            )
            print(error_message)
            return []

    def describe_table(self, table_name: str) -> dict:
        """
        Retrieves and prints details about a DynamoDB table, including its primary keys,
        Global Secondary Indexes (GSIs), and Local Secondary Indexes (LSIs), if available.

        Parameters:
        - table_name (str): The name of the DynamoDB table to describe.

        Returns:
        - dict: Dictionary containing the table's metadata if successful.
        - Empty dict: If the table does not exist or an error occurs.

        Raises:
        - ClientError: If a general AWS error occurs while accessing the table details.
        """

        try:
            # Describe the table
            response = self.dynamodb.describe_table(TableName=table_name)
            table_description = response["Table"]

            # Extract and print primary key details
            print("[+] Primary Key:")
            for key in table_description["KeySchema"]:
                print(f"  - {key['AttributeName']} ({key['KeyType']})")

            return table_description

        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"[-] Table '{table_name}' not found.")
            return {}

        except ClientError as e:
            print(
                f"[-] Error describing table '{table_name}': {e.response['Error']['Message']}"
            )
            return {}

        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            return {}

    def create_table(
        self,
        table_name: str,
        partition_key: str,
        partition_key_type: Literal["S", "N", "B"],
        sort_key: Optional[str] = None,
        sort_key_type: Optional[Literal["S", "N", "B"]] = None,
        read_capacity: int = 1,
        write_capacity: int = 1,
    ):
        """
        Creates a DynamoDB table with the specified primary key and optional sort key.

        Parameters:
        - table_name (str): Name of the table to create.
        - partition_key (str): Name of the partition key (primary key).
        - partition_key_type (Literal['S', 'N', 'B']): Data type for the partition key ('S' for string, 'N' for number, 'B' for binary).
        - sort_key (Optional[str]): Name of the sort key, if any.
        - sort_key_type (Optional[Literal['S', 'N', 'B']]): Data type for the sort key, if provided.
        - read_capacity (int): Read capacity units for provisioned throughput (default is 1).
        - write_capacity (int): Write capacity units for provisioned throughput (default is 1).

        Returns:
        - Tuple[str, Dict]: A tuple containing:
            - str: Status message of the table creation process.
            - Dict: A dictionary with the table description if creation or retrieval is successful,
                    or an empty dictionary if an error occurs.
        """

        try:
            # check if table already exists
            print(f"[] Checking if {table_name} exists...")
            response = self.dynamodb.describe_table(
                TableName=table_name
            )  # This will raise an error if the table does not exist
            exist_message = f"[-] Table '{table_name}' already exists."
            print(exist_message)
            print(f"[-] printing table description:")
            print(f"{response['Table']}")
            return (exist_message, response["Table"])

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"[-] Table '{table_name}' does not exist. Creating it now...")

                # Define table schema
                KeySchema = [
                    {"AttributeName": partition_key, "KeyType": "HASH"}
                ]  # partition key
                AttributeDefinitions = [
                    {
                        "AttributeName": partition_key,
                        "AttributeType": partition_key_type,
                    }
                ]

                if sort_key and sort_key_type:
                    KeySchema.append(
                        {"AttributeName": sort_key, "KeyType": "RANGE"}
                    )  # sort key  [optional]
                    AttributeDefinitions.append(
                        {"AttributeName": sort_key, "AttributeType": sort_key_type}
                    )

                # Create the table
                try:
                    table = self.dynamodb.create_table(
                        TableName=table_name,
                        KeySchema=KeySchema,
                        AttributeDefinitions=AttributeDefinitions,
                        ProvisionedThroughput={
                            "ReadCapacityUnits": read_capacity,
                            "WriteCapacityUnits": write_capacity,
                        },
                    )

                    # Wait until the table exists
                    print(f"[+] printing table creation request:")
                    print(table["TableDescription"])
                    waiter = self.dynamodb.get_waiter("table_exists")
                    waiter.wait(
                        TableName=table_name,
                        WaiterConfig={"Delay": 3, "MaxAttempts": 20},
                    )
                    success_message = (
                        f"[+] Table '{table_name}' has been created successfully."
                    )
                    print(success_message)
                    print(f"[+] printing table description:")
                    response = self.dynamodb.describe_table(TableName=table_name)
                    print(f"{response['Table']}")
                    return (success_message, response["Table"])

                except ClientError as e:
                    error_message = f"[-] Unexpected error occurred: {e.response['Error']['Message']}"
                    print(error_message)
                    return (error_message, {})

            else:
                error_message = (
                    f"[-] Unexpected error occurred: {e.response['Error']['Message']}"
                )
                print(error_message)
                return (error_message, {})

    def put_item(
        self,
        table_name: str,
        item: dict,
        partition_key: str,
        sort_key: Optional[str] = None,
        prevent_overwrite: bool = False,
    ) -> dict:
        """
        Inserts an item into DynamoDB with schema validation and optional overwrite prevention.

        Parameters:
        - table_name (str): The DynamoDB table name.
        - item (dict): The item data to insert, without DynamoDB-specific type wrappers.
        - partition_key (str): The partition key name.
        - sort_key (Optional[str]): The sort key name, if applicable.
        - prevent_overwrite (bool): If True, prevents overwriting existing items with the same primary key resulting in conditional request failed.

        Returns:
        - dict: The response from DynamoDB if the insertion is successful.
        - Empty dict: If an error occurs during the insertion.

        Example:
        >>> item = {"id": 25, "book_name": "anotherBook", "genre": "Short Story", "year": 2010, "isActive": True}
        >>> response = put_item(table_name="MyTable", item=item, partition_key="id", sort_key="book_name", prevent_overwrite=True)
        >>> print(response)
        """

        try:
            # Describe table to check existence and schema
            table_description = self.describe_table(table_name)
            # print(table_description)
            if not table_description:
                # print(f"[-] Table '{table_name}' does not exist.") # describe_table() already prints the error text
                return {}

            # Validate schema with table description
            if not validate_keys(table_description, partition_key, sort_key):
                print("[-] Item insertion aborted due to invalid schema.")
                return {}

            # Check item keys
            if not check_item_keys(item, partition_key, sort_key):
                print("[-] Item insertion aborted due to missing key(s) in item.")
                return {}

            # Convert item to DynamoDB format
            print("[] creating dynamodb item...")
            dynamodb_item = convert_to_dynamodb_format(item)
            print(dynamodb_item)

            # Set up condition expression to prevent overwrite if required
            condition_expression = None
            if prevent_overwrite:
                condition_expression = f"attribute_not_exists({partition_key})"
                if sort_key:
                    condition_expression += f" AND attribute_not_exists({sort_key})"

            print("[] Putting dynamodb item...")
            if condition_expression:
                response = self.dynamodb.put_item(
                    TableName=table_name,
                    Item=dynamodb_item,
                    ConditionExpression=condition_expression,
                )
            else:
                response = self.dynamodb.put_item(
                    TableName=table_name, Item=dynamodb_item
                )
                print("[] overwriting even if primary key exists already...")
            print("[+] Item inserted successfully.")
            return response

        except ClientError as e:
            print(f"[-] Error inserting item: {e.response['Error']['Message']}")
            return {}

    def get_item(self, table_name: str, item_key: dict) -> dict:
        """
        Retrieves an item from DynamoDB based on the provided primary key.

        Parameters:
        - table_name (str): The DynamoDB table name.
        - item_key (dict): The item key containing the partition key and, if applicable, the sort key.

        Returns:
        - dict: The retrieved item from DynamoDB if found.
        - Empty dict: If the item does not exist or an error occurs.

        Example:
        >>> item_key = {"id": 25, "book_name": "anotherBook"}
        >>> response = get_item(table_name="MyTable", item_key=item_key)
        >>> print(response)
        """
        try:
            # Describe table to check existence and schema
            table_description = self.describe_table(table_name)
            if not table_description:
                # print(f"[-] Table '{table_name}' does not exist.") # describe_table() already prints the error text
                return {}

            # Get key schema to determine if a sort key is required
            partition_key = next(
                (
                    key["AttributeName"]
                    for key in table_description["KeySchema"]
                    if key["KeyType"] == "HASH"
                ),
                None,
            )
            sort_key = next(
                (
                    key["AttributeName"]
                    for key in table_description["KeySchema"]
                    if key["KeyType"] == "RANGE"
                ),
                None,
            )

            # Check if provided item_key matches schema requirements
            if partition_key not in item_key or (sort_key and sort_key not in item_key):
                print("[-] Item retrieval aborted due to missing key(s) in item_key.")
                return {}

            # Convert item_key to DynamoDB key format
            dynamodb_key = convert_to_dynamodb_format(item_key)

            # Get the item from DynamoDB
            response = self.dynamodb.get_item(TableName=table_name, Key=dynamodb_key)

            if "Item" in response:
                print("[+] Item retrieved successfully.")
                return response["Item"]
            else:
                print(
                    f"[-] Item with the specified key(s) not found in '{table_name}'."
                )
                return {}

        except ClientError as e:
            print(f"[-] Error retrieving item: {e.response['Error']['Message']}")
            return {}

        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            return {}

    def get_all_items(self, table_name: str) -> list:
        """
        Retrieves all items from a DynamoDB table based on the provided primary key.

        This method scans the table to fetch all items that match the given primary key.

        Parameters:
            table_name (str): The name of the DynamoDB table from which to retrieve the items.

        Returns:
            - list: A list of dictionaries representing the items found in the table.

        Example:
            >>> all_items = dynamo_crud.get_all_items("your_table_name")
            >>> print(all_items)
            [
                {"partition_key": "value1", "sort_key": "1", "attribute1": "value1", "attribute2": "value2"},
                {"partition_key": "value2", "sort_key": "2", "attribute1": "value3", "attribute2": "value4"}
            ]
        """
        try:
            # Check if the table exists
            table_description = self.describe_table(table_name)
            if not table_description:
                # print(f"[-] Table '{table_name}' does not exist.") # describe_table() already prints the error text
                return []

            # Perform a scan to get all items from the table
            scan_response = self.dynamodb.scan(TableName=table_name)

            # If no items found, return an empty list
            if not scan_response.get("Items"):
                print(f"[-] No items found in table {table_name}.")
                return []

            # Return the list of items
            print(f"[+] Items retrieved from {table_name}.")
            return scan_response["Items"]

        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"[-] Table {table_name} does not exist.")
            return []

        except ClientError as e:
            print(f"[-] An error occurred: {e.response['Error']['Message']}")
            return []

    def delete_item(self, table_name: str, item_key: dict) -> dict:
        """
        Deletes an item from a DynamoDB table based on the provided primary key.

        Parameters:
            table_name (str): The name of the DynamoDB table from which to delete the item.
            item_key (dict): A dictionary containing the primary key (partition key and
                                optionally sort key) of the item to delete.

        Returns:
            - dict: The item details of the deleted item, or an empty dict if the item does not exist.

        Example:
        >>> dynamo_crud = DynamoCrud()
        >>> dynamo_crud.delete_item('MyTable', {'partition_key': 'value1'})
        Item for {'partition_key': 'value1'} deleted.
        {'partition_key': 'value1', 'sort_key': 'value1', 'attribute1': 'value1'}

        >>> dynamo_crud.delete_item('MyTable', {'partition_key': 'value2'})
        No item found with primary key {'partition_key': 'value2'} to delete.
        {}

        >>> dynamo_crud.delete_item('NonExistentTable', {'partition_key': 'value1'})
        ValueError: Table NonExistentTable does not exist.
        """

        try:
            # Check if the table exists
            table_description = self.describe_table(table_name)
            if not table_description:
                # print(f"[-] Table '{table_name}' does not exist.") # describe_table() already prints the error text
                return {}

            # Extract key schema to check the primary key structure
            key_schema = table_description["KeySchema"]
            key_names = {key["AttributeName"]: key["KeyType"] for key in key_schema}

            # Validate item_key
            for required_key in key_names.keys():
                if required_key not in item_key:
                    print(f"[-] Missing required key: {required_key}")
                    return {}

            # Convert item_key to DynamoDB format
            dynamodb_key = convert_to_dynamodb_format(item_key)

            # Attempt to delete the item
            delete_response = self.dynamodb.delete_item(
                TableName=table_name, Key=dynamodb_key, ReturnValues="ALL_OLD"
            )

            # Check if any item was deleted
            if "Attributes" not in delete_response:
                print(f"[-] No item found with primary key {item_key} to delete.")
                return {}

            # If the item was deleted, return the attributes
            print(f"[+] Item for {item_key} deleted.")
            return delete_response.get("Attributes", {})

        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"[-] Table {table_name} does not exist.")
            return {}

        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            print(f"[-] Error occurred: {error_message}")
            return {}

        except Exception as e:
            print(f"[-] An unexpected error occurred: {str(e)}")
            return {}

    def delete_table(self, table_name: str) -> dict:
        """
        Deletes a DynamoDB table with the specified name if it exists. It might take some time to delete successfully.

        Parameters:
        - table_name (str): The name of the DynamoDB table to delete.

        Returns:
        - dict: The response from the DynamoDB delete_table operation if successful.
        - Empty dict: If the table does not exist or an error occurs.
        """

        try:
            # Initiate table deletion
            response = self.dynamodb.delete_table(TableName=table_name)
            print(f"[] Table '{table_name}' is being deleted.")

            # Wait until the table is fully deleted
            self.dynamodb.get_waiter("table_not_exists").wait(
                TableName=table_name, WaiterConfig={"Delay": 2, "MaxAttempts": 20}
            )
            print(f"[+] Table '{table_name}' has been successfully deleted.")
            return response

        except self.dynamodb.exceptions.ResourceNotFoundException:
            print(f"[-] Table '{table_name}' does not exist.")
            return {}

        except ClientError as e:
            print(
                f"[-] Error deleting table '{table_name}': {e.response['Error']['Message']}"
            )
            return {}

        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            return {}
