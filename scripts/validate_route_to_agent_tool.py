#!/usr/bin/env python3
"""
Validate route_to_agent tool configuration
Ensures consistency between:
1. Pydantic model (RouteToAgentRequest)
2. Vapi tool schema (create_vapi_transfer_tool.py)
3. Implementation (route_to_agent.py)
"""

import sys
import inspect
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.vapi_models import RouteToAgentRequest
import json


def validate_route_to_agent_configuration():
    """Validate route_to_agent tool configuration across all files"""
    
    print("="*80)
    print("VALIDATING route_to_agent TOOL CONFIGURATION")
    print("="*80)
    print()
    
    errors = []
    warnings = []
    
    # 1. Check Pydantic Model
    print("📋 1. Checking Pydantic Model (RouteToAgentRequest)")
    print("-" * 80)
    
    model_fields = RouteToAgentRequest.model_fields
    required_fields = []
    optional_fields = []
    
    for field_name, field_info in model_fields.items():
        if field_info.is_required():
            required_fields.append(field_name)
        else:
            optional_fields.append(field_name)
    
    print(f"   Required fields: {', '.join(sorted(required_fields))}")
    print(f"   Optional fields: {', '.join(sorted(optional_fields))}")
    print()
    
    # 2. Check Vapi Tool Schema (from create_vapi_transfer_tool.py)
    print("📋 2. Checking Vapi Tool Schema (create_vapi_transfer_tool.py)")
    print("-" * 80)
    
    script_path = Path(__file__).parent / "create_vapi_transfer_tool.py"
    script_content = script_path.read_text()
    
    # Extract required fields from script
    # Look for "required": [...] in the script
    import re
    required_match = re.search(r'"required":\s*\[(.*?)\]', script_content, re.DOTALL)
    if required_match:
        required_in_script = [
            f.strip().strip('"') 
            for f in required_match.group(1).split(',') 
            if f.strip().strip('"')
        ]
        print(f"   Required in script: {', '.join(sorted(required_in_script))}")
    else:
        errors.append("Could not find 'required' array in create_vapi_transfer_tool.py")
        required_in_script = []
    
    # Extract all properties from script
    properties_match = re.search(r'"properties":\s*\{', script_content)
    if properties_match:
        # Extract properties section (rough extraction)
        props_start = properties_match.start()
        props_section = script_content[props_start:props_start+2000]
        properties_in_script = []
        for field in ['reason', 'lead_id', 'agent_id', 'agent_name', 'agent_phone', 'caller_name', 'caller_phone']:
            if f'"{field}"' in props_section:
                properties_in_script.append(field)
        print(f"   Properties in script: {', '.join(sorted(properties_in_script))}")
    else:
        errors.append("Could not find 'properties' in create_vapi_transfer_tool.py")
        properties_in_script = []
    
    # Check async flag
    has_async = '"async": True' in script_content or "'async': True" in script_content or '"async":True' in script_content
    if has_async:
        print("   ✅ Async flag: True (correct)")
    else:
        errors.append("❌ Async flag not set to True in create_vapi_transfer_tool.py (required for controlUrl)")
    
    print()
    
    # 3. Validate consistency
    print("📋 3. Validating Consistency")
    print("-" * 80)
    
    # Check required fields match
    model_required_set = set(required_fields)
    script_required_set = set(required_in_script)
    
    missing_in_script = model_required_set - script_required_set
    missing_in_model = script_required_set - model_required_set
    
    if missing_in_script:
        errors.append(f"❌ Required fields in model but not in script: {', '.join(missing_in_script)}")
    if missing_in_model:
        errors.append(f"❌ Required fields in script but not in model: {', '.join(missing_in_model)}")
    
    # Check all fields exist in both
    all_model_fields = set(model_fields.keys())
    all_script_fields = set(properties_in_script)
    
    missing_fields = all_model_fields - all_script_fields
    extra_fields = all_script_fields - all_model_fields
    
    if missing_fields:
        errors.append(f"❌ Fields in model but not in script: {', '.join(missing_fields)}")
    if extra_fields:
        warnings.append(f"⚠️  Fields in script but not in model: {', '.join(extra_fields)}")
    
    # 4. Check implementation (route_to_agent.py)
    print("📋 4. Checking Implementation (route_to_agent.py)")
    print("-" * 80)
    
    impl_path = Path(__file__).parent.parent / "src" / "functions" / "route_to_agent.py"
    impl_content = impl_path.read_text()
    
    # Check if implementation reads all required fields
    for field in required_fields:
        if f'arguments.get("{field}"' in impl_content or f'params.get("{field}"' in impl_content:
            print(f"   ✅ Reads {field}")
        else:
            warnings.append(f"⚠️  Implementation may not read {field} from arguments")
    
    # Check for Transfer Gate enforcement
    if 'lead_id' in impl_content and 'caller_name' in impl_content and 'caller_phone' in impl_content:
        if 'if not lead_id or not caller_name or not caller_phone:' in impl_content:
            print("   ✅ Transfer Gate enforcement present")
        else:
            warnings.append("⚠️  Transfer Gate check may be missing")
    else:
        warnings.append("⚠️  Transfer Gate fields may not be checked")
    
    # Check for controlUrl usage
    if 'control_url' in impl_content and 'controlUrl' in impl_content:
        print("   ✅ Control URL handling present")
    else:
        errors.append("❌ Control URL handling may be missing in implementation")
    
    # Check for async client usage
    if 'httpx.AsyncClient' in impl_content:
        print("   ✅ Uses httpx.AsyncClient (correct)")
    else:
        warnings.append("⚠️  May not be using async HTTP client")
    
    print()
    
    # 5. Summary
    print("="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print()
    
    if not errors and not warnings:
        print("✅ All validations passed! Tool configuration is consistent.")
        return 0
    else:
        if errors:
            print("❌ ERRORS FOUND:")
            for error in errors:
                print(f"   {error}")
            print()
        
        if warnings:
            print("⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        print(f"Total: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1 if errors else 0


if __name__ == "__main__":
    exit_code = validate_route_to_agent_configuration()
    sys.exit(exit_code)
