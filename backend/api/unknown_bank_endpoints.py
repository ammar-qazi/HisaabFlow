"""
Unknown Bank API Endpoints
Handles unknown bank CSV analysis, configuration generation, and validation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Dict, Any, Optional
import io
import os
import uuid
from backend.services.unknown_bank_service import UnknownBankService
from backend.services.unknown_bank_service import BankConfigInput, ConfigValidationResult
from backend.infrastructure.csv_parsing.structure_analyzer import UnknownBankAnalysis
from backend.shared.amount_formats.regional_formats import AmountFormat, RegionalFormatRegistry
from backend.api.models import (
    UnknownBankAnalysisResponse, UnknownBankAnalysisRequest,
    GenerateBankConfigRequest, GenerateBankConfigResponse,
    ValidateBankConfigRequest, ValidateBankConfigResponse,
    SaveBankConfigRequest, SaveBankConfigResponse,
    AmountFormatAnalysisModel, AmountFormatModel, FieldMappingSuggestionModel,
    BankConfigInputModel, ConfigValidationResultModel
)

# Router for unknown bank endpoints
unknown_bank_router = APIRouter(prefix="/unknown-bank", tags=["unknown-bank"])

# Storage for analysis results (in production, use Redis or database)
analysis_storage: Dict[str, UnknownBankAnalysis] = {}

# Service instance
unknown_bank_service = UnknownBankService()


def get_unknown_bank_service() -> UnknownBankService:
    """Dependency injection for UnknownBankService"""
    return unknown_bank_service


@unknown_bank_router.post("/analyze-csv")
async def analyze_unknown_csv(
    file: UploadFile = File(...),
    header_row: Optional[int] = Form(None),
    service: UnknownBankService = Depends(get_unknown_bank_service)
) -> UnknownBankAnalysisResponse:
    """
    Analyze uploaded CSV for unknown bank configuration.
    
    Args:
        file: Uploaded CSV file
        service: Injected UnknownBankService
        
    Returns:
        UnknownBankAnalysisResponse with analysis results
    """
    print(f"ℹ [API] Analyzing unknown bank CSV: {file.filename}")
    print(f"ℹ [API] Header row parameter received: {header_row}")
    
    temp_file_path = None
    try:
        # Save the uploaded file to a temporary path
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        # Call the refactored service with the file path
        analysis = service.analyze_unknown_bank_csv(
            file_path=temp_file_path,
            filename=file.filename or "unknown.csv",
            header_row=header_row
        )
        
        # Store analysis for later use
        analysis_id = str(uuid.uuid4())
        analysis_storage[analysis_id] = analysis
        
        # Convert to API models
        amount_format_model = AmountFormatModel(
            decimal_separator=analysis.amount_format_analysis.detected_format.decimal_separator,
            thousand_separator=analysis.amount_format_analysis.detected_format.thousand_separator,
            negative_style=analysis.amount_format_analysis.detected_format.negative_style,
            currency_position=analysis.amount_format_analysis.detected_format.currency_position,
            grouping_pattern=analysis.amount_format_analysis.detected_format.grouping_pattern
        )
        
        amount_analysis_model = AmountFormatAnalysisModel(
            detected_format=amount_format_model,
            confidence=analysis.amount_format_analysis.confidence,
            sample_count=analysis.amount_format_analysis.sample_count,
            detected_patterns=analysis.amount_format_analysis.detected_patterns,
            problematic_samples=analysis.amount_format_analysis.problematic_samples,
            currency_symbols=analysis.amount_format_analysis.currency_symbols
        )
        
        # Convert field mapping suggestions
        field_suggestions = {}
        for field_name, suggestion in analysis.field_mapping_suggestions.items():
            field_suggestions[field_name] = FieldMappingSuggestionModel(
                field_name=suggestion.field_name,
                suggested_columns=suggestion.suggested_columns,
                confidence_scores=suggestion.confidence_scores,
                best_match=suggestion.best_match
            )
        
        # Create response
        response = UnknownBankAnalysisResponse(
            success=True,
            filename=analysis.filename,
            encoding=analysis.encoding,
            delimiter=analysis.delimiter,
            headers=analysis.headers,
            header_row=analysis.header_row,
            data_start_row=analysis.data_start_row,
            amount_format_analysis=amount_analysis_model,
            field_mapping_suggestions=field_suggestions,
            filename_patterns=analysis.filename_patterns,
            sample_data=analysis.sample_data,
            structure_confidence=analysis.structure_confidence
        )
        
        # Add analysis_id to response (extend model if needed)
        response_dict = response.dict()
        response_dict['analysis_id'] = analysis_id
        
        print(f"  Analysis complete. ID: {analysis_id}, Confidence: {analysis.structure_confidence:.2f}")
        return response_dict
        
    except Exception as e:
        print(f"[ERROR] [API] Unknown CSV analysis failed: {str(e)}")
        return UnknownBankAnalysisResponse(
            success=False,
            filename=file.filename or "unknown.csv",
            encoding="utf-8",
            delimiter=",",
            headers=[],
            header_row=0,
            data_start_row=0,
            amount_format_analysis=AmountFormatAnalysisModel(
                detected_format=AmountFormatModel(
                    decimal_separator=".",
                    thousand_separator=",",
                    negative_style="minus",
                    currency_position="prefix"
                ),
                confidence=0.0,
                sample_count=0,
                detected_patterns={},
                problematic_samples=[],
                currency_symbols=[]
            ),
            field_mapping_suggestions={},
            filename_patterns=[],
            sample_data=[],
            structure_confidence=0.0,
            error=str(e)
        )
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@unknown_bank_router.post("/generate-config")
async def generate_bank_config(
    request: GenerateBankConfigRequest,
    service: UnknownBankService = Depends(get_unknown_bank_service)
) -> GenerateBankConfigResponse:
    """
    Generate bank configuration from analysis and user input.
    
    Args:
        request: Configuration generation request
        service: Injected UnknownBankService
        
    Returns:
        GenerateBankConfigResponse with generated configuration
    """
    print(f"ℹ [API] Generating config for bank: {request.config_input.bank_name}")
    
    try:
        # Retrieve stored analysis
        if request.analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found. Please re-analyze the CSV.")
        
        analysis = analysis_storage[request.analysis_id]
        
        # Convert API model to service model
        amount_format = AmountFormat(
            decimal_separator=request.config_input.amount_format.decimal_separator,
            thousand_separator=request.config_input.amount_format.thousand_separator,
            negative_style=request.config_input.amount_format.negative_style,
            currency_position=request.config_input.amount_format.currency_position,
            grouping_pattern=request.config_input.amount_format.grouping_pattern
        )
        
        config_input = BankConfigInput(
            bank_name=request.config_input.bank_name,
            display_name=request.config_input.display_name,
            filename_patterns=request.config_input.filename_patterns,
            column_mappings=request.config_input.column_mappings,
            amount_format=amount_format,
            currency_primary=request.config_input.currency_primary,
            cashew_account=request.config_input.cashew_account,
            description_cleaning_rules=request.config_input.description_cleaning_rules
        )
        
        # Generate configuration
        config = service.generate_bank_config(analysis, config_input)
        
        # Generate INI preview
        config_preview = _generate_config_preview(config)
        
        return GenerateBankConfigResponse(
            success=True,
            config=config,
            config_preview=config_preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] [API] Config generation failed: {str(e)}")
        return GenerateBankConfigResponse(
            success=False,
            config={},
            config_preview="",
            error=str(e)
        )


@unknown_bank_router.post("/validate-config")
async def validate_bank_config(
    request: ValidateBankConfigRequest,
    service: UnknownBankService = Depends(get_unknown_bank_service)
) -> ValidateBankConfigResponse:
    """
    Validate generated bank configuration.
    
    Args:
        request: Validation request
        service: Injected UnknownBankService
        
    Returns:
        ValidateBankConfigResponse with validation results
    """
    print(f"ℹ [API] Validating bank config")
    
    try:
        # Retrieve stored analysis
        if request.analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found. Please re-analyze the CSV.")
        
        analysis = analysis_storage[request.analysis_id]
        
        # Validate configuration
        validation_result = service.validate_generated_config(request.config, analysis)
        
        # Convert to API model
        validation_model = ConfigValidationResultModel(
            is_valid=validation_result.is_valid,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            sample_parse_success=validation_result.sample_parse_success,
            parsed_sample_count=validation_result.parsed_sample_count
        )
        
        return ValidateBankConfigResponse(
            success=True,
            validation_result=validation_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] [API] Config validation failed: {str(e)}")
        return ValidateBankConfigResponse(
            success=False,
            validation_result=ConfigValidationResultModel(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                sample_parse_success=False,
                parsed_sample_count=0
            ),
            error=str(e)
        )


@unknown_bank_router.post("/save-config")
async def save_bank_config(
    request: SaveBankConfigRequest,
    service: UnknownBankService = Depends(get_unknown_bank_service)
) -> SaveBankConfigResponse:
    """
    Save bank configuration to file.
    
    Args:
        request: Save configuration request
        service: Injected UnknownBankService
        
    Returns:
        SaveBankConfigResponse with save results
    """
    bank_name = request.config.get('bank_info', {}).get('bank_name', 'unknown')
    print(f"ℹ [API] Saving bank config: {bank_name}")
    
    try:
        # Check if config already exists (unless force overwrite)
        if not request.force_overwrite and service.config_service.has_bank_config(bank_name):
            return SaveBankConfigResponse(
                success=False,
                config_file="",
                bank_name=bank_name,
                reload_success=False,
                message=f"Bank '{bank_name}' already exists. Use force_overwrite=true to replace.",
                error="Bank already exists"
            )
        
        # Save configuration
        save_success = service.save_bank_config(request.config)
        
        if save_success:
            # Check if reload was successful
            reload_success = service.config_service.has_bank_config(bank_name)
            
            return SaveBankConfigResponse(
                success=True,
                config_file=f"{bank_name}.conf",
                bank_name=bank_name,
                reload_success=reload_success,
                message=f"Bank configuration '{bank_name}' saved successfully.",
            )
        else:
            return SaveBankConfigResponse(
                success=False,
                config_file="",
                bank_name=bank_name,
                reload_success=False,
                message="Failed to save configuration.",
                error="Save operation failed"
            )
        
    except Exception as e:
        print(f"[ERROR] [API] Config save failed: {str(e)}")
        return SaveBankConfigResponse(
            success=False,
            config_file="",
            bank_name=bank_name,
            reload_success=False,
            message="Configuration save failed.",
            error=str(e)
        )


@unknown_bank_router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str) -> UnknownBankAnalysisResponse:
    """
    Retrieve stored analysis by ID.
    
    Args:
        analysis_id: Analysis identifier
        
    Returns:
        UnknownBankAnalysisResponse with stored analysis
    """
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_storage[analysis_id]
    
    # Convert back to response format (simplified version)
    # In a real implementation, this would be stored in proper format
    return {"success": True, "analysis": analysis, "analysis_id": analysis_id}


@unknown_bank_router.post("/validate-header-row")
async def validate_header_row(
    file: UploadFile = File(...),
    header_row: int = 1,
    service: UnknownBankService = Depends(get_unknown_bank_service)
) -> Dict[str, Any]:
    """
    Validate a specific header row configuration for a CSV file.
    
    Args:
        file: Uploaded CSV file
        header_row: Header row number (1-based indexing)
        service: Injected UnknownBankService
        
    Returns:
        Validation results with preview data
    """
    print(f"ℹ [API] Validating header row {header_row} for: {file.filename}")
    
    temp_file_path = None
    try:
        # Save the uploaded file to a temporary path
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Read CSV content for validation
        csv_content = content.decode('utf-8')
        
        # Use the structure analyzer to validate header row
        validation_result = service.structure_analyzer.validate_header_row(
            csv_data=csv_content,
            header_row=header_row,
            delimiter=','  # Could be auto-detected in future
        )
        
        print(f"  Header row validation: {'Valid' if validation_result['valid'] else 'Invalid'}")
        return validation_result
        
    except Exception as e:
        print(f"[ERROR] [API] Header row validation failed: {str(e)}")
        return {
            'valid': False,
            'error': f'Validation failed: {str(e)}',
            'total_rows': 0
        }
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@unknown_bank_router.delete("/analysis/{analysis_id}")
async def cleanup_analysis(analysis_id: str) -> Dict[str, Any]:
    """
    Clean up stored analysis to free memory.
    
    Args:
        analysis_id: Analysis identifier
        
    Returns:
        Cleanup confirmation
    """
    if analysis_id in analysis_storage:
        del analysis_storage[analysis_id]
        return {"success": True, "message": "Analysis cleaned up"}
    else:
        return {"success": False, "message": "Analysis not found"}


def _generate_config_preview(config: Dict[str, Any]) -> str:
    """Generate INI format preview of the configuration."""
    import configparser
    import io
    
    try:
        config_parser = configparser.ConfigParser()
        
        # Add sections in order
        if 'bank_info' in config:
            config_parser.add_section('bank_info')
            for key, value in config['bank_info'].items():
                if isinstance(value, list):
                    config_parser.set('bank_info', key, ', '.join(value))
                else:
                    config_parser.set('bank_info', key, str(value))
        
        if 'csv_config' in config:
            config_parser.add_section('csv_config')
            for key, value in config['csv_config'].items():
                config_parser.set('csv_config', key, str(value))
        
        if 'column_mapping' in config:
            config_parser.add_section('column_mapping')
            for key, value in config['column_mapping'].items():
                if value:  # Only add non-empty mappings
                    config_parser.set('column_mapping', key, str(value))
        
        if 'data_cleaning' in config:
            config_parser.add_section('data_cleaning')
            data_cleaning = config['data_cleaning']
            if 'amount_format' in data_cleaning:
                amount_format = data_cleaning['amount_format']
                for key, value in amount_format.items():
                    config_parser.set('data_cleaning', key, str(value))
            for key, value in data_cleaning.items():
                if key != 'amount_format':
                    config_parser.set('data_cleaning', key, str(value))
        
        # Generate string output
        output = io.StringIO()
        config_parser.write(output)
        return output.getvalue()
        
    except Exception as e:
        return f"# Error generating preview: {str(e)}"