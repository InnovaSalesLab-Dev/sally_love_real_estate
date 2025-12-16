# BoldTrail API V2 - Complete Endpoint Reference

**Base URL:** `https://api.kvcore.com`  
**Documentation:** https://developer.insiderealestate.com/publicv2/reference

---

## 🔗 ENDPOINTS USED IN THIS PROJECT

The following endpoints are **actively used** in the Sally Love Real Estate AI Concierge project:

| # | Endpoint Name | Method | Path | Reference URL | Used In |
|---|---------------|--------|------|---------------|---------|
| 1 | **Create New Contact** | `POST` | `/v2/public/contact` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact) | `create_buyer_lead()`, `create_seller_lead()` - **Same endpoint, different `deal_type`** |
| 2 | **Get Contact Details** | `GET` | `/v2/public/contact/{contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id) | `get_contact()` |
| 3 | **Get Contacts List** | `GET` | `/v2/public/contacts` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contacts) | `search_contacts()` |
| 4 | **Update Contact** | `PUT` | `/v2/public/contact/{contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id) | `update_contact()` |
| 5 | **Add a Note** | `PUT` | `/v2/public/contact/{contact-id}/action/note` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-note) | `add_note()` |
| 6 | **Log a Call** | `PUT` | `/v2/public/contact/{contact-id}/action/call` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-call) | `log_call()` |
| 7 | **Get User List** | `GET` | `/v2/public/users` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-users) | `get_agents()` |
| 8 | **Get User Details** | `GET` | `/v2/public/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id) | `get_agent()` |

### Additional Data Source

| Resource | Type | URL Format | Used In |
|----------|------|------------|---------|
| **XML Listings Feed** | Data Feed | `https://api.kvcore.com/export/listings/{ZAPIER_KEY}/10` | `search_listings_from_xml()` |

**Note:** The XML listings feed is used for property searches as an alternative to the Manual Listings API endpoint.

---

## 🎯 SALLY LOVE PROJECT - PRIORITY ENDPOINTS

These are the **essential endpoints** needed for the Sally Love Real Estate AI Concierge project.

### ⭐ CRITICAL (Must Have)

| Endpoint Name | Method | Path | Purpose |
|--------------|--------|------|---------|
| **Get Manual Listings List** | `GET` | `/v2/public/manuallistings` | Search properties by address |
| **Create New Contact** | `POST` | `/v2/public/contact` | Create buyer/seller leads |
| **Log a Call** | `PUT` | `/v2/public/contact/{contact-id}/action/call` | Log call activities |
| **Get User Details** | `GET` | `/v2/public/user/{user-id}` | Get agent phone for transfers |
| **Get User List** | `GET` | `/v2/public/users` | Search agents by name |

### ⭐ RECOMMENDED (Enhanced Functionality)

| Endpoint Name | Method | Path | Purpose |
|--------------|--------|------|---------|
| **Add a Note** | `PUT` | `/v2/public/contact/{contact-id}/action/note` | Add detailed lead notes |
| **Get Manual Listing Details** | `GET` | `/v2/public/manuallisting/{manual-listing-id}` | Get specific listing |
| **Get Contact Details** | `GET` | `/v2/public/contact/{contact-id}` | Verify existing contacts |
| **Update Contact** | `PUT` | `/v2/public/contact/{contact-id}` | Update lead information |

---

## 📚 COMPLETE ENDPOINT CATALOG

### 1. Create & Update Offices

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Create Office | `POST` | `/v2/public/office` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-office) |
| Update Office | `PUT` | `/v2/public/office/{office-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-office-office-id) |
| Remove Office | `DELETE` | `/v2/public/office/{office-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-office-office-id) |
| Get Office Details | `GET` | `/v2/public/office/{office-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-office-office-id) |
| Get Office List | `GET` | `/v2/public/offices` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-offices) |
| Add User to Office | `POST` | `/v2/public/office/{office-id}/user` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-office-office-id-user) |
| Update Users Existing Office | `PUT` | `/v2/public/office/{office-id}/user` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-office-office-id-user) |
| Remove User from Office | `DELETE` | `/v2/public/office/{office-id}/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-office-office-id-user-user-id) |

---

### 2. Create & Update Teams

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Create Team | `POST` | `/v2/public/team` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-team) |
| Update Team | `PUT` | `/v2/public/team/{team-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-team-team-id) |
| Remove Team | `DELETE` | `/v2/public/team/{team-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-team-team-id) |
| Get Team Details | `GET` | `/v2/public/team/{team-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-team-team-id) |
| Get Team List | `GET` | `/v2/public/teams` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-teams) |
| Add User to Team | `POST` | `/v2/public/team/{team-id}/user` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-team-team-id-user) |
| Remove User from Team | `DELETE` | `/v2/public/team/{team-id}/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-team-team-id-user-user-id) |

