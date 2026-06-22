```
.
├── app.js                      # Main application entry point
├── environments/               # Environment-specific configurations
│   └── index.js
├── src/
│   ├── common/                 # Common utilities, constants, templates
│   │   ├── auth-header.js
│   │   ├── contants.js
│   │   └── templates/
│   │       └── crmApiPath/
│   │           ├── developPath.js
│   │           ├── prodPath.js
│   │           └── stagePath.js
│   ├── config/                 # Application configurations
│   │   ├── logger.js
│   │   ├── redis.js
│   │   └── sequelize.js
│   ├── cloudJobs/              # Cloud-specific job definitions
│   │   └── incentiveCalculation.js
│   ├── controllers/            # Request handlers, orchestrating business logic
│   │   ├── accessories-grp.controller.js
│   │   ├── auth.controller.js
│   │   ├── auto-approval.controller.js
│   │   ├── bill-processor.controller.js
│   │   ├── bill-status.controller.js
│   │   ├── common.controller.js
│   │   ├── custom-incentive.controller.js
│   │   ├── health.controller.js
│   │   ├── incentive-split.controller.js
│   │   ├── incentive.controller.js
│   │   ├── kitty-auto-approval.controller.js
│   │   ├── kitty-config.controller.js
│   │   ├── kitty-details.controller.js
│   │   ├── kitty-emp-config.controller.js
│   │   ├── kitty-rule-attribute.controller.js
│   │   ├── kitty-rule-config.controller.js
│   │   ├── page-access.controller.js
│   │   ├── pages.controller.js
│   │   ├── program.controller.js
│   │   ├── push-notification.controller.js
│   │   ├── queue.controller.js
│   │   ├── sales-category-group.controller.js
│   │   ├── sales-category.controller.js
│   │   ├── sales-target.controller.js
│   │   ├── user-roles.controller.js
│   │   └── user.controller.js
│   ├── cron/                   # Scheduled tasks
│   │   ├── Pushnotification.js
│   │   ├── checkKittyDetails.js
│   │   └── index.js
│   ├── metrics/                # Monitoring and metrics related files
│   │   └── bullBoard.js
│   ├── middlewares/            # Express middleware for request processing
│   │   ├── auth.js
│   │   ├── authCfMiddleware.js
│   │   ├── common-error-handler.js
│   │   ├── common-not-found-error.js
│   │   ├── csrf-protection.js
│   │   ├── file-upload.js
│   │   ├── index.js
│   │   └── validate-json.js
│   ├── models/                 # Sequelize database models
│   │   └── index.js
│   ├── queues/                 # Queue definitions (e.g., BullMQ)
│   │   └── incentiveQueue.js
│   ├── repo/                   # Repository implementations
│   │   └── push-notification.repo.js
│   ├── response/               # Standardized API response structures
│   │   ├── errorResponse.js
│   │   └── response.js
│   ├── routes/                 # API route definitions
│   │   ├── health.route.js
│   │   └── v1/                 # Versioned API routes
│   │       ├── accessories-grp.route.js
│   │       ├── auth.route.js
│   │       ├── auto-approval.route.js
│   │       ├── bill-processor.route.js
│   │       ├── bill-status.route.js
│   │       ├── common.routes.js
│   │       ├── custom-incentive.route.js
│   │       ├── incentive-split.route.js
│   │       ├── incentive.route.js
│   │       ├── index.js
│   │       ├── kitty-auto-approval.routes.js
│   │       ├── kitty-config.routes.js
│   │       ├── kitty-details.routes.js
│   │       ├── kitty-emp-config.routes.js
│   │       ├── kitty-rule-attribute.routes.js
│   │       ├── kitty-rule-config.routes.js
│   │       ├── page-access.routes.js
│   │       ├── pages.routes.js
│   │       ├── program.route.js
│   │       ├── push-notification.route.js
│   │       ├── queue.route.js
│   │       ├── sales-category-group.routes.js
│   │       ├── sales-category.routes.js
│   │       ├── sales-target.routes.js
│   │       ├── user-roles.routes.js
│   │       └── user.route.js
│   ├── server.js               # Express server setup and main routing
│   ├── services/               # Business logic and orchestration
│   │   ├── accessories-grp.service.js
│   │   ├── additional-incentive.service.js
│   │   ├── auto-approval.service.js
│   │   ├── bill-processor.service.js
│   │   ├── bill-status.service.js
│   │   ├── custom-incentive.service.js
│   │   ├── incentive-kitty.service.js
│   │   ├── incentive-split.service.js
│   │   ├── incentive.service.js
│   │   ├── keycloak.service.js
│   │   ├── kitty-auto-approval.service.js
│   │   ├── kitty-emp.service.js
│   │   ├── kitty-rule-attribute.service.js
│   │   ├── kitty-rule.service.js
│   │   ├── kitty.service.js
│   │   ├── page-access.service.js
│   │   ├── pages.service.js
│   │   ├── program.service.js
│   │   ├── push-notification.service.js
│   │   ├── sales-category-group.service.js
│   │   ├── sales-category.service.js
│   │   ├── sales-target.service.js
│   │   ├── user-token.service.js
│   │   ├── user.service.js
│   │   └── user_roles.service.js
│   ├── utils/                  # General utility functions
│   │   ├── common-api-error.js
│   │   ├── common-helpers.js
│   │   ├── emailNotify.js
│   │   ├── file-system.js
│   │   ├── gcp-storage.js
│   │   ├── helper.js
│   │   ├── password-policy.js
│   │   └── rest-helper.js
│   ├── validations/            # Input validation schemas (Joi)
│   │   └── joi/
│   │       ├── auth.js
│   │       ├── custom-incentive.js
│   │       ├── incentive.js
│   │       ├── index.js
│   │       └── role.js
│   └── workers/                # Worker processes for background tasks
│       ├── incentiveWorker.bootstrap.js
│       └── incentiveWorker.js
├── swagger.js                  # Swagger/OpenAPI documentation configuration
├── tests/                      # Unit and integration tests
│   ├── controllers/
│   └── services/
└── worker/                     # Separate worker application entry point
    ├── index.js
    ├── jobs/                   # Worker job implementations
    │   ├── bullmqWorkerApi.js
    │   ├── bullmqWorkerCron.js
    │   ├── incentiveCalculation.js
    │   ├── kittyAutoApproval.js
    │   └── kittyExpiry.js
    └── utils/                  # Worker-specific utilities
        └── index.js
```# Architectural Design Report: sales-backend

