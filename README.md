# VexDB Dify Plugin

This plugin provides **seamless integration between Dify and the VexDB vector database**, covering database discovery, table management, data insertion, and vector similarity search.  
It is designed for use cases such as **RAG (Retrieval-Augmented Generation)**, semantic search, and embedding storage & retrieval.

---

## Open Source Overview

This repository contains the **full implementation of the VexDB Dify plugin**, suitable for:

- Users who want to deploy Dify + VexDB in local or private environments  
- Developers who plan to extend or customize the plugin  
- Teams integrating VexDB’s vector database capabilities into **Agents** or **Workflows**

---

## Plugin Capabilities

| Capability | Description |
|----------|-------------|
| Database Discovery | List all databases in a VexDB instance |
| Table Management | List tables under a schema, with optional vector-table filtering |
| Schema Awareness | Retrieve column definitions, data types, and index metadata |
| Data Insertion | Insert a single row of data, including `floatvector` |
| Vector Search | Top-K similarity search with multiple distance metrics |

---

## Design Principles

- **Minimal Assumptions**: Does not rely on fixed table schemas, making it adaptable to diverse use cases  
- **Plug and Play**: One-time authorization is sufficient; supports `db_uri` override when needed  

---

## Security & Connection

- Database credentials are managed via Dify **Secret Input**
- No sensitive connection details are exposed in tool outputs
- Supports temporary connection overrides using `db_uri` for multi-database scenarios or debugging

---

## License

Maintained and provided by **shuzhiyinhang**.

You are welcome to fork, modify, and redistribute this project in accordance with the license.
