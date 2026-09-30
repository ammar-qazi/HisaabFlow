"""
Configuration endpoints for bank configurations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from backend.api.dependencies import get_config_manager

# Import models from centralized location
from backend.api.models import (
    ConfigListResponse, 
    ConfigResponse, 
    ReloadConfigsResponse
)
import logging

logger = logging.getLogger(__name__)

config_router = APIRouter()

# Config manager is now injected via dependencies

@config_router.get("/configs", response_model=ConfigListResponse)
async def list_configs(config_manager = Depends(get_config_manager)):
    """List available bank configurations using lightweight detection patterns"""
    logger.debug(f" API: Listing available bank configurations...")
    try:
        # Use detection patterns instead of loading full configs
        detection_patterns = config_manager.unified_service.get_detection_patterns()
        
        # Return user-friendly names from detection patterns
        config_display_names = []
        available_configs = []
        
        for bank_name, detection_info in detection_patterns.items():
            display_name = f"{detection_info.display_name} Configuration"
            config_display_names.append(display_name)
            available_configs.append(bank_name)
            logger.debug(f" Available: {display_name} (from {bank_name}.conf)")
        
        logger.debug(f" Total configurations found: {len(config_display_names)} (lightweight)")
        
        return {
            "configurations": config_display_names,
            "raw_bank_names": available_configs,
            "count": len(config_display_names)
        }
    except Exception as e:
        logger.error(f"[ERROR]  Config list error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@config_router.get("/config/{config_name}", response_model=ConfigResponse)
async def load_config(
    config_name: str,
    config_manager = Depends(get_config_manager)
):
    """Load bank configuration by display name or bank name"""
    logger.debug(f" API: Loading bank configuration '{config_name}'")
    try:
        # Find matching bank name
        bank_name = _find_matching_bank_name(config_name, config_manager)
        logger.debug(f" Matched bank name: '{bank_name}'")
        
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
        
        logger.debug(f"[SUCCESS] Configuration loaded successfully: {result['display_name']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR]  Config load error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")

def _find_matching_bank_name(config_name: str, config_manager) -> Optional[str]:
    """Find bank name from configuration display name or direct name"""
    logger.debug(f" Finding bank name for: '{config_name}'")
    
    config_name_lower = config_name.lower()
    available_banks = config_manager.list_configured_banks()
    
    # Direct bank name match
    if config_name_lower in [bank.lower() for bank in available_banks]:
        for bank in available_banks:
            if bank.lower() == config_name_lower:
                logger.debug(f"[SUCCESS] Direct match: {bank}")
                return bank
    
    # Display name match (e.g., "NayaPay Configuration" -> "nayapay")
    for bank_name in available_banks:
        display_name = f"{bank_name.title()} Configuration".lower()
        if config_name_lower == display_name:
            logger.debug(f"[SUCCESS] Display name match: {bank_name}")
            return bank_name
    
    logger.error(f"[ERROR]  No match found for: '{config_name}'")
    return None


@config_router.post("/reload", response_model=ReloadConfigsResponse)
async def reload_configurations(config_manager = Depends(get_config_manager)):
    """Reload all bank configurations from disk"""
    logger.debug("ℹ [API] Reloading all bank configurations...")
    try:
        # Call the reload method on the underlying unified service
        success = config_manager.unified_service.reload_all_configs(force=True)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Configuration reload failed"
            )
        
        # Get count of loaded configurations  
        available_configs = config_manager.list_configured_banks()
        count = len(available_configs)
        
        logger.debug(f"[SUCCESS] Reloaded {count} bank configurations")
        
        return {
            "success": True,
            "message": f"Successfully reloaded {count} bank configurations",
            "configurations_reloaded": count
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Configuration reload failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to reload configurations: {str(e)}"
        )