## 1. Project Overview

*   **Project Name:** sales-backend
*   **Framework:** Express (Node.js)
*   **Database Technologies:** MySQL, PostgreSQL, Redis
*   **ORM:** Sequelize
*   **Project Path:** `/home/acer/Downloads/crewai-developer-copilot/projects/sales-backend`
*   **Scanned At:** 2026-06-22 09:23:05

**FACT:** The project is a Node.js application built with the Express framework, utilizing Sequelize as an ORM to interact with MySQL and PostgreSQL databases. Redis is also used, likely for caching or queueing.

## 2. System's Structural Pattern

**INFERENCE:** The `sales-backend` project exhibits a **Layered Architecture** with strong characteristics of a **Service Layer Pattern** and elements of a **Repository Pattern**, which is a common evolution of the traditional **Model-View-Controller (MVC)** pattern in API-centric applications.

The core layers identified are:
*   **Presentation/API Layer:** Handled by Express routes and controllers.
*   **Application/Business Logic Layer:** Encapsulated within services.
*   **Data Access Layer:** Managed by Sequelize models and explicit repositories.
*   **Cross-Cutting Concerns:** Implemented through middlewares and utility modules.

## 3. Directory Layout

**FACT (derived from file paths in dependencies and routes):** The project follows a well-organized directory structure, primarily under the `src/` folder, with clear separation of concerns.



## 4. Request Lifecycle

**INFERENCE:** The request lifecycle in the `sales-backend` application, from an incoming HTTP request to database interaction, generally follows these steps:

1.  **Entry Point (`app.js` -> `src/server.js`):**
    *   The `app.js` file likely initializes the Express application and imports `src/server.js`.
    *   `src/server.js` sets up the main Express application, including global middlewares, logging (`src/config/logger.js`), and mounts the API routes. It also integrates Swagger for API documentation (`swagger.js`) and BullMQ for queue monitoring (`src/metrics/bullBoard.js`).

2.  **Routing (`src/routes/v1/index.js` and specific route files):**
    *   Incoming requests are matched against defined routes in `src/routes/v1/index.js` and its imported sub-route files (e.g., `src/routes/v1/auth.route.js`, `src/routes/v1/incentive.route.js`).
    *   **FACT:** Routes like `/api/v1/push-notifications` (POST) are handled by `createPushNotification` and use middlewares such as `validateJWT` and `upload.single("image")`.

3.  **Middleware Processing (`src/middlewares/`):**
    *   Before reaching the controller, requests pass through various middlewares.
    *   **FACT:** Common middlewares observed include:
        *   `auth.js` / `authCfMiddleware.js`: For authentication and authorization (`validateJWT`).
        *   `file-upload.js`: For handling file uploads.
        *   `validate-json.js`: For validating request bodies against Joi schemas.
        *   `fileOperationRateLimit`, `handleObjectTypes`: Custom middlewares for specific operations.
    *   **INFERENCE:** These middlewares handle cross-cutting concerns like authentication, input validation, and file processing, ensuring that the request is properly formatted and authorized before reaching the core business logic.