---

### 3. Create & Update Users ⭐

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| **Get User Details** ⭐ | `GET` | `/v2/public/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id) |
| **Get User List** ⭐ | `GET` | `/v2/public/users` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-users) |
| Create User | `POST` | `/v2/public/user` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-user) |
| Update User | `PUT` | `/v2/public/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-user-user-id) |
| Remove User | `DELETE` | `/v2/public/user/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-user-user-id) |
| Get User Extended Details | `GET` | `/v2/public/user/{user-id}/ext` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-ext) |
| Update User Extended Detail | `PUT` | `/v2/public/user/{user-id}/ext` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-user-user-id-ext) |
| Get Vacation Information | `GET` | `/v2/public/user/{user-id}/vacation` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-vacation) |
| Update Vacation Information | `PUT` | `/v2/public/user/{user-id}/vacation` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-user-user-id-vacation) |
| Get User Website | `GET` | `/v2/public/user/{user-id}/website` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-website) |
| Get Entities | `GET` | `/v2/public/user/{user-id}/entities` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-entities) |
| Get User Tasks | `GET` | `/v2/public/user/{user-id}/tasks` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-tasks) |
| Get User Calls | `GET` | `/v2/public/user/{user-id}/calls` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-calls) |
| Get User Pipeline | `GET` | `/v2/public/user/{user-id}/pipeline` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-pipeline) |
| Get Agent Success Course Status | `GET` | `/v2/public/user/{user-id}/agent-success` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-user-id-agent-success) |
| Get Users to be deleted in future | `GET` | `/v2/public/user/upcoming-deleted` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-upcoming-deleted) |
| Set Future User Deletion Date | `POST` | `/v2/public/user/upcoming-deleted` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-user-upcoming-deleted) |
| Get All Languages | `GET` | `/v2/public/languages` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-languages) |
| Get All User Spoken Languages | `GET` | `/v2/public/user/languages/{user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-user-languages-user-id) |
| Update User Spoken Languages | `POST` | `/v2/public/user/languages` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-user-languages) |
| Delete User Spoken Language | `DELETE` | `/v2/public/user/languages` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-user-languages) |

---

### 4. Listing Management ⭐

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| **Get Manual Listings List** ⭐ | `GET` | `/v2/public/manuallistings` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallistings) |
| **Get Manual Listing Details** ⭐ | `GET` | `/v2/public/manuallisting/{manual-listing-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallisting-manual-listing-id) |
| Add Manual Listing | `POST` | `/v2/public/manuallisting` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-manuallisting) |
| Update Manual Listing | `PUT` | `/v2/public/manuallisting/{manual-listing-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-manuallisting-manual-listing-id) |
| Remove Manual Listing | `DELETE` | `/v2/public/manuallisting/{manual-listing-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-manuallisting-manual-listing-id) |
| Get Manual Listing Property Types | `GET` | `/v2/public/manuallisting/propertytypes` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-manuallisting-propertytypes) |

---

### 5. Open Houses

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get All Open Houses In Date Range | `GET` | `/v2/public/openhouse` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-openhouse) |
| Get All Contacts From Open House by Hashtag | `GET` | `/v2/public/openhouse/contacts` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-openhouse-contacts) |

---

### 6. Contact Management ⭐

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| **Create New Contact** ⭐ | `POST` | `/v2/public/contact` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact) |
| **Get Contact Details** ⭐ | `GET` | `/v2/public/contact/{contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id) |
| **Update Contact** ⭐ | `PUT` | `/v2/public/contact/{contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id) |
| **Add a Note** ⭐ | `PUT` | `/v2/public/contact/{contact-id}/action/note` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-note) |
| **Log a Call** ⭐ | `PUT` | `/v2/public/contact/{contact-id}/action/call` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-call) |
| Get Contacts List | `GET` | `/v2/public/contacts` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contacts) |
| Remove Contact | `DELETE` | `/v2/public/contact/{contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-contact-contact-id) |
| Get Notes List | `GET` | `/v2/public/contact/{contact-id}/action/note` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-action-note) |
| Get Note Details | `GET` | `/v2/public/contact/{contact-id}/action/note/{action-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-action-note-action-id) |
| Update a Note | `PUT` | `/v2/public/contact/{contact-id}/action/note/{action-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-note-action-id) |
| Get Calls List | `GET` | `/v2/public/contact/{contact-id}/action/call` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-action-call) |
| Get Call Details | `GET` | `/v2/public/contact/{contact-id}/action/call/{action-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-action-call-action-id) |
| Update a Call | `PUT` | `/v2/public/contact/{contact-id}/action/call/{action-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-action-call-action-id) |
| Get Listing Views | `GET` | `/v2/public/contact/{contact-id}/listingviews` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-listingviews) |
| Get Market Reports | `GET` | `/v2/public/contact/{contact-id}/marketreport` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-marketreport) |
| Get Tag List | `GET` | `/v2/public/contact/{contact-id}/tags` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-tags) |
| Add Tags to Contact | `PUT` | `/v2/public/contact/{contact-id}/tags` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-tags) |
| Remove Tags from Contact | `DELETE` | `/v2/public/contact/{contact-id}/tags` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-contact-contact-id-tags) |
| Send Email to Contact | `PUT` | `/v2/public/contact/{contact-id}/email` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-email) |
| Send Text to Contact | `PUT` | `/v2/public/contact/{contact-id}/text` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-text) |
| Schedule a Call | `POST` | `/v2/public/schedule/call` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-schedule-call) |
| Ask a Question | `POST` | `/v2/public/{contactid}/question` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contactid-question) |
| Showing Request | `POST` | `/v2/public/contact/{contactid}/appointment` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact-contactid-appointment) |
| Add Listing View | `POST` | `/v2/public/views` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-views) |

