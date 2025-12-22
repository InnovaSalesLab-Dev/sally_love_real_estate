# Sally Love Voice Agent - Documentation Index

All project documentation is organized in this folder.

---

## 🚀 Getting Started

Start here if you're new to the project:

| Document | Description |
|----------|-------------|
| [START_HERE.md](getting-started/START_HERE.md) | Project overview and quick start guide |
| [README_TESTING.md](../scripts/README_TESTING.md) | Testing guide (in scripts folder) |
| [REQUIREMENTS.md](getting-started/REQUIREMENTS.md) | Business requirements and project scope |

---

## ⚙️ Configuration & Setup

Essential configuration documentation:

| Document | Description |
|----------|-------------|

| [SETTINGS_REFACTOR.md](configuration/SETTINGS_REFACTOR.md) | How configuration system works |
| [TEST_MODE_CONFIGURATION.md](configuration/TEST_MODE_CONFIGURATION.md) | Test mode setup and usage |

---

## 🎯 Feature Implementation

Documentation for specific features:

| Document | Description |
|----------|-------------|
| [OPTION_A_IMPLEMENTATION.md](features/OPTION_A_IMPLEMENTATION.md) | Lead notifications & fallback routing implementation |
| [MANUAL_LISTINGS_FALLBACK.md](features/MANUAL_LISTINGS_FALLBACK.md) | Manual listings fallback feature documentation |
| [MANUAL_LISTINGS_DEPLOYMENT_SUMMARY.md](features/MANUAL_LISTINGS_DEPLOYMENT_SUMMARY.md) | Manual listings deployment summary and testing guide |
| [MANUAL_LISTINGS_IMPLEMENTATION_COMPLETE.md](features/MANUAL_LISTINGS_IMPLEMENTATION_COMPLETE.md) | Complete manual listings implementation summary |
| [CLIENT_REQUIREMENTS_AUDIT.md](features/CLIENT_REQUIREMENTS_AUDIT.md) | Client requirements checklist and status |
| [TEST_1_FIXES_SUMMARY.md](features/TEST_1_FIXES_SUMMARY.md) | Test case fixes and improvements |

---

## 📞 Vapi Integration

Vapi AI voice assistant configuration:

| Document | Description |
|----------|-------------|
| [VAPI_SYSTEM_PROMPT_2.md](vapi/VAPI_SYSTEM_PROMPT_2.md) | **Current system prompt** (short, concise) |
| [VAPI_KNOWLEDGE_BASE.md](vapi/VAPI_KNOWLEDGE_BASE.md) | **Current knowledge base** (upload to Vapi) |
| [VAPI_SYSTEM_PROMPT.md](vapi/VAPI_SYSTEM_PROMPT.md) | Legacy system prompt (reference only) |
| [VAPI_TOOLS_CONFIGURATION.md](vapi/VAPI_TOOLS_CONFIGURATION.md) | Tool/function definitions for Vapi |
| [VAPI_PHONE_NUMBER_ASSIGNMENT.md](vapi/VAPI_PHONE_NUMBER_ASSIGNMENT.md) | Phone number setup guide |
| [PHONE_NUMBER_SETUP.md](vapi/PHONE_NUMBER_SETUP.md) | Detailed phone configuration |

---

## 🔧 Technical Guides

Developer reference documentation:

| Document | Description |
|----------|-------------|
| [ROUTE_TO_AGENT_GUIDE.md](technical/ROUTE_TO_AGENT_GUIDE.md) | Call transfer implementation guide |
| [BoldTrail_API_V2_Endpoints.md](technical/BoldTrail_API_V2_Endpoints.md) | BoldTrail CRM API reference |
| [XML_FEED_VERIFICATION.md](technical/XML_FEED_VERIFICATION.md) | XML feed parameter explanation and verification |
| [VIEWING_LOGS.md](technical/VIEWING_LOGS.md) | How to view and analyze logs |

---

## 🔗 Webhooks & Integrations

Webhook setup and integration guides:

| Document | Description |
|----------|-------------|
| [GHL_FORM_WEBHOOK_SETUP.md](webhooks/GHL_FORM_WEBHOOK_SETUP.md) | **Setup guide: GHL form → Vapi outbound call** ⭐ |
| [GHL_FORM_WEBHOOK_IMPLEMENTATION.md](webhooks/GHL_FORM_WEBHOOK_IMPLEMENTATION.md) | **Implementation summary & technical details** ⭐ |
| [GHL_WEBHOOK_SETUP.md](webhooks/GHL_WEBHOOK_SETUP.md) | GoHighLevel webhook general reference |
| [GHL_WEBHOOK_QUICKSTART.md](../GHL_WEBHOOK_QUICKSTART.md) | Quick start for GHL webhook configuration |

---

## 🧪 Testing & Validation

Testing tools and validation guides:

| Document | Description |
|----------|-------------|
| [XML_FEED_VALIDATOR_READY.md](testing/XML_FEED_VALIDATOR_READY.md) | Quick start guide for XML feed validator |
| [README_XML_VALIDATION.md](testing/README_XML_VALIDATION.md) | Complete XML feed validation documentation |
| [README_TESTING.md](../scripts/README_TESTING.md) | General testing guide (in scripts folder) |
| [validate_xml_feed.py](../tests/validate_xml_feed.py) | XML feed validation script |

---

## 🚀 Deployment

Deployment and production documentation:

| Document | Description |
|----------|-------------|
| [DEPLOY_INSTRUCTIONS.md](deployment/DEPLOY_INSTRUCTIONS.md) | Step-by-step deployment guide |

---

## 📁 Documentation Organization

