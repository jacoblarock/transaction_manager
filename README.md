# transaction_manager

A REST API for managing shared group expenses. Users can create groups, log
transactions (shared expenses), record payments between users, and calculate
how to settle outstanding balances.

## API Spec

All endpoints are `GET` requests with query string parameters.

### Healthcheck

| | |
|---|---|
| `GET /api/` | Returns `200` if the service is running. |

### Authentication & Users

#### Authenticate

```
GET /api/authenticate?user=<username>&passHash=<password_hash>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `user` | string | yes |
| `passHash` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | Session token (string) |
| 400 | `user not found` / `password does not match` / `invalid request format` |

#### Auth Check

```
GET /api/auth_check?token=<session_token>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `no token provided` / `session not found` |

#### Create Invite Token

Generates a new invite token. Requires an authenticated session.

```
GET /api/create_invite_token?token=<session_token>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | Invite token (string) |
| 400 | `no token provided` / `invalid token` |

#### Create User from Invite Token

```
GET /api/create_user_from_invite_token?token=<invite_token>&user=<username>&passHash=<password_hash>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `user` | string | yes |
| `passHash` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid invite token` / `user with username already exists` / `invalid request format` |

#### Get User ID

Returns the user ID for a given username. Requires an authenticated session.

```
GET /api/get_user_id?token=<session_token>&user=<username>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `user` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | User ID (int) |
| 400 | `user not found` / `invalid request format` |

### Groups

#### Get Groups

Returns all groups the authenticated user belongs to.

```
GET /api/get_groups?token=<session_token>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | JSON array of `[{"g_id": int, "g_name": string}, ...]` |
| 400 | `no token provided` |

#### Get Group Users

Returns the users (IDs and names) in a group. The caller must be a member.

```
GET /api/get_group_users?token=<session_token>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | JSON array of `[{"u_id": int, "u_name": string}, ...]` |
| 400 | `invalid id` / `invalid request format` |

Returns `[]` if the caller is not a member of the group.

#### Create Group

Creates a new group and adds the authenticated user to it.

```
GET /api/create_group?token=<session_token>&name=<group_name>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `name` | string | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | Group ID (int) |
| 400 | `invalid request format` |

#### Delete Group

Deletes a group and all its user mappings. The caller must be a member.

```
GET /api/delete_group?token=<session_token>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid group id` / `invalid request format` |
| 403 | `user not in group` |

#### Add User to Group

Adds a user to a group. The caller must be a member of the group.

```
GET /api/add_user_to_group?token=<session_token>&userId=<user_id>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `userId` | int | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `user_group_map` row ID (int) |
| 400 | `invalid token` / `invalid id` / `user already in group` / `invalid request format` |
| 403 | `calling user not in group` |

#### Remove User from Group

Removes a user from a group. The caller must be a member of the group.

```
GET /api/remove_user_from_group?token=<session_token>&userId=<user_id>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `userId` | int | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid token` / `invalid id` / `user not in group` / `invalid request format` |
| 403 | `calling user not in group` |

### Transactions

Transactions are shared expenses paid by a single user on behalf of the group.
The cost is split evenly across all group members.

#### Create Transaction

```
GET /api/create_transaction?token=<session_token>&groupId=<group_id>&name=<name>&amount=<amount>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |
| `name` | string | yes |
| `amount` | float | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | Transaction ID (int) |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

#### Get Transactions

Returns all transactions in a group.

```
GET /api/get_transactions?token=<session_token>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | JSON array of transactions |
| 400 | `invalid id` / `invalid request format` |

Transaction object:

```json
{
  "t_id": 1,
  "t_u_ref": 1,
  "t_name": "dinner",
  "t_g_ref": 1,
  "t_amount": "60.00",
  "t_created_at": "Sat, 05 Sep 2026 10:11:06 GMT"
}
```

#### Update Transaction

Updates the name and amount of a transaction. The caller must be in the
transaction's group.

```
GET /api/update_transaction?token=<session_token>&transactionId=<transaction_id>&name=<name>&amount=<amount>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `transactionId` | int | yes |
| `name` | string | yes |
| `amount` | float | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

#### Delete Transaction

Deletes a transaction. The caller must be in the transaction's group.

```
GET /api/delete_transaction?token=<session_token>&transactionId=<transaction_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `transactionId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

### Payments

Payments are direct transfers from one user to another within a group.

#### Create Payment

```
GET /api/create_payment?token=<session_token>&groupId=<group_id>&recipientId=<user_id>&amount=<amount>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |
| `recipientId` | int | yes |
| `amount` | float | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | Payment ID (int) |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

#### Get Payments

Returns all payments in a group.

```
GET /api/get_payments?token=<session_token>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | JSON array of payments |
| 400 | `invalid id` / `invalid request format` |

Payment object:

```json
{
  "p_id": 1,
  "p_u_sender": 3,
  "p_u_recipient": 1,
  "p_g_ref": 1,
  "p_amount": "10.00",
  "p_created_at": "Sat, 05 Sep 2026 10:11:07 GMT"
}
```

#### Update Payment

Updates the amount of a payment. The caller must be in the payment's group.

```
GET /api/update_payment?token=<session_token>&paymentId=<payment_id>&amount=<amount>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `paymentId` | int | yes |
| `amount` | float | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

#### Delete Payment

Deletes a payment. The caller must be in the payment's group.

```
GET /api/delete_payment?token=<session_token>&paymentId=<payment_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `paymentId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | `success` |
| 400 | `invalid id` / `invalid request format` |
| 403 | `user not in group` |

### Settlement

#### Settle Balances

Calculates the minimum set of payments required to balance the group's
budget. Takes into account all transactions (split evenly) and existing
payments between members.

```
GET /api/settle?token=<session_token>&groupId=<group_id>
```

| Parameter | Type | Required |
|-----------|------|----------|
| `token` | string | yes |
| `groupId` | int | yes |

**Responses**

| Status | Body |
|--------|------|
| 200 | JSON array of transfers |
| 400 | `invalid id` / `invalid request format` |

Transfer object:

```json
[
  {"from": 3, "to": 1, "amount": 10.0},
  {"from": 2, "to": 1, "amount": 5.0}
]
```

| Field | Description |
|-------|-------------|
| `from` | User ID that owes the payment |
| `to` | User ID that receives the payment |
| `amount` | Positive amount to transfer |

Returns `[]` if the caller is not in the group or if all balances are
already settled.