---

### 7. Contact Listing Search Alerts

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get Contact Search Alert | `GET` | `/v2/public/contact/{contact-id}/searchalert` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-searchalert) |
| Add Search Alert to Contact | `POST` | `/v2/public/contact/{contact-id}/searchalert` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact-contact-id-searchalert) |
| Update Contact Search Alert | `PUT` | `/v2/public/contact/{contact-id}/searchalert/{searchalertnumber}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-contact-contact-id-searchalert-searchalertnumber) |
| Delete Contact Search Alert | `DELETE` | `/v2/public/contact/{contact-id}/searchalert/{searchalertnumber}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-contact-contact-id-searchalert-searchalertnumber) |
| Send Search Alert Results to Contact | `POST` | `/v2/public/contact/{contact-id}/searchalert/{searchalertnumber}` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-contact-contact-id-searchalert-searchalertnumber) |
| Get Search Alert Recent Results | `GET` | `/v2/public/contact/{contact-id}/searchalert/{searchalertnumber}/results` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-contact-contact-id-searchalert-searchalertnumber-results) |

---

### 8. Super Account Management

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Sync scheduled email to all child accounts | `POST` | `/superaccount/scheduledemails/sync` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_superaccount-scheduledemails-sync) |
| Delete synced email from all child accounts | `DELETE` | `/superaccount/scheduledemails/sync` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_superaccount-scheduledemails-sync) |
| Sync scheduled email to specific users | `POST` | `/superaccount/scheduledemails/sync-to-users` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_superaccount-scheduledemails-sync-to-users) |
| Get User List | `GET` | `/v2/public/superaccount/users` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-superaccount-users) |
| Get Accounts List | `GET` | `/v2/public/superaccount/accounts` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-superaccount-accounts) |
| Get Entities | `GET` | `/v2/public/superaccount/entities` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-superaccount-entities) |
| Refresh Campaigns | `PUT` | `/v2/public/superaccount/campaigns/refresh` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-superaccount-campaigns-refresh) |
| Refresh Templates | `PUT` | `/v2/public/superaccount/templates/refresh` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-superaccount-templates-refresh) |
| Transfer Contact | `PUT` | `/v2/public/superaccount/transfer/contact` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-superaccount-transfer-contact) |
| Archive Contact | `POST` | `/v2/public/superaccount/contacts/archive` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-superaccount-contacts-archive) |
| Delete Contacts | `DELETE` | `/v2/public/superaccount/contacts/delete` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-superaccount-contacts-delete) |
| Get Users on Vacation | `GET` | `/v2/public/superaccount/vacations/all` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-superaccount-vacations-all) |

---