```
docs/
├── INDEX.md (this file)
│
├── getting-started/
│   ├── START_HERE.md
│   └── REQUIREMENTS.md
│
├── configuration/
│   ├── ENV_CONFIGURATION.md
│   ├── ENV_REFERENCE.md
│   ├── SETTINGS_REFACTOR.md
│   └── TEST_MODE_CONFIGURATION.md
│
├── features/
│   ├── OPTION_A_IMPLEMENTATION.md
│   ├── MANUAL_LISTINGS_FALLBACK.md
│   ├── MANUAL_LISTINGS_DEPLOYMENT_SUMMARY.md
│   ├── MANUAL_LISTINGS_IMPLEMENTATION_COMPLETE.md
│   ├── CLIENT_REQUIREMENTS_AUDIT.md
│   └── TEST_1_FIXES_SUMMARY.md
│
├── vapi/
│   ├── VAPI_SYSTEM_PROMPT_2.md ⭐
│   ├── VAPI_KNOWLEDGE_BASE.md ⭐
│   ├── VAPI_SYSTEM_PROMPT.md
│   ├── VAPI_TOOLS_CONFIGURATION.md
│   ├── VAPI_PHONE_NUMBER_ASSIGNMENT.md
│   └── PHONE_NUMBER_SETUP.md
│
├── technical/
│   ├── ROUTE_TO_AGENT_GUIDE.md
│   ├── BoldTrail_API_V2_Endpoints.md
│   ├── XML_FEED_VERIFICATION.md
│   └── VIEWING_LOGS.md
│
├── testing/
│   ├── XML_FEED_VALIDATOR_READY.md
│   └── README_XML_VALIDATION.md
│
├── webhooks/
│   ├── GHL_FORM_WEBHOOK_SETUP.md ⭐
│   ├── GHL_FORM_WEBHOOK_IMPLEMENTATION.md ⭐
│   └── GHL_WEBHOOK_SETUP.md
│
└── deployment/
    └── DEPLOY_INSTRUCTIONS.md
```

⭐ = Currently active configuration

---

## 🔍 Quick Lookup

### "I need to..."

- **Set up the project for the first time** → [START_HERE.md](getting-started/START_HERE.md)
- **Configure environment variables** → [ENV_CONFIGURATION.md](configuration/ENV_CONFIGURATION.md)
- **Update the AI agent behavior** → [VAPI_SYSTEM_PROMPT_2.md](vapi/VAPI_SYSTEM_PROMPT_2.md) + [VAPI_KNOWLEDGE_BASE.md](vapi/VAPI_KNOWLEDGE_BASE.md)
- **Deploy to production** → [DEPLOY_INSTRUCTIONS.md](deployment/DEPLOY_INSTRUCTIONS.md)
- **Test the system** → [README_TESTING.md](../scripts/README_TESTING.md)
- **Validate XML feed** → [XML_FEED_VALIDATOR_READY.md](testing/XML_FEED_VALIDATOR_READY.md)
- **Setup GHL form webhook** → [GHL_FORM_WEBHOOK_SETUP.md](webhooks/GHL_FORM_WEBHOOK_SETUP.md)
- **Setup GHL webhook (general)** → [GHL_WEBHOOK_SETUP.md](webhooks/GHL_WEBHOOK_SETUP.md)
- **Enable test mode** → [TEST_MODE_CONFIGURATION.md](configuration/TEST_MODE_CONFIGURATION.md)
- **Understand lead notifications** → [OPTION_A_IMPLEMENTATION.md](features/OPTION_A_IMPLEMENTATION.md)
- **Understand property search** → [MANUAL_LISTINGS_FALLBACK.md](features/MANUAL_LISTINGS_FALLBACK.md)
- **Check what's implemented** → [CLIENT_REQUIREMENTS_AUDIT.md](features/CLIENT_REQUIREMENTS_AUDIT.md)
- **Debug call transfers** → [ROUTE_TO_AGENT_GUIDE.md](technical/ROUTE_TO_AGENT_GUIDE.md)
- **View logs** → [VIEWING_LOGS.md](technical/VIEWING_LOGS.md)

---

## 📝 Document Status

### Active (Currently Used)
- ✅ vapi/VAPI_SYSTEM_PROMPT_2.md
- ✅ vapi/VAPI_KNOWLEDGE_BASE.md
- ✅ configuration/ENV_CONFIGURATION.md
- ✅ features/OPTION_A_IMPLEMENTATION.md
- ✅ features/MANUAL_LISTINGS_IMPLEMENTATION_COMPLETE.md
- ✅ testing/XML_FEED_VALIDATOR_READY.md
- ✅ configuration/TEST_MODE_CONFIGURATION.md

### Reference (Keep for History)
- 📚 vapi/VAPI_SYSTEM_PROMPT.md (legacy)
- 📚 vapi/VAPI_TOOLS_CONFIGURATION.md (reference)
- 📚 features/TEST_1_FIXES_SUMMARY.md (archive)

### Development (Work in Progress)
- 🚧 features/CLIENT_REQUIREMENTS_AUDIT.md (tracking)
- 🚧 configuration/SETTINGS_REFACTOR.md (completed)

---

## 🔄 Keeping Documentation Updated

When creating new documentation:
1. Add the file to `/docs/` folder
2. Update this INDEX.md with the new file
3. Categorize it appropriately
4. Add to "Quick Lookup" section if relevant

When deprecating documentation:
1. Move to "Reference" section (don't delete)
2. Add "(deprecated)" or "(legacy)" to the name
3. Update relevant links in other documents

---

## 📞 Support

For questions about the documentation:
1. Check this INDEX for the right document
2. Use the "Quick Lookup" section
3. Refer to START_HERE.md for project overview

