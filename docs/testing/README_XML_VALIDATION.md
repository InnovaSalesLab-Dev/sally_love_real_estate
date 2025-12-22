# Quick XML Feed Validation

## 🎯 Purpose

Quickly validate that your BoldTrail XML feed is fetching **ALL** MLS listings (not just 10!).

---

## 🚀 How To Run

### Step 1: Navigate to project directory

```bash
cd /Users/mac/Developer/sally_love_voice_agent
```

### Step 2: Run the validator

```bash
python3 tests/validate_xml_feed.py
```

---

## 📊 What It Shows

### 1. **Total Listings Count**

```
✅ SUCCESS - FEED STATISTICS
Total listings fetched: 247
```

**This proves we're NOT limited to 10 listings!**

### 2. **Listings by Status**

```
Active: 180
Pending: 15
Sold: 52
```

### 3. **Sample Listings**

Shows first 5 listings with details:
- Address
- Price
- Beds/Baths
- Status
- Agent

### 4. **Interactive Search**

You can enter any address to search:

```
🏠 Search address (or 'q' to quit): 17300 SE 91st Lee Avenue

✅ Found 1 matching listing(s):

1. 17300 SE 91ST LEE AVENUE, THE VILLAGES, FL 32162
   MLS #: G5105694
   Price: $575,000
   Beds/Baths: 3/2
   Property Type: Single Family
   Status: Active
   Agent: Kim Coffer (352-626-7671)
   Listed: 2025-12-18
```

---

## 🧪 Test Cases

### Test 1: Verify Total Count

**Expected:** Should show 100-300+ listings (not 10!)

**If you see only 10 listings:**
- ❌ Something is wrong with the XML parsing
- Check the script output for errors

**If you see 100+ listings:**
- ✅ XML feed is working correctly!

---

### Test 2: Search for Known Property

**Steps:**
1. Run the validator
2. Enter an address you know exists in BoldTrail
3. Confirm it's found

**Example:**
```
Search address: 17300 SE 91st Lee Avenue
✅ Found 1 matching listing(s)
```

---

### Test 3: Search for Active vs Sold

**Active property:**
```
Search address: [any active listing from the sample]
✅ Found - Status: Active
```

**Sold property (within 10 days):**
```
Search address: [recently sold listing]
✅ Found - Status: Sold
```

**Sold property (older than 10 days):**
```
Search address: [sold 2+ weeks ago]
❌ Not found (this is expected with /10 parameter)
```

---

## 📋 Example Output

```
================================================================================
🔍 BOLDTRAIL XML FEED VALIDATOR
================================================================================

📋 Configuration:
   Zapier Key: OTg3NjlhMWU0M2M0MDgzZ...
   Environment: production

📡 Fetching listings from XML feed...
   URL: https://api.kvcore.com/export/listings/OTg3NjlhMWU0M2M0MDgzZ.../10

================================================================================
✅ SUCCESS - FEED STATISTICS
================================================================================
📊 Total listings fetched: 247

📈 Listings by Status:
   Active: 180
   Pending: 15
   Sold: 52

================================================================================
📋 SAMPLE LISTINGS (First 5)
================================================================================

1. 17300 SE 91ST LEE AVENUE, THE VILLAGES
   Price: $575,000
   Beds/Baths: 3/2
   Status: Active
   Agent: Kim Coffer

[... more listings ...]

================================================================================
🔍 INTERACTIVE SEARCH
================================================================================
Enter an address to search (or press Enter to skip):
Examples:
  - 17300 SE 91st Lee Avenue
  - 1738 Augustine Drive
  - 368 Grand Vista Trail

🏠 Search address (or 'q' to quit): 
```

---

## ✅ What To Look For

### **GOOD SIGNS:**

✅ **Total listings > 100** → Proves `/10` is NOT a limit!  
✅ **Active + Sold listings** → Shows we're getting both  
✅ **Can search and find properties** → Validates search logic  
✅ **Agent info included** → Ready for call transfers  

### **BAD SIGNS:**

❌ **Total listings = 10** → Something is wrong with parsing  
❌ **Total listings = 0** → Zapier key or XML feed issue  
❌ **Can't find known properties** → Search logic issue  
❌ **Missing agent info** → XML structure might have changed  

---

## 🔧 Troubleshooting

### Issue: "Total listings fetched: 0"

**Possible causes:**
1. Zapier key not configured in `.env`
2. Invalid Zapier key
3. No listings in BoldTrail CRM

**Solution:**
1. Check `.env` file has `BOLDTRAIL_ZAPIER_KEY=...`
2. Verify key is correct from BoldTrail
3. Log into BoldTrail and verify listings exist

---

### Issue: "Total listings fetched: 10"

**Possible causes:**
1. XML parsing is finding wrong elements
2. XML structure changed

**Solution:**
1. Check raw XML output in the error message
2. Verify the XML element tags match `<Listing>`

---

### Issue: "Property not found"

**Possible causes:**
1. Property doesn't exist in XML feed
2. Address format doesn't match
3. Property is in manual listings (not MLS)

**Solution:**
1. Try searching with partial address (e.g., just street number)
2. Check if property is in manual listings (will be caught by fallback)
3. Verify property exists in BoldTrail UI

---

## 📞 Next Steps

### If All Tests Pass ✅

**Your XML feed is working correctly!**

- You're fetching ALL listings (not just 10)
- Search logic is working
- Agent info is available for transfers
- Ready to use in production

**No action needed!** 🎉

---

### If Tests Fail ❌

1. Share the output with the development team
2. Check the error messages
3. Verify Zapier key configuration
4. Check BoldTrail CRM has listings

---

## 🎯 Quick Validation Checklist

- [ ] Run `python3 tests/validate_xml_feed.py`
- [ ] Verify total listings > 100 (not 10!)
- [ ] Search for a known active property → Found ✅
- [ ] Search for a recently sold property → Found ✅
- [ ] Verify agent info is included

**If all checked:** ✅ Your XML feed is working perfectly!

---

**Last Updated:** December 22, 2025  
**Status:** Ready to use

