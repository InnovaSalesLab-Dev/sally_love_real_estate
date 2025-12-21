# Sally Love Real Estate - Voice Agent Requirements

## 📋 Business Context

- **Company**: Sally Love Real Estate
- **Location**: Florida
- **Team**: 70+ Real Estate Agents
- **Main Phone**: 352-399-2010
- **CRM**: BoldTrail
- **MLS**: Stellar MLS

## 🎯 Project Goals

Create an AI-powered voice agent that:

1. **Handles incoming calls** to the main office line
2. **Qualifies leads** (buyers and sellers)
3. **Provides property information** from MLS
4. **Routes calls** to appropriate agents
5. **Captures detailed information** for follow-up
6. **Sends confirmations** via SMS

_Note: Appointment scheduling will be added in Phase 2._

## 👥 User Types

### 1. Buyers (Property Inquiries)
- Looking for properties to purchase
- Need: Property details, pricing, availability
- Want: Agent contact, showing schedule

### 2. Sellers (Listing Inquiries)
- Want to sell their property
- Need: Market analysis, listing services
- Want: Listing agent consultation

### 3. General Inquiries
- Questions about services
- Agent information requests
- Office hours and contact info

## 🔄 Call Flow

### Inbound Call Flow

```
1. Greeting
   ↓
2. Identify Need (Buyer / Seller / Other)
   ↓
3. Collect Information
   ↓
4. Provide Relevant Info or Route to Agent
   ↓
5. Confirm & Send SMS
   ↓
6. End Call
```

### Buyer Flow
```
1. What type of property?
2. What location?
3. Price range?
4. Bedrooms/bathrooms?
5. Timeline?
6. Pre-approved for mortgage?
7. Contact information
8. Create lead in CRM
9. Send confirmation SMS
10. Offer to connect with agent or schedule showing
```

### Seller Flow
```
1. Property address?
2. Property details (beds, baths, sq ft)?
3. Year built?
4. Reason for selling?
5. Timeline?
6. Estimated value expectations?
7. Contact information
8. Create lead in CRM
9. Send confirmation SMS
10. Offer listing agent consultation
```

## 🛠️ Required Functions

### 1. check_property
**Purpose**: Search MLS for properties

**Inputs**:
- Address, city, state, zip
- MLS number
- Price range
- Bedrooms, bathrooms
- Property type

**Outputs**:
- Matching properties
- Property details (price, beds, baths, address)
- Availability status

### 2. get_agent_info
**Purpose**: Find and retrieve agent information

**Inputs**:
- Agent name or ID
- Specialty (buyers, sellers, luxury, commercial)
- Service area

**Outputs**:
- Agent contact info
- Specialties
- Availability
- Service areas

### 3. route_to_agent
**Purpose**: Transfer call to specific agent

**Inputs**:
- Agent ID and phone
- Caller information
- Reason for transfer

**Outputs**:
- Transfer initiation
- Context for agent

### 4. create_buyer_lead
**Purpose**: Capture buyer information in CRM

**Inputs**:
- Contact details (name, phone, email)
- Property preferences
- Budget range
- Timeline
- Pre-approval status

**Outputs**:
- Lead ID in CRM
- Confirmation SMS sent
- Agent assignment

### 5. create_seller_lead
**Purpose**: Capture seller information in CRM

**Inputs**:
- Contact details
- Property address and details
- Reason for selling
- Timeline
- Value expectations

**Outputs**:
- Lead ID in CRM
- Confirmation SMS sent
- Listing agent assignment

_Note: Appointment scheduling functionality will be added in Phase 2. For now, agents will contact buyers directly to arrange showings._

### 6. send_notification
**Purpose**: Send SMS/email confirmations

**Inputs**:
- Recipient phone/email
- Message content
- Type (SMS/email/both)

**Outputs**:
- Delivery status
- Message ID

## 🚫 Business Rules & Constraints

