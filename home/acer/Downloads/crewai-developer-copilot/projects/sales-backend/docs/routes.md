# API Routing Documentation: Sales-Backend

This document provides a comprehensive overview of the API routes, controllers, and middleware configurations for the `sales-backend` project.

## 1. Overview
The API follows a versioned structure (`/api/v1`) and utilizes a Controller-Route pattern. All routes are defined within `src/routes/v1/` and mounted via `src/server.js`.

---

## 2. Global & System Routes

| Method | Path | Handler | Middlewares | File |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/` | (req, res) => { ... } | None | `src/server.js` |
| USE | `/api/v1` | v1Routes | None | `src/server.js` |
| USE | `/health` | healthRoute | None | `src/server.js` |
| USE | `/api-docs` | swaggerUi.setup | `swaggerUi.serve` | `swagger.js` |

---

## 3. Versioned API Endpoints (`/api/v1`)

### Bill Processing (`/sales`)
| Method | Path | Handler | Middlewares | File |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/download` | BillProcessorController.downloadBills | `handleObjectTypes` | `src/routes/v1/bill-processor.route.js` |
| POST | `/process-bill/:billNo` | BillProcessorController.processBill | None | `src/routes/v1/bill-processor.route.js` |
| POST | `/recalculation-bill` | BillProcessorController.recalculateBill | None | `src/routes/v1/bill-processor.route.js` |
| POST | `/reprocess-bill/` | BillProcessorController.processBill | None | `src/routes/v1/bill-processor.route.js` |
| GET | `/reprocess-bill-remarks` | BillProcessorController.listReprocessRemarks | None | `src/routes/v1/bill-processor.route.js` |
| POST | `/reprocess-bill-by-mode/` | BillProcessorController.reprocessBill | None | `src/routes/v1/bill-processor.route.js` |

### User Management (`/users`)
| Method | Path | Handler | Middlewares | File |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/` | getUsers | `validateJWT` | `src/routes/v1/user.route.js` |
| GET | `/:userId` | getUser | None | `src/routes/v1/user.route.js` |
| PUT | `/:id` | updateUserById | `validateJWT` | `src/routes/v1/user.route.js` |
| POST | `/reset-password` | resetUserDefaultPassword | `validateJWT` | `src/routes/v1/user.route.js` |

### Push Notifications (`/push-notifications`)
| Method | Path | Handler | Middlewares | File |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/` | createPushNotification | `validateJWT`, `upload.single("image")` | `src/routes/v1/push-notification.route.js` |
| GET | `/` | getAllPushNotificationsAll | `validateJWT` | `src/routes/v1/push-notification.route.js` |
| GET | `/:id` | getPushNotificationByIdCtl | `validateJWT` | `src/routes/v1/push-notification.route.js` |
| PUT | `/:id` | updatePushNotificationCtl | `validateJWT` | `src/routes/v1/push-notification.route.js` |
| PATCH | `/:id/status` | changePushNotificationStatusCtl | `validateJWT` | `src/routes/v1/push-notification.route.js` |
| PATCH | `/:id/read_status` | changeReadStatus | `validateJWT` | `src/routes/v1/push-notification.route.js` |

### Auto Approval (`/auto-approval`)
| Method | Path | Handler | Middlewares | File |
| :--- | :--- | :--- | :--- | :--- |
| GET | `/list` | AutoApprovalController.getAllRuleSets | `validateJWT` | `src/routes/v1/auto-approval.route.js` |
| POST | `/create` | AutoApprovalController.createRuleSet | `validateJWT` | `src/routes/v1/auto-approval.route.js` |
| PUT | `/modify` | AutoApprovalController.editRuleSet | `validateJWT` | `src/routes/v1/auto-approval.route.js` |
| DELETE | `/delete` | AutoApprovalController.deleteRuleSets | `validateJWT` | `src/routes/v1/auto-approval.route.js` |

---

## 4. Summary Table: Fact vs. Inference

| Feature | Type | Description |
| :--- | :--- | :--- |
| **Routing Structure** | FACT | Express Router used for modularizing routes in `src/routes/v1/`. |
| **Middleware** | FACT | `validateJWT` is the primary security layer for protected routes. |
| **File Handling** | FACT | `fileOperationRateLimit` is consistently applied to download/export endpoints. |
| **Controller Logic** | INFERENCE | Handlers like `BillProcessorController` suggest a class-based controller structure. |
| **Request Lifecycle** | INFERENCE | The `upload.single("image")` middleware implies the use of `multer` for multipart form data. |

*Note: This documentation is generated based on the project's route metadata. For specific business logic implementation, please refer to the corresponding controller files in `src/controllers/`.*