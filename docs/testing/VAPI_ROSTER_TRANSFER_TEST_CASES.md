# Vapi Roster Transfer Integration — Manual Test Cases

Use these test cases when validating the roster-based transfer integration **via live Vapi phone calls**. Call the business phone number and follow each scenario.

**Prerequisites:**
- App deployed to production (Fly.io) or running locally with ngrok for webhooks
- Vapi assistant configured with `get_agent_info`, `route_to_agent`, `check_property`, `create_buyer_lead`, `create_seller_lead`, `send_notification`
- Jeff transfer tool attached to the assistant (for fallback when transfer fails)

**Roster reference (sample agents for tests):** Kim Coffer, Sally Love, Jeff Beatty, Star Amador, Amber Moore

---

## Section A: get_agent_info (Roster Lookup)

### Test Case 1: Request Specific Agent by Full Name (In Roster)
**Goal:** Verify AI uses roster and returns correct agent.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say: "I'd like to speak with Kim Coffer" | AI acknowledges and offers to connect |
| 2 | Provide name, phone, email when asked | AI creates lead first (Lead-Before-Transfer) |
| 3 | Say "yes, connect me" | AI calls `route_to_agent` with Kim Coffer; call transfers to 352-626-7671 |

**Validation:** Call transfers to Kim Coffer's number. Check Fly logs for `get_agent_info` and `route_to_agent`; agent should match roster.

---

### Test Case 2: Request Agent by Partial Name (In Roster)
**Goal:** Verify partial name matching (e.g., "Sally" matches "Sally Love").

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say: "I want to talk to Sally" | AI identifies Sally Love and offers to connect |
| 2 | Provide name, phone, email when asked | AI creates lead |
| 3 | Confirm transfer | Call transfers to Sally Love (352-430-6960) |

**Validation:** Transfer goes to Sally Love's roster number.

---

### Test Case 3: Request Unknown Agent (Not in Roster)
**Goal:** Verify fallback to roster agent when requested agent is not in roster.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say: "I need to speak with John Smith" | AI either finds a fallback agent or offers "an agent" / office |
| 2 | Provide name, phone, email when asked | AI creates lead |
| 3 | Confirm transfer | AI calls `route_to_agent`; backend replaces "John Smith" with a roster agent (e.g., Star Amador); call transfers |

**Validation:** Check Fly logs for `Agent John Smith not in roster; using fallback agent [Name]`. Call should still transfer to a valid roster number.

---

### Test Case 3b: Agent Not Found — Ask for Spelling, Then Retry
**Goal:** When agent name not found (e.g., mispronounced), AI asks for spelling and looks up again.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say a name that sounds like a roster agent but may be misheard (e.g., "Kim Cooper" for Kim Coffer) | AI calls get_agent_info, gets no match |
| 2 | — | AI asks: "Could you spell their last name for me?" (or similar) |
| 3 | Spell the correct name: "C-O-F-F-E-R" | AI calls get_agent_info again with "Coffer" or "Kim Coffer" |
| 4 | — | If found, AI offers to connect; if still not found, offers Jeff |
| 5 | Provide contact info, confirm | Transfer to Kim Coffer (or Jeff if still not found) |

**Validation:** AI does not immediately offer Jeff; it asks for spelling first and retries the lookup.

---

### Test Case 4: Request "Any Agent" (No Specific Name)
**Goal:** Verify `get_agent_info` returns roster agents when no name given.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say: "I need to speak with someone about buying a home" | AI asks for details or offers to connect with an agent |
| 2 | Say "yes, connect me to an agent" | AI calls `get_agent_info` (no params) and gets first roster agents |
| 3 | Provide name, phone, email when asked | AI creates lead |
| 4 | Confirm transfer | Call transfers to a roster agent |

**Validation:** Transfer succeeds to a number from `data/agent_roster.json`.

---

## Section B: Property Inquiry + Listing Agent (Roster Validation)

### Test Case 5: Property with Listing Agent in Roster
**Goal:** Verify `check_property` returns roster-validated listing agent; transfer uses roster phone.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call and say: "I'm interested in a property at [valid address in The Villages]" | AI calls `check_property`, gets property details |
| 2 | Note the listing agent name AI mentions | Listing agent should be one from roster (if XML has matching name) |
| 3 | Say "yes, connect me to the agent" | AI collects contact info, creates lead |
| 4 | Confirm transfer | Call transfers to listing agent's roster phone |