### Never Do:
1. ❌ Discuss commission rates or fees
2. ❌ Say negative things about people
3. ❌ Say negative things about properties
4. ❌ Say negative things about competitors
5. ❌ Make promises about property values
6. ❌ Provide legal or financial advice

### Always Do:
1. ✅ Be professional and friendly
2. ✅ Collect detailed information
3. ✅ Send confirmations via SMS
4. ✅ Offer to connect with live agent
5. ✅ Confirm phone numbers and spelling
6. ✅ Provide accurate property information
7. ✅ Note urgency and timeline

## ⏰ Operating Hours

- **Office Hours**: 9 AM - 5 PM EST
- **Agent Availability**: Agents accept calls anytime
- **After Hours**: Voice agent active 24/7
- **Holiday Coverage**: Voice agent handles all calls

## 📱 SMS Confirmations

Send SMS for:
- ✅ Lead capture (buyer/seller)
- ✅ Appointment scheduling
- ✅ Agent routing
- ✅ Follow-up reminders

SMS Format:
```
Hi [Name]! Thank you for contacting Sally Love Real Estate. 
[Specific confirmation message]
We'll be in touch shortly. - Sally Love Real Estate
```

## 🔗 Integration Requirements

### Vapi.ai
- Voice recognition and synthesis
- Function calling capability
- Call routing
- Recording and transcription

### BoldTrail CRM
- Create/update contacts
- Create buyer/seller leads
- Assign to agents
- Add notes and tags
- (Appointments in Phase 2)

### Stellar MLS
- Property search
- Property details
- Availability status
- Photos and virtual tours

### Twilio
- SMS notifications
- Call transfer capability
- Phone number management

## 📊 Success Metrics

### Key Metrics to Track:
1. **Call Volume**: Total inbound calls handled
2. **Lead Capture Rate**: % of calls resulting in leads
3. **Transfer Rate**: % of calls transferred to agents
4. **Showing Bookings**: Number of showings scheduled
5. **Response Time**: Average time to answer
6. **Call Duration**: Average call length
7. **SMS Delivery**: % of confirmations sent successfully
8. **Agent Satisfaction**: Feedback from agents
9. **Caller Satisfaction**: Follow-up surveys

### Performance Targets:
- ✅ 95%+ call answer rate
- ✅ 80%+ lead capture rate
- ✅ 90%+ SMS delivery rate
- ✅ < 30 second average response time
- ✅ 4.5+ agent satisfaction rating

## 🔐 Security & Compliance

### Data Protection:
- Secure storage of contact information
- Encrypted API communications
- GDPR/CCPA compliance
- Call recording disclosure
- Data retention policies

### Quality Assurance:
- Regular transcript review
- Agent feedback collection
- Performance monitoring
- Continuous prompt optimization

## 📞 Escalation Path

When to transfer to live agent:
1. Caller requests specifically
2. Complex legal/financial questions
3. Complaints or disputes
4. Commission discussions
5. Technical issues with voice agent
6. After 3 failed attempts to understand caller

## 🎓 Training Data Needs

### Property Knowledge:
- Florida real estate market
- Local neighborhoods
- School districts
- Property types and terminology
- MLS data structure

### Process Knowledge:
- Buying process overview
- Selling process overview
- Financing basics
- Showing procedures
- Offer and negotiation basics

### Agent Knowledge:
- Agent specialties and strengths
- Service area expertise
- Language capabilities
- Availability patterns

## 🚀 Rollout Plan

### Phase 1: Testing (Week 1-2)
- Internal testing with team
- Sample call scenarios
- Function validation
- Integration testing

### Phase 2: Soft Launch (Week 3-4)
- Limited hours (business hours only)
- Monitor all calls
- Collect feedback
- Adjust prompts

### Phase 3: Full Launch (Week 5+)
- 24/7 operation
- All call types
- Performance monitoring
- Continuous optimization

