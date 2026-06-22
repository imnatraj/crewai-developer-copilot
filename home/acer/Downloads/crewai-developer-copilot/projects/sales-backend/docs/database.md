# Database Model, Relationships, and Data-Flow Documentation: `sales-backend`

This document outlines the database architecture for the `sales-backend` project, detailing the Sequelize models, schema definitions, and inferred data-flow paths.

---

## 1. FACT: Database Schema & Models

The application uses Sequelize as the ORM to interact with the database. Below are the primary entities identified in the system.

### Core Data Models

| Model Name | Table Name | Key Fields |
| :--- | :--- | :--- |
| **User** | `users` | `id`, `emp_id`, `email`, `role`, `password` |
| **SalesTarget** | `salestargets` | `target_id`, `sales_target_name`, `from_date`, `to_date` |
| **Incentive** | `incentives` | `id`, `item_code`, `model`, `sku`, `brand`, `mop_one`, `mop_two` |
| **KittyDetailsWarm** | `kittydetailswarms` | `id`, `mobile_no`, `item_code`, `price`, `approval_status` |
| **KittyRule** | `kittyrules` | `rule_id`, `rule_name`, `conditions_json`, `max_percentage_value` |
| **SalesCategory** | `salescategorys` | `id`, `name`, `code`, `group_id` |
| **IncentiveSaleData** | `incentivesaledatas` | `id`, `bill_transcation_no`, `item_code`, `item_net_amount` |

### Supporting & Configuration Models
*   **Access Control:** `PageAccess`, `Pages`, `UserRole`, `UserToken`.
*   **Kitty/Approval Logic:** `KittyConfig`, `StoreKittyConfig`, `KittyEmpConfig`, `KittyEmpMaxConfig`, `AutoApproval`, `KittyAutoApprovalHistory`, `KittyAutoApprovalOutcome`, `KittyApprovalRuleStats`, `KittyRuleProducts`, `KittyRuleAttribute`, `KittyRuleAuditHistory`.
*   **Incentive Logic:** `SalesIncentiveBreakdown`, `CustomIncentive`, `CustomIncentiveProduct`, `IncentiveSplit`, `IncentiveSaleErrorLog`.
*   **System/Utility:** `JobTracker`, `NatsMessageLog`, `Sequence`, `AccessoriesGrp`, `SalesProductMap`, `SalesTargetBreakdown`, `ExcludedItems`, `PushNotification`.

---

## 2. INFERENCE: Relationships & Validation

### Model Relationships (Inferred)
While explicit Sequelize associations are not defined in the provided metadata, the following logical relationships exist:
*   **One-to-Many:**
    *   `SalesTarget` (1) -> `SalesProductMap` (N)
    *   `SalesCategoryGroup` (1) -> `SalesCategory` (N)
    *   `KittyRule` (1) -> `KittyRuleProducts` (N)
    *   `User` (1) -> `UserToken` (N)
*   **Data Linking (Foreign Key Logic):**
    *   `IncentiveSaleData` and `SalesIncentiveBreakdown` are linked via `bill_transcation_no`.
    *   `KittyDetailsWarm` and `KittyDetailsCold` share similar structures, likely representing different stages of a workflow.

### Schema-Level Validation Constraints
*   **Data Integrity:** Fields like `status` (TINYINT/BOOLEAN) and `created_at`/`updated_at` (DATE) are ubiquitous, enforcing standard audit trails.
*   **JSON Storage:** Extensive use of `JSON` and `JSONB` types (e.g., in `KittyRule`, `KittyDetailsWarm`, `PageAccess`) indicates a flexible schema design for complex, evolving business rules.
*   **Enums:** Used for status tracking and type definition (e.g., `IncentiveSaleData.status`, `KittyRule.outcome_type`).

---

## 3. FACT: Migration History

The migration history is managed via JavaScript files in `src/migrations/`.

*   **Example Migration:** `incentive-split.js`
    *   **Action:** Creates the `public."incentive-split"` table.
    *   **Constraints:** Defines a primary key `incentive_split_pkey` on `id` and sets default values for `status`.
    *   **Type:** Uses `DOUBLE PRECISION` for incentive calculations, ensuring high precision for financial data.

---

## 4. INFERENCE: Data-Flow Paths

The data flows through the application in a standard MVC pattern:

1.  **Ingestion:** External data (e.g., bill transactions) enters via `NatsMessageLog` or API controllers.
2.  **Processing:**
    *   `Controllers` (e.g., `incentive.controller.js`) receive the request.
    *   `Services` (e.g., `bill-processor.service.js`) perform business logic, often querying `Incentive` or `KittyConfig` models.
3.  **Persistence:**
    *   Data is written to transactional tables like `IncentiveSaleData` or `KittyDetailsWarm`.
    *   Errors during processing are captured in `IncentiveSaleErrorLog`.
4.  **Audit/Tracking:** Changes to rules or approvals are logged in `KittyRuleAuditHistory` or `KittyAutoApprovalHistory`.

**Data Bottleneck:** `src/models/index.js` acts as the central gateway for all database operations, making it the primary point of contention for schema changes and performance tuning.