**Validation:** Transfer uses roster `cell_phone` for that agent, not necessarily the XML/CRM phone.

---

### Test Case 6: Property with Listing Agent Not in Roster
**Goal:** Verify backend uses roster fallback when listing agent not in roster.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call about a property whose listing agent (from XML) is not in roster | AI gets property, may say listing agent name from XML |
| 2 | Say "connect me to the agent" | AI collects contact info, creates lead |
| 3 | Confirm transfer | Backend replaces with roster fallback; call transfers to a roster agent |

**Validation:** Check Fly logs for `Listing agent 'X' not in roster; using fallback: [Name]`. Transfer should succeed.

---

### Test Case 7: Property with No Listing Agent
**Goal:** Verify AI uses `get_agent_info` when listing agent is missing.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call about a property that returns no agent (or agent with no phone) | AI says "Would you like me to connect you with an agent?" |
| 2 | Say "yes" | AI calls `get_agent_info` (no params) to get roster agent |
| 3 | Provide contact info, confirm transfer | Call transfers to roster agent or main office |

**Validation:** Transfer goes to roster agent or main office (352-290-8023 / +13523992010).

---

## Section C: Lead-Before-Transfer Gate

### Test Case 8: Transfer Blocked Without Lead
**Goal:** Verify AI cannot transfer before creating lead.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call, ask about a property, say "connect me" | AI asks for name, phone, email |
| 2 | Refuse to give phone or give incomplete info | AI should not transfer; should say something like "Before I connect you, can I get your name and the best callback number?" |
| 3 | Provide full name, phone, email | AI creates lead, then transfers |

**Validation:** No transfer occurs until lead is created. Check logs: `Transfer gate blocked` if backend receives request without lead_id.

---

### Test Case 9: Full Property Inquiry Flow with Transfer
**Goal:** End-to-end: property lookup → lead creation → agent notification → transfer.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call: "I'm interested in [address]" | AI looks up property, shares beds/baths/price |
| 2 | Say "connect me to the agent" | AI asks for name, phone, email |
| 3 | Provide: Name, Phone, Email | AI confirms each |
| 4 | AI creates lead | Caller gets SMS + email confirmation |
| 5 | AI notifies agent, then transfers | "I'm connecting you now." Call transfers to agent |

**Validation:** Lead in CRM, confirmations sent, transfer completes. Agent receives notification (SMS + email if configured).

---

## Section D: Transfer Fallback (Roster → Jeff/Office)

### Test Case 10: Agent in Roster — Successful Transfer
**Goal:** Normal path when agent is in roster.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Request "Kim Coffer" or another roster agent | AI uses roster |
| 2 | Provide contact info, confirm | Lead created |
| 3 | Agent answers | Call connects; conversation with agent |

**Validation:** Call connects to correct roster agent.

---

