# VexDB Dify Plugin

Provides one-stop integration capabilities for the **VexDB Vector Database** within **Dify Applications**, covering database browsing, table management, data writing, and vector similarity retrieval. It is suitable for scenarios such as RAG, semantic search, and Embedding storage and retrieval.

---

## Open Source Note

This repository provides the complete implementation of the **VexDB Dify Plugin**, suitable for:

* Users wishing to deploy Dify + VexDB in local/private environments.
* Developers wishing to perform secondary development based on existing capabilities.
* Teams wishing to integrate VexDB vector database capabilities into Agents / Workflows.

---

## Capabilities Overview

| Capability | Identity (ID) | Description |
| :--- | :--- | :--- |
| **Discover Databases** | `list_databases` | List all non-template databases in the VexDB instance. |
| **Manage Tables** | `list_tables` | List all tables in a schema, with support for filtering to return only tables containing vector columns. |
| **Schema Awareness** | `table_schema` | Retrieve metadata such as column names, data types, and indexes. |
| **Data Writing** | `insert_row` | Insert a single row of data, supporting JSON format and `floatvector` types. |
| **Vector Search** | `vector_search` | Perform TopK similarity search based on a `floatvector` column. |

---

## Detailed Usage Guide (Input Format Specifications)

When orchestrating in a Dify Agent or Workflow, please strictly adhere to the following parameter input specifications, especially regarding JSON data structures.

### 1. Insert Row
Insert a single row into the specified table.

* **Table Name (`table`)**: The target table name (String).
* **Row Data (`row`)**: **⚠️ Must be a valid JSON object string**.
    * The plugin internally uses a JSON parser to process this field, so property names **must use double quotes**.
    * Vector data must be represented as an array of floating-point numbers.
    * **LLM Input Example**:
        ```json
        {
          "content": "This is a test document fragment",
          "metadata": {"source": "wiki", "author": "admin"},
          "embedding": [0.012, -0.34, 0.88, 0.15]
        }
        ```
* **Schema**: Defaults to `public`.

### 2. Vector Search
Perform a similarity search.

* **Table Name (`table`)**: The target table name (String).
* **Vector Column (`vector_column`)**: The field name storing vector data (e.g., `embedding`).
* **Query Vector (`query_vector`)**: **⚠️ Must be a valid JSON array string**.
    * Format must be `[float, float, ...]`.
    * **LLM Input Example**:
        ```json
        [0.012, -0.34, 0.88, 0.15]
        ```
* **Distance Type (`distance_type`)**: Optional. Values: `l2` (Default, Euclidean), `cosine` (Cosine), `ip` (Inner Product).
* **Top K**: Number of results to return. Defaults to 5.

### 3. Get Table Schema
* **Table (`tables`)**:
    * **Empty**: Returns the schema for all tables in the current schema.
    * **Single Table**: Enter the table name, e.g., `users`.
    * **Multiple Tables**: Use **commas** to separate, e.g., `users, items`.

### 4. List Tables
* **Only Vector Tables (`only_vector_tables`)**: Boolean (`true`/`false`). If set to `true`, the plugin automatically filters out tables that do not contain fields with the `vector` type.

### 5. List Databases
* Lists all non-template databases in the VexDB instance.
* **DB URI (`db_uri`)**: Optional database connection string.

---

## Design Philosophy

* **Weak Assumption**: Does not strictly depend on specific table structures, making it suitable for multiple business scenarios.
* **Plug and Play**: Authorize once to use; supports `db_uri` override when necessary.

---

## Security & Connection

* **Global Configuration**: Database connection information is usually configured globally via Dify's **Secret Input** when installing the plugin.
* **Temporary Override**: All tools provide a `db_uri` parameter. If this parameter is filled when calling a tool, it will override the global configuration (useful for debugging or multi-database operations).
* **Privacy & Safety**: The plugin code captures exceptions and does not throw raw stack trace information in the Tool response, avoiding the leakage of sensitive connection strings.

---

## 📄 License

Maintained and provided by **shuzhiyinhang**.

Forking, modifying, and redistributing are welcome under the terms of the License.