### 9. Create & Update Transaction Users

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get list of User/Transaction relationships | `GET` | `/v2/public/transaction/users` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transaction-users) |
| Get a specific User/Transaction relationship | `GET` | `/v2/public/transaction/user/{transaction-user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transaction-user-transaction-user-id) |
| Update the User/Transaction relationship | `PUT` | `/v2/public/transaction/user/{transaction-user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-transaction-user-transaction-user-id) |
| Delete a User From Transaction | `DELETE` | `/v2/public/transaction/user/{transaction-user-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-transaction-user-transaction-user-id) |
| Add User to a Transaction | `POST` | `/v2/public/transaction/user` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-transaction-user) |

---

### 10. Create & Update Transaction Contacts

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get a list of Contacts/Transactions Relationships | `GET` | `/v2/public/transaction/contacts` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transaction-contacts) |
| Get a specific Contact/Transaction Relationship | `GET` | `/v2/public/transaction/contact/{transaction-contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transaction-contact-transaction-contact-id) |
| Update the Contact/Transaction relationship | `PUT` | `/v2/public/transaction/contact/{transaction-contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-transaction-contact-transaction-contact-id) |
| Delete a Contact From Transaction | `DELETE` | `/v2/public/transaction/contact/{transaction-contact-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-transaction-contact-transaction-contact-id) |
| Add Contact to a Transaction | `POST` | `/v2/public/transaction/contact` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-transaction-contact) |

---

### 11. Create & Update Transactions

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get Transaction List | `GET` | `/v2/public/transactions` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transactions) |
| Get a Transaction | `GET` | `/v2/public/transaction/{transaction-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-transaction-transaction-id) |
| Update a Transaction | `PUT` | `/v2/public/transaction/{transaction-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-transaction-transaction-id) |
| Delete a Transaction | `DELETE` | `/v2/public/transaction/{transaction-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-transaction-transaction-id) |
| Create a Transaction | `POST` | `/v2/public/transaction` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-transaction) |

---

### 12. Website and Testimonial Management

| Endpoint Name | Method | Path | Documentation URL |
|--------------|--------|------|-------------------|
| Get All Testimonials | `GET` | `/v2/public/website/{website-id}/testimonials` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-website-website-id-testimonials) |
| Get Testimonial | `GET` | `/v2/public/testimonial/{testimonial-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-testimonial-testimonial-id) |
| Update Testimonial by ID | `PUT` | `/v2/public/testimonial/{testimonial-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/put_v2-public-testimonial-testimonial-id) |
| Delete Testimonial | `DELETE` | `/v2/public/testimonial/{testimonial-id}` | [Link](https://developer.insiderealestate.com/publicv2/reference/delete_v2-public-testimonial-testimonial-id) |
| Create Testimonial | `POST` | `/v2/public/testimonial` | [Link](https://developer.insiderealestate.com/publicv2/reference/post_v2-public-testimonial) |
| Get Team Website | `GET` | `/v2/public/website/team/{teamid}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-website-team-teamid) |
| Get Office Website | `GET` | `/v2/public/website/office/{officeid}` | [Link](https://developer.insiderealestate.com/publicv2/reference/get_v2-public-website-office-officeid) |

---

## 📝 AUTHENTICATION

All API requests require authentication using a Bearer token:

```bash
Authorization: Bearer {YOUR_API_TOKEN}
Content-Type: application/json
```

**Get API Token:** BoldTrail Account → Lead Engine → Lead Dropbox → Generate "All" API Token

---

## 🔗 QUICK REFERENCE - SALLY LOVE PROJECT ENDPOINTS

### Property Lookup
```bash
GET https://api.boldtrail.com/v2/public/manuallistings?address={address}&status=active
```

### Create Buyer/Seller Lead
```bash
POST https://api.boldtrail.com/v2/public/contact
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "352-555-1234",
  "email": "john@example.com",
  "lead_type": "Buyer",
  "status": "New"
}
```

### Log Call Activity
```bash
PUT https://api.boldtrail.com/v2/public/contact/{contact-id}/action/call
{
  "type": "Inbound",
  "subject": "Buyer Inquiry - AI Concierge",
  "duration": 180
}
```

### Get Agent Details for Transfer
```bash
GET https://api.boldtrail.com/v2/public/user/{user-id}
```

### Search Agents by Name
```bash
GET https://api.boldtrail.com/v2/public/users?search={agent_name}&role=agent
```

---

## ⚠️ IMPORTANT NOTES

1. **Listing Search Limitation:** Need to verify if `GET /v2/public/manuallistings` supports searching by address parameter. If not, use **BoldTrail XML Feed** as alternative:
   ```
   GET https://api.kvcore.com/export/listings/{ZAPIER_KEY}/10
   ```

2. **Rate Limits:** Check BoldTrail documentation for specific rate limit details.

3. **Error Handling:** Always implement proper error handling for API calls.

4. **Testing:** Test all endpoints in development environment before production deployment.

---

**Last Updated:** December 12, 2024  
**Project:** Sally Love Real Estate AI Concierge  
**Version:** BoldTrail API V2
