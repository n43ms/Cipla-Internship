# Brutal & Detailed Critical Review: Will This Stack Actually Work in Cipla?
## Architectural Risk Registry, Failure Mode Analysis, and Remediation Matrix

This document provides a cold, objective, and detailed engineering critique of deploying the current codebase (Vite/React, Python/FastAPI, SQLAlchemy, PostgreSQL) in Microsoft Azure for Cipla. It analyzes where the system will fail, why it will fail, and how to mitigate those risks.

---

## 1. Executive Summary & Verdict

**Verdict**: The current architecture is a functional *local prototype*, but it **will not work** in a corporate production Azure environment without immediate, specific remediation of several architectural bottlenecks. 

The primary failure points are not related to coding syntax. They are:
1. **Out-of-Memory (OOM) Ingestion Crashes** when parsing XLSB files in serverless web nodes.
2. **HTTP Transaction Timeouts** on the Azure Load Balancer during heavy data ingestion runs.
3. **Database Locking during Materialized View refreshes**, which causes frontend 504 Gateway Timeouts.
4. **SSL/TLS handshake failures** caused by corporate firewall decryption proxies.
5. **Corporate Data Privacy and Outbound Networking blocks** on external LLM calls (Gemini).

---

## 2. Deep Dive: Core Failure Modes

```text
[User Uploads File] 
       |
       v
+-------------------------------+
| Azure SWA / Gateway           |
| Timeout (>230s Idle Limit)    |  <-- FAILURE MODE 1: Ingestion takes 5+ minutes; gateway drops connection.
+-------------------------------+
       |
       v
+-------------------------------+
| Azure Container App (FastAPI) |
| memory spike (OOM crash)      |  <-- FAILURE MODE 2: calamine parses 10MB XLSB, RAM spikes >1GB, ACA kills container.
+-------------------------------+
       |
       v
+-------------------------------+
| Azure Database (PostgreSQL)   |
| View Locked (No reads)        |  <-- FAILURE MODE 3: REFRESH MATERIALIZED VIEW locks table; reads hang.
+-------------------------------+
```

### Failure Mode 2.1: Ingestion Memory Bottleneck (OOM Crashes)
* **How the code works**: The ingestion orchestrator uses `python-calamine` and Pandas to parse XLSB sheets (e.g., `Sri Lanka RCPA Report Apr'25 - Mar'26.xlsb` which has 159k+ rows, and `Nepal RCPA` which has 134k+ rows).
* **The Problem**: Calamine loading XLSB files deserializes the binary structure in memory. When loaded into Pandas, memory overhead typically scales to **15x–20x the raw file size**. Loading a 10MB XLSB file with 160,000 rows can consume between **300MB and 1.2GB of RAM** in Python.
* **The Failure**: If the FastAPI backend is running inside an Azure Container App configured with standard cost-saving resources (e.g., 0.5 vCPU, 1GB Memory), the container will trigger the **Linux Out-Of-Memory (OOM) killer** and crash instantly during file upload.

### Failure Mode 2.2: Ingestion Timeout (Azure Load Balancer Limits)
* **How the code works**: The user uploads a file, and the FastAPI endpoint synchronously triggers the ingestion pipeline and waits for the database writes to complete before returning a response.
* **The Problem**: Writing 160,000 aggregated rows to PostgreSQL, running event matching logic, and calling `REFRESH MATERIALIZED VIEW` can take **between 2 and 6 minutes** depending on connection pools and database IOPS.
* **The Failure**: Azure Static Web Apps and Azure App Service have a **hardcoded idle timeout of 230 seconds (3.8 minutes)** on the Azure Load Balancer. If a request does not write bytes to the socket for 230 seconds, the load balancer closes the connection, returning a `504 Gateway Timeout` to the frontend, even though the background ingestion continues to run. This results in duplicate ingestions or partial state corruptions.

### Failure Mode 2.3: Read Lock Hangups (Stale Materialized Views)
* **How the code works**: After ingestion, `refresh_dashboard_materialized_views()` is executed:
  ```sql
  REFRESH MATERIALIZED VIEW mv_doctor_roi;
  REFRESH MATERIALIZED VIEW mv_territory_opportunity;
  ```
* **The Problem**: Standard `REFRESH MATERIALIZED VIEW` takes an **exclusive AccessExclusiveLock** on the view. This blocks all read queries (`SELECT`) against that view until the refresh is complete.
* **The Failure**: While the database is compiling the doctor ROI and territory views (which can take 30–90 seconds for 290k records), any user browsing the dashboard will see their page **hang and eventually time out**.

### Failure Mode 2.4: Corporate SSL Interception ("Easy Auth" & SSL Verify Failures)
* **How the code works**: Python libraries like `requests`, `urllib3`, or the Google Generative AI SDK rely on Python's built-in `certifi` package for SSL certificate validation when calling external APIs.
* **The Problem**: Cipla's corporate network uses TLS decryption proxies to inspect outbound traffic. The proxy signs outbound requests with a custom corporate Root CA.
* **The Failure**: Because the container running FastAPI does not trust the custom corporate Root CA, all outbound calls (e.g., calling Gemini API, fetching external exchange rates) will fail instantly with:
  ```text
  SSLError(MaxRetryError("SSL: CERTIFICATE_VERIFY_FAILED"))
  ```

---

## 3. Remediation Matrix & Architecture Adjustments

To transition this application from a local prototype to a robust, enterprise-grade Azure service, the following changes must be implemented:

| Identified Risk | Severity | Root Cause | Target Remediation (Azure Ecosystem) |
| :--- | :--- | :--- | :--- |
| **Ingestion OOM Crashes** | **High** | Calamine/Pandas memory spike inside serverless web nodes. | **Asynchronous Job Delegation**: Offload ingestion to an **Azure Container Job** or **Azure Function (Premium)** with higher memory ceilings, rather than executing it within the web container. |
| **HTTP Gateway Timeouts** | **High** | Synchronous API calls running longer than the 230s Load Balancer idle limit. | **Asynchronous Task Pattern**: Return a `202 Accepted` status with a `Task ID` immediately upon file upload. Use a polling endpoint `/api/ingestion/status/{id}` to query progress. |
| **DB Locking Hangups** | **Medium** | `REFRESH MATERIALIZED VIEW` locking read queries. | **Concurrent Refreshes**: Define a unique index on all materialized views (e.g. `CREATE UNIQUE INDEX ON mv_doctor_roi (pcode_normalized, country_id)`) and execute: `REFRESH MATERIALIZED VIEW CONCURRENTLY`. |
| **AED / FX Conversion Bug** | **High** | Hardcoded exchange rate set to `1:1` for AED, overstating UAE values. | **Seed Corrections**: Correct the currency seed database table to use the peg `3.6725` for AED and transition from hardcoded python constants to dynamic database lookups. |
| **Outbound SSL Failures** | **Medium** | Corporate firewall TLS inspection blocking outbound requests. | **CA Certificate Injection**: Inject the corporate CA certificate (.pem/crt) into the Docker image's trust store (`/usr/local/share/ca-certificates/`) during the CI/CD build phase. |
| **Data Privacy (AI calls)** | **Medium** | Sending doctor metrics out of the network boundary to public API keys. | **Private AI Endpoints**: Transition ExecAI from external Gemini to a dedicated **Azure OpenAI (GPT-4o)** endpoint hosted inside the Cipla corporate subscription. |
