# Architectural Report: Sales-Backend

## 1. Executive Summary
The `sales-backend` project is a Node.js application built on the **Express** framework. It serves as a centralized API service for managing sales incentives, user roles, configurations, and bill processing. The system utilizes a multi-database strategy, integrating **Sequelize** as an ORM to interface with **PostgreSQL**, **MySQL**, and **Redis**.

---

## 2. Structural Pattern & Directory Layout

### Structural Pattern
*   **FACT:** The project follows a **Controller-Route** pattern, which is a common variation of the Model-View-Controller (MVC) architecture adapted for RESTful APIs.
*   **INFERENCE:** Given the separation of concerns between `routes/` and the handler logic (often found in `controllers/` or service layers), the architecture is likely moving toward a **Layered Architecture**. The presence of `src/routes/v1/` suggests a versioned API design to maintain backward compatibility.

### Directory Layout (Inferred)
Based on the file paths identified in the metadata:
*   `src/server.js`: Entry point for the application, configuring Express and mounting route modules.
*   `src/routes/v1/`: Contains route definitions, grouped by domain (e.g., `user.route.js`, `incentive.route.js`, `bill-processor.route.js`).
*   `src/controllers/` (Inferred): Expected location for business logic handlers referenced in the routes (e.g., `BillStatusController`, `AutoApprovalController`).
*   `src/models/` (Inferred): Likely contains Sequelize model definitions for the various database entities.

---

## 3. Request Lifecycle
The request lifecycle follows a standard Express middleware-to-handler flow:

1.  **Entry Point:** The request hits `src/server.js`, which acts as the central router.
2.  **Routing:** The request is delegated to the appropriate versioned route file (e.g., `src/routes/v1/index.js`).
3.  **Middleware Execution:**
    *   **Security:** `validateJWT` is applied to most protected routes (e.g., `POST /pages`, `GET /users`).
    *   **Rate Limiting:** `fileOperationRateLimit` is used for resource-heavy endpoints (e.g., `GET /download`).
    *   **File Handling:** `upload.single("image")` or `customFileUpload` handles multipart form data.
4.  **Controller/Handler:** The request reaches the specific handler (e.g., `BillStatusController.listBill`).
5.  **Data Access:** The handler interacts with the database via **Sequelize** (ORM).
6.  **Response:** The controller sends a JSON response back to the client.

---

## 4. Key Architecture Patterns

*   **Versioned API Design:** The use of `src/routes/v1/` allows the team to evolve the API without breaking existing client integrations.
*   **Middleware-Driven Security:** Authentication and authorization are decoupled from business logic using the `validateJWT` middleware.
*   **Multi-Database Integration:** The project explicitly uses Sequelize to manage connections to multiple database technologies (PostgreSQL, MySQL, Redis), indicating a polyglot persistence strategy.
*   **Task-Based Routing:** The API is highly granular, with specific routes for distinct operations (e.g., `reprocess-bill`, `recalculation-bill`, `download-report`), which is characteristic of a service-oriented approach.
*   **Configuration-as-Code:** The inclusion of `swagger.js` and `/api-docs` indicates a commitment to API documentation and standardized interface definitions.

---

## 5. Summary Table: Fact vs. Inference

| Feature | Type | Description |
| :--- | :--- | :--- |
| **Framework** | FACT | Express.js |
| **ORM** | FACT | Sequelize |
| **Databases** | FACT | PostgreSQL, MySQL, Redis |
| **API Versioning** | FACT | `src/routes/v1/` structure |
| **Architecture** | INFERENCE | Layered/Controller-Route pattern |
| **Scalability** | INFERENCE | Use of Redis suggests caching or job queueing (Bull queues) |