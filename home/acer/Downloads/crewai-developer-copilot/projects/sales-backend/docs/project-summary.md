

# Project Summary: Sales Backend

## Executive Project Summary
The `sales-backend` is a robust Node.js/Express-based service designed to manage core sales operations, including order processing, inventory tracking, and customer management. The system is built for scalability, utilizing a relational database for transactional integrity and Redis for caching performance.

## System Architecture & Tech Stack
- **Runtime:** Node.js
- **Framework:** Express.js
- **Database Layer:** 
    - **Primary:** PostgreSQL (Transactional data) / MySQL (Legacy/Secondary)
    - **ORM:** Sequelize
    - **Caching:** Redis
- **Architecture Pattern:** Layered architecture (Controller-Service-Repository pattern).

## Primary Database Models and Relationships
- **User:** Manages authentication and role-based access.
- **Order:** Central entity linked to `User` (One-to-Many) and `Product` (Many-to-Many via `OrderItems`).
- **Product:** Manages inventory levels and pricing.
- **Inventory:** Tracks stock movements and warehouse locations.

## Core API Routes & Validations
- **Authentication:** `/api/v1/auth/*` (JWT-based, validation via Joi/Express-Validator).
- **Orders:** `/api/v1/orders/*` (Requires authentication, validates stock availability before creation).
- **Products:** `/api/v1/products/*` (Public read access, restricted write access).

## Key Business Logic & Side Effects
- **Order Placement:** Triggers an inventory decrement side effect. If inventory is insufficient, the transaction is rolled back via Sequelize transactions.
- **Caching:** Product listings are cached in Redis with a TTL of 3600 seconds to reduce database load.
- **Notifications:** Order creation events emit an asynchronous event to the notification service.

## Refactoring and Coupling Warnings
- **Tight Coupling:** The `OrderService` is currently tightly coupled with the `InventoryService`. It is recommended to decouple these using an Event Emitter or Message Queue (e.g., RabbitMQ/BullMQ) to improve system resilience.
- **Database Migrations:** Ensure all Sequelize migrations are tested in a staging environment before deployment, as some legacy MySQL tables have complex constraints that may cause downtime during schema updates.
- **Error Handling:** Centralized error handling middleware is implemented but requires more granular logging for production debugging.