### Test Case 11: Transfer Fails — Fallback to Office/Jeff
**Goal:** When transfer API fails or agent number fails, fallback to office.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Request transfer to a roster agent | Normal flow |
| 2 | (Simulate failure: use a number that doesn't answer, or rely on infrastructure failure) | If transfer fails, backend tries office line |
| 3 | — | Jeff/office receives SMS + email: "FAILED TRANSFER ALERT" |

**Validation:** Check that OFFICE_NOTIFICATION_PHONE and OFFICE_NOTIFICATION_EMAIL receive failed-transfer alert. Call may still connect to office if fallback succeeds.

---

### Test Case 12: No One Picks (Transfer No-Answer)
**Goal:** When transfer succeeds (200) but agent doesn't answer, Jeff gets notified.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Request transfer to an agent (e.g., Kim Coffer) | AI creates lead, initiates transfer |
| 2 | Do not answer when the agent's phone rings | Call may ring out, go to voicemail, or return to assistant |
| 3 | — | Vapi sends `end-of-call-report` with endReason like `call.forwarding.operator-busy` or `voicemail` |
| 4 | — | Backend sends SMS + email to Jeff: "TRANSFER NO-ANSWER ALERT" |

**Validation:** Jeff receives "No one picked up" notification. Requires Vapi webhook configured and `end-of-call-report` in serverMessages.

---

## Section E: Jeff Transfer Tool (AI Fallback)

### Test Case 13: AI Uses Jeff Transfer When Transfer Fails
**Goal:** When backend transfer fails, AI should use Jeff transfer tool.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Request transfer; backend returns error (e.g., transfer failed) | AI hears that transfer could not be completed |
| 2 | — | AI says something like "I'm having trouble connecting you. Let me connect you with our office." |
| 3 | — | AI calls Jeff transfer tool (separate Vapi tool) |
| 4 | — | Call transfers to Jeff's number |

**Validation:** AI does not leave caller stranded; uses Jeff tool as fallback. Confirm in Vapi dashboard / logs that Jeff transfer tool was invoked.

---

## Section F: Buyer and Seller Flows (Roster Integration)

### Test Case 14: Buyer Flow — No Specific Property, Request Agent
**Goal:** Buyer flow with "connect me to an agent".

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call: "I'm looking to buy a home in The Villages" | AI asks timeframe, price range, etc. |
| 2 | Answer questions, then say "I want to speak with an agent" | AI collects name, phone, email |
| 3 | AI creates buyer lead | Confirmation sent |
| 4 | — | AI does NOT transfer by default (per KB); only if caller insists |
| 5 | Insist: "I need to talk to someone now" | AI creates lead, then uses `get_agent_info` → `route_to_agent` |

**Validation:** If transfer happens, it uses roster agent.

---

### Test Case 15: Seller Flow — Request Specific Agent
**Goal:** Seller asks for Sally or Jeff by name.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call: "I want to sell my home" | AI asks address, timeframe |
| 2 | Provide details, then: "I'd like to speak with Sally Love" | AI uses `get_agent_info` with agent_name="Sally Love" |
| 3 | Provide contact info | AI creates seller lead |
| 4 | Confirm transfer | Transfer to Sally Love (352-430-6960) |

**Validation:** Transfer to correct roster agent.

---

## Section G: Edge Cases

### Test Case 16: Case-Insensitive Name Match
**Goal:** "KIM COFFER" or "sally love" should still match.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Say "I need to reach KIM COFFER" (all caps) | AI finds Kim Coffer in roster |
| 2 | Complete flow | Transfer to 352-626-7671 |

---

### Test Case 17: Staff in Roster
**Goal:** Staff (e.g., Blerim Prenaj) are in roster and can receive transfers.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Say "I need to speak with Blerim Prenaj" | AI finds in roster (staff section) |
| 2 | Complete flow | Transfer to 352-626-7772 |

---

## Quick Validation Checklist

After running tests, verify in Fly.io logs:

```bash
fly logs --app sally-love-voice-agent
```

| Log Pattern | Meaning |
|-------------|---------|
| `Getting agent info` | get_agent_info was called |
| `Agent X not in roster; using fallback agent Y` | Roster fallback worked |
| `Routing call to agent: [Name] ([Phone])` | route_to_agent executing |
| `Transfer executed successfully` | Transfer succeeded |
| `Failed transfer notification sent` | Fallback alert sent to Jeff/office |
| `No-answer notification` | Transfer no-answer alert sent |
| `Transfer gate blocked` | Lead not created before transfer attempt |

---

## Test Summary Table

| # | Test Case | Category | Key Validation |
|---|-----------|----------|----------------|
| 1 | Full name (in roster) | get_agent_info | Transfer to correct agent |
| 2 | Partial name | get_agent_info | "Sally" → Sally Love |
| 3 | Unknown agent | Fallback | Roster fallback used |
| 3b | Agent not found, ask spelling | get_agent_info | Spelling retry before Jeff |
| 4 | Any agent | get_agent_info | Roster agent returned |
| 5 | Property + agent in roster | check_property | Roster-validated transfer |
| 6 | Property + agent not in roster | check_property | Roster fallback |
| 7 | Property, no agent | get_agent_info | Uses get_agent_info |
| 8 | Transfer without lead | Transfer Gate | Blocked |
| 9 | Full flow | E2E | Lead + transfer + notifications |
| 10 | Successful transfer | route_to_agent | Connects |
| 11 | Transfer fails | Fallback | Jeff/office alert |
| 12 | No one picks | No-answer | Jeff SMS+email |
| 13 | Jeff transfer tool | AI fallback | Jeff tool used |
| 14 | Buyer + agent | Buyer flow | Roster used |
| 15 | Seller + Sally | Seller flow | Roster used |
| 16 | Case-insensitive | Edge | Name match works |
| 17 | Staff transfer | Edge | Staff in roster |
