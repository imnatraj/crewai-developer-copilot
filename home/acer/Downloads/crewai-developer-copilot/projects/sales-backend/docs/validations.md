# Input Security and Validation Audit Report

This report provides a comprehensive audit of the API input validation layer. It maps existing validation schemas to their respective routes and identifies critical gaps in security coverage.

## Validation Matrix

| Route Path | Method | Handler | Validation Schema | Status |
| :--- | :--- | :--- | :--- | :--- |
| `/auth` | USE | `authRoute` | `authSchema` | FACT |
| `/incentive` | USE | `incentiveRoute` | `incentiveSchema` | FACT |
| `/custom-incentive` | USE | `customIncentiveRoute` | `customIncentiveSchema` | FACT |
| `/user-roles` | USE | `userRolesRoute` | `roleSchema` | FACT |
| `/` | POST | `addPageAccess` | None | **MISSING** |
| `/reset-password` | POST | `resetUserDefaultPassword` | None | **MISSING** |
| `/:id` | PUT | `updateUserById` | None | **MISSING** |
| `/` | POST | `createPushNotification` | None | **MISSING** |
| `/:id` | PUT | `updatePushNotificationCtl` | None | **MISSING** |
| `/process-bill/:billNo` | POST | `processBill` | None | **MISSING** |
| `/create` | POST | `createmopIncentive` | None | **MISSING** |
| `/` | POST | `createRole` | None | **MISSING** |
| `/:id` | PUT | `updateRole` | None | **MISSING** |

---

## Validation Shape Mapping

| Schema Name | Fields | Rules (Inferred/Explicit) |
| :--- | :--- | :--- |
| **authSchema** | `email`, `password`, `empId`, `mobile` | String format, Auth-specific objects |
| **incentiveSchema** | `startDate`, `endDate`, `branch`, `item_code` | Date, String, Numeric types |
| **customIncentiveSchema** | `percentage`, `split`, `start_date`, `end_date` | Number, Array, String |
| **roleSchema** | `role_name`, `role_id`, `status` | String, Number, Boolean |

---

## Security Audit Findings

### 1. Missing Validations (Critical)
The following routes perform state-changing operations (POST/PUT/DELETE) but lack explicit validation schemas. This exposes the application to mass-assignment vulnerabilities, type-confusion attacks, and injection risks.

*   **`POST /reset-password`**: No schema validation for password complexity or user identification.
*   **`POST /process-bill/:billNo`**: The `billNo` parameter and request body are unvalidated.
*   **`POST /create` (Incentive/Role)**: Missing schema validation for creation payloads.
*   **`PUT /:id` (User/Role/Page)**: Missing validation for update payloads, increasing risk of unauthorized data modification.

### 2. Inconsistent Middleware Usage
*   **FACT**: Several routes (e.g., `downloadKittyConfigs`, `uploadIncentives`) utilize `fileOperationRateLimit` or `customFileUpload`, which provides some level of input control.
*   **INFERENCE**: Many routes rely solely on `validateJWT` for security. While this handles authentication, it does **not** validate the structure or content of the request body, which is a common oversight in API security.

### 3. Recommendations
1.  **Implement Schema Enforcement**: Every `POST`, `PUT`, and `PATCH` route must be wrapped in a validation middleware (e.g., `validate(schema)`) that enforces strict typing and sanitization.
2.  **Parameter Validation**: Routes using path parameters (e.g., `/:id`, `/:billNo`) should validate that the parameter matches the expected format (e.g., UUID, numeric ID) before reaching the controller.
3.  **Centralize Validation**: Move all validation logic into a dedicated middleware layer to ensure consistency across the `/api/v1` namespace.