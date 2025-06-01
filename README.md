# DynamoDB_Pycrud

`dynamodb_pycrud` is a Python package that provides a simple interface to perform basic CRUD operations on AWS DynamoDB using AWS Python SDK, `boto3`. This package allows developers to interact with DynamoDB tables programmatically with minimal setup.

## Table of Contents

1. [Setup](#setup)
   * [Create Virtual Environment](#create-virtual-environment)
   * [AWS Configuration](#aws-configuration)
2. [Installation](#installation)
3. [Usage](#usage)
   * [Create a Client](#create-a-client)
   * [CRUD Operations](#crud-operations)
4. [Contribution](#contribution)
5. [License](#license)

## Setup

> [!TIP]
> It's recommended to install the package inside a virtual environment. This ensures that dependencies are isolated from your global Python environment.

### Create Virtual Environment

using `venv`:

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On MacOS/Linux:
source venv/bin/activate

# deactivate the virtual environment
deactivate
```

using `conda`:

```
# Create a conda environment
conda create --name myenv python=3.9

# Activate the conda environment
conda activate myenv

# deactivate the virtual environment
conda deactivate
```

### AWS Configuration

3 ways for AWS configuration are enlilsted here. For more: <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration">Setup AWS Configuration</a>

#### 1. Using `~/.aws/credentials` file

This is the recommended approach for managing AWS credentials securely.

1. **Locate or create the credentials file:**
   - **Windows:** `C:\Users\<YourUsername>\.aws\credentials`
   - **macOS/Linux:** `~/.aws/credentials`

2. **Add your AWS credentials in the following format:**
   ```ini
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY_ID
   aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
   region = YOUR_REGION

3. **Ensure that the file is secured (for macOS/Linux):**

  Confirm who is the owner:

  ```
      whoami
      ls -l ~/.aws/credentials
  ```

  If `whoami` matches the owner in the `ls` output, its safe to go with 600.

  ```
      # set the permissions to restrict access
      chmod 600 ~/.aws/credentials
  ```

  Run `ls -l ~/.aws/credentials` again to check updated restriction.

#### 2. Using a `.env` file

Credentials can be stored in a `.env` file and loaded using `python-dotenv`.
  1. Create a `.env` file in the project root directory:

```
    AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
    AWS_REGION=YOUR_REGION
```

  2. Add `.env` file to `.gitignore` preventing sensitive information from being committed:

```
    .env
```

  3. Load the `.env` file in your code:

  ```
  from dotenv import load_dotenv
  import os

  load_dotenv()

  aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
  aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
  aws_region = os.getenv("AWS_REGION")
  ```

  ```python
  # Example:
  from dynamodb_pycrud import DynamoCrud
  from dotenv import load_dotenv
  import os

  # Load environment variables from .env
  load_dotenv()

  # Boto3 will automatically pick up AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION
  # from environment variables if they are set.
  # You can then initialize DynamoCrud, optionally specifying a region:
  pycrud = DynamoCrud(region_name=os.getenv("AWS_REGION"))

  # Or, if the region is already set in the environment or you want boto3's default:
  # pycrud = DynamoCrud()
  ```

  > [!NOTE]
  > `boto3` automatically uses the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` environment variables if they are set. These variables are not directly passed into the `DynamoCrud` constructor.


> [!CAUTION]
> Avoid directly using aws keys inside the code and make sure to add sensitive files like `.env` and `~/.aws/credentials` to `.gitignore` file if they are inside the project directory.


#### 3. Using Environment Variables

Credentials can be set as environment variables.

- *Windows (cmd):*

  ```
  set AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
  set AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
  set AWS_REGION=YOUR_REGION
  ```

- *MacOS/Linux (Bash):*

  ```
  export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
  export AWS_REGION=YOUR_REGION
  ```
To make these variables persistent:
- *Windows:* Add them to the system environment variables via the Control Panel.
- *MacOS/Linux:* Add them to shell profile (e.g., `.baschrc`, `.zshrc` or `.bash-profile`):

  ```
  echo "export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID" >> ~/.bashrc
  echo "export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY" >> ~/.bashrc
  echo "export AWS_REGION=YOUR_REGION" >> ~/.bashrc
  ```

## Installation

Install the package directly from the Github repository:

```
pip install git+https://github.com/Ahnaf19/dynamodb_pycrud.git
```

### [optional] install dependencies from requirements.txt

> [!NOTE]
> use the requirements.txt from the repository if any dependency issue arises

```
pip install -r requirements.txt
```

## Usage

once installed, `DynamoCrud` class can be imported from the package:

```
from dynamodb_pycrud.dynamodb_pycrud import DynamoCrud
```

### Create a Client

Boto3, <a href="https://aws.amazon.com/sdk-for-python/">AWS SDK for Python</a>, looks at various configuration locations untill it finds configuration values. For about the lookup order, see: <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html">Configuration Overview</a>

To start interacting with DynamoDB, initialize the `DynamoCrud` client:

  ```
# Create the client
# If your AWS credentials and region are configured (e.g., via ~/.aws/credentials, environment variables),
# boto3 will use them automatically.
# You can optionally specify a region_name if you want to override the default or configured region.
pycrud = DynamoCrud(region_name="YOUR_AWS_REGION")

# If region_name is also configured or you want to use the default region for the session:
# pycrud = DynamoCrud()

  ```

> [!CAUTION]
> Avoid directly using aws keys inside the code and make sure to add sensitive files like `.env` and `~/.aws/credentials` to `.gitignore` file if they are inside the project directory.

### CRUD Operations

#### Create

1. Create a Table

Creates a DynamoDB table with a partition key and optional sort key and returns table metadata.

   ```
    pycrud.create_table(table_name, partition_key, partition_key_type, sort_key=None, sort_key_type=None, read_capacity=5, write_capacity=5)
   ```
   - `partition_key_type`: Type of the partition key ('S', 'N', 'B').
   - `sort_key_type`: Type of the sort key ('S', 'N', 'B'), required if `sort_key` is provided.

Example:

   ```
    response = dynamo_crud.create_table(
      table_name="MyTable",
      partition_key="id",
      partition_key_type="N",
      sort_key="category",
      sort_key_type="S",
      read_capacity=2,
      write_capacity=2,
    )
   ```

#### Read

1. List all Tables

Lists all available DynamoDB tables in given region and returns the list.

   ```
    pycrud.list_tables()
   ```

Example:

   ```
    tables = pycrud.list_tables()
   ```

2. Describe a Table

Returns metadata of given DynamoDB table.

   ```
    pycrud.describe_table(table_name)
   ```

Example:

   ```
    table_description = pycrud.describe_table("MyTable")
   ```

3. Get an Item

Returns a single item from a DynamoDB table based on its primary key.

   ```
    pycrud.get_item(table_name="MyTable", item_key=item_key)
   ```

Example:

   ```
    item_key = {"id": 101, "title": "Book Title"}
    response = pycrud.get_item(table_name="MyTable", item_key=item_key)
   ```

4. Get all Items

Returns all items from given DynamoDB table.

   ```
    pycrud.get_all_items("MyTable")
   ```

Example:

   ```
    items = pycrud.get_all_items("MyTable")
   ```

#### Update

1. Put an Item

Inserts an item into the given DynamoDB table with **overwriting** control. The item is automatically converted to DynamoDB format using a helper function.

   ```
    pycrud.put_item(
        table_name="Books",
        item=item,
        partition_key="id",
        sort_key="title",
        prevent_overwrite=True
    )
   ```

Example:

   ```
    item = {"id": 25, "title": "The Great Gatsby", "year": 1925, "author": "F. Scott Fitzgerald"}
    response = pycrud.put_item(
        table_name="Books",
        item=item,
        partition_key="id",
        sort_key="title",
        prevent_overwrite=True
    )
   ```

#### Delete

1. Delete an Item

Deletes an item from a DynamoDB table based on given primary key and returns the deleted item dictionary.

   ```
    pycrud.delete_item(table_name="MyTable", item_key=item_key)
   ```

Example:

   ```
    item_key = {"id": 101, "title": "Book Title"}
    response = pycrud.delete_item(table_name="MyTable", item_key=item_key)
   ```

2. Delete a Table

Deletes a specified DynamoDB table and returns the deleted table metadata.

   ```
    pycrud.delete_table("Books")
   ```

Example:

   ```
    response = pycrud.delete_table("Books")
   ```

## Contribution

Bug reports and pull requests are welcome on the <a href="https://github.com/Ahnaf19/dynamodb_pycrud">GitHub repo</a>

## License

This project is available as open source under the MIT License. See the [LICENSE](./LICENSE) file for details.