4.  **Controller Execution (`src/controllers/`):**
    *   Once middlewares are processed, the request is dispatched to the appropriate controller function (e.g., `createPushNotification` in `src/controllers/push-notification.controller.js`).
    *   **INFERENCE:** Controllers are responsible for:
        *   Parsing request parameters, body, and headers.
        *   Delegating business operations to one or more services.
        *   Handling potential errors from services.
        *   Formatting the response using `src/response/response.js` or `src/response/errorResponse.js`.

5.  **Service Layer Interaction (`src/services/`):**
    *   **INFERENCE:** Services encapsulate the application's business logic. A controller calls a service method (e.g., `push-notification.service.js` for push notifications).
    *   **FACT:** Services often depend on other services (e.g., `bill-processor.service.js` depends on `additional-incentive.service.js`, `custom-incentive.service.js`, `incentive-kitty.service.js`, `incentive.service.js`, `sales-target.service.js`).
    *   **INFERENCE:** Services orchestrate complex operations, apply business rules, and interact with the data access layer.

6.  **Data Access Layer (Models/Repositories - `src/models/`, `src/repo/`):**
    *   **INFERENCE:** Services interact with the database primarily through Sequelize models defined in `src/models/index.js`.
    *   **FACT:** `src/models/index.js` depends on `src/config/sequelize.js`, indicating that Sequelize is configured here to manage database connections and ORM.
    *   **FACT:** The presence of `src/repo/push-notification.repo.js` suggests that for some entities, a **Repository Pattern** is explicitly used, abstracting the data storage details from the services. This allows services to interact with a consistent interface regardless of the underlying data source.

7.  **Response:**
    *   The result from the service/data layer is returned to the controller.
    *   The controller then constructs an appropriate HTTP response using the standardized response utilities (`src/response/response.js` for success, `src/response/errorResponse.js` for errors) and sends it back to the client.

## 5. Framework Configuration

**FACT:**
*   **Express:** The core web framework, configured in `src/server.js` to handle routes, middlewares, and start the HTTP server.
*   **Sequelize:** The ORM for MySQL and PostgreSQL, configured in `src/config/sequelize.js`, which is then used by `src/models/index.js` to define and manage database models.
*   **Redis:** Configured in `src/config/redis.js`, used for queueing (BullMQ) and potentially caching or session management.
*   **Joi:** Used for request payload validation, with schemas defined in `src/validations/joi/`.
*   **BullMQ:** Used for background job processing, with queues defined in `src/queues/incentiveQueue.js` and workers in `src/workers/` and `worker/jobs/`.
*   **Swagger:** Integrated via `swagger.js` for API documentation.
*   **Logger:** Configured in `src/config/logger.js`.
*   **Environment Variables:** Managed via `environments/index.js`.

## 6. Key Architecture Patterns Used

**INFERENCE:**

*   **Layered Architecture:** The clear separation into presentation (routes, controllers), business logic (services), and data access (models, repositories) layers.
*   **Service Layer Pattern:** Services (`src/services/`) encapsulate the business logic, providing a clean API for controllers and orchestrating interactions with multiple data sources or other services. This promotes reusability and maintainability of business rules.
*   **Repository Pattern:** Evident in `src/repo/push-notification.repo.js`, this pattern abstracts the data access logic, making the application independent of the specific ORM or database technology. Services interact with repositories, not directly with models or raw database queries.
*   **Middleware Pattern:** Extensively used in Express (`src/middlewares/`) for handling cross-cutting concerns such as authentication (`auth.js`), validation (`validate-json.js`), error handling (`common-error-handler.js`), and file uploads (`file-upload.js`). This promotes modularity and reusability of these concerns.
*   **Asynchronous Messaging/Queueing (BullMQ):** The presence of `src/queues/incentiveQueue.js`, `src/workers/`, and `worker/jobs/` indicates the use of message queues for handling long-running or background tasks (e.g., incentive calculations, kitty auto-approval, kitty expiry). This improves responsiveness of the API and enables scalable processing of jobs.
*   **Configuration Management:** Dedicated `environments/` and `src/config/` directories for managing application settings, database connections, and external service configurations.
*   **API Versioning:** The `src/routes/v1/` directory structure suggests that API endpoints are versioned, allowing for easier evolution and maintenance of the API.
*   **Centralized Error Handling:** `src/middlewares/common-error-handler.js` and `src/response/errorResponse.js` indicate a centralized approach to handling and formatting errors consistently across the API.
*   **Input Validation:** Use of Joi schemas in `src/validations/joi/` and `src/middlewares/validate-json.js` ensures that incoming data conforms to expected formats and constraints.