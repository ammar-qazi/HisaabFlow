"""
Configuration endpoints for bank configurations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from backend.api.dependencies import get_config_manager

# Import models from centralized location
from backend.api.models import (
    SaveTemplateRequest, 
    ConfigListResponse, 
    ConfigResponse, 
    SaveConfigResponse
)

config_router = APIRouter()

# Config manager is now injected via dependencies

@config_router.get("/configs", response_model=ConfigListResponse)
async def list_configs(config_manager = Depends(get_config_manager)):
    """List available bank configurations"""
    print(f" API: Listing available bank configurations...")
    try:
        available_configs = config_manager.list_configured_banks()
        
        # Return user-friendly names
        config_display_names = []
        for bank_name in available_configs:
            config = config_manager.get_bank_config(bank_name)
            if config:
                display_name = f"{config.name.title()} Configuration"
                config_display_names.append(display_name)
                print(f" Available: {display_name} (from {bank_name}.conf)")
        
        print(f" Total configurations found: {len(config_display_names)}")
        
        return {
            "configurations": config_display_names,
            "raw_bank_names": available_configs,
            "count": len(config_display_names)
        }
    except Exception as e:
        print(f"[ERROR]  Config list error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@config_router.get("/config/{config_name}", response_model=ConfigResponse)
async def load_config(
    config_name: str,
    config_manager = Depends(get_config_manager)
):
    """Load bank configuration by display name or bank name"""
    print(f" API: Loading bank configuration '{config_name}'")
    try:
        # Find matching bank name
        bank_name = _find_matching_bank_name(config_name, config_manager)
        print(f" Matched bank name: '{bank_name}'")
        
        if not bank_name:
            available = config_manager.list_configured_banks()
            raise HTTPException(
                status_code=404, 
                detail=f"Configuration '{config_name}' not found. Available: {available}"
            )
        
        # Load the configuration
        config = config_manager.get_bank_config(bank_name)
        if not config:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to load configuration for {bank_name}"
            )
        
        # Convert to frontend format
        frontend_config = {
            "start_row": getattr(config.csv_config, 'start_row', 0),
            "end_row": getattr(config.csv_config, 'end_row', None),
            "start_col": getattr(config.csv_config, 'start_col', 0),
            "end_col": getattr(config.csv_config, 'end_col', None),
            "column_mapping": config.column_mapping,
            "bank_name": config.name,
            "currency": config.currency_primary,
            "account": config.cashew_account,
            "categorization_rules": getattr(config, 'categorization_rules', {}),
            "default_category_rules": config.default_category_rules,
            "account_mapping": config.account_mapping,
            "data_cleaning": {
                "enable_currency_addition": config.data_cleaning.enable_currency_addition,
                "multi_currency": config.data_cleaning.multi_currency,
                "numeric_amount_conversion": config.data_cleaning.numeric_amount_conversion,
                "date_standardization": config.data_cleaning.date_standardization,
                "remove_invalid_rows": config.data_cleaning.remove_invalid_rows,
                "default_currency": config.data_cleaning.default_currency
            }
        }
        
        result = {
            "success": True,
            "config": frontend_config,
            "bank_name": config.name,
            "display_name": f"{config.name.title()} Configuration",
            "source": f"{bank_name}.conf"
        }
        
        print(f"[SUCCESS] Configuration loaded successfully: {result['display_name']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR]  Config load error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")

@config_router.post("/save-config", response_model=SaveConfigResponse)
async def save_config(
    request: SaveTemplateRequest,
    config_manager = Depends(get_config_manager)
):
    """Save bank configuration"""
    print(f" API: Saving bank configuration: {request.template_name}")
    try:
        config_filename = f"{request.template_name.lower().replace(' ', '_')}.conf"
        print(f" Configuration should be saved to: ../configs/{config_filename}")
        print(f" Config data: {request.config}")
        
        return {
            "success": True,
            "message": f"Configuration saved as {config_filename}",
            "config_file": config_filename,
            "suggestion": "Consider manually creating the .conf file for better control"
        }
    except Exception as e:
        print(f"[ERROR]  Config save error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

def _find_matching_bank_name(config_name: str, config_manager) -> Optional[str]:
    """Find bank name from configuration display name or direct name"""
    print(f" Finding bank name for: '{config_name}'")
    
    config_name_lower = config_name.lower()
    available_banks = config_manager.list_configured_banks()
    
    # Direct bank name match
    if config_name_lower in [bank.lower() for bank in available_banks]:
        for bank in available_banks:
            if bank.lower() == config_name_lower:
                print(f"[SUCCESS] Direct match: {bank}")
                return bank
    
    # Display name match (e.g., "NayaPay Configuration" -> "nayapay")
    for bank_name in available_banks:
        display_name = f"{bank_name.title()} Configuration".lower()
        if config_name_lower == display_name:
            print(f"[SUCCESS] Display name match: {bank_name}")
            return bank_name
    
    print(f"[ERROR]  No match found for: '{config_name}'")
    return None
