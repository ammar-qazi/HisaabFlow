"""
File Re-evaluation Service for automatic bank detection updates after configuration creation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import logging
from backend.core.bank_detection import BankDetector
from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.core.csv_processing.csv_processing_service import CSVProcessingService
from backend.infrastructure.csv_parsing.unified_parser import UnifiedCSVParser
from backend.infrastructure.csv_cleaning.data_cleaner import DataCleaner
from backend.infrastructure.preprocessing.csv_preprocessor import CSVPreprocessor
from backend.infrastructure.csv_parsing.encoding_detector import EncodingDetector


@dataclass
class FileReclassification:
    """Result of file reclassification from unknown to known"""
    file_id: str
    filename: str
    old_status: str
    new_status: str
    new_bank_name: str
    new_confidence: float
    error: Optional[str] = None


@dataclass
class ReEvaluationResult:
    """Result of re-evaluation process"""
    processed_files: int
    reclassified_files: List[FileReclassification]
    errors: List[Dict[str, Any]]
    summary: str


@dataclass
class ReEvaluationError:
    """Error during re-evaluation process"""
    file_id: str
    filename: str
    error_type: str
    message: str
    recoverable: bool


class FileReEvaluationService:
    """Service for re-evaluating unknown files after configuration creation"""
    
    def __init__(self):
        """Initialize the re-evaluation service with required dependencies"""
        self.config_service = get_unified_config_service()
        self.logger = logging.getLogger(__name__)
        
        # Initialize CSV processing service with dependencies
        csv_parser = UnifiedCSVParser()
        csv_preprocessor = CSVPreprocessor()
        encoding_detector = EncodingDetector()
        
        self.csv_processing_service = CSVProcessingService(
            csv_parser=csv_parser,
            csv_preprocessor=csv_preprocessor,
            encoding_detector=encoding_detector
        )
        
        print(f"ℹ [FileReEvaluationService] Initialized with CSV processing dependencies")
    
    async def re_evaluate_unknown_files(self, new_config_name: str, unknown_files: List[Dict[str, Any]]) -> ReEvaluationResult:
        """
        Re-evaluate unknown files after a new configuration is created
        
        Args:
            new_config_name: Name of the newly created bank configuration
            unknown_files: List of unknown file information dictionaries
            
        Returns:
            ReEvaluationResult with processing results
        """
        print(f"ℹ [FileReEvaluationService] Starting re-evaluation for {len(unknown_files)} files after creating config: {new_config_name}")
        
        # Reload configurations to pick up the new one
        reload_success = self.config_service.reload_all_configs()
        if not reload_success:
            self.logger.warning("Failed to reload configurations - proceeding with cached configs")
        
        reclassified_files = []
        errors = []
        processed_count = 0
        
        for file_info in unknown_files:
            try:
                processed_count += 1
                print(f"  Processing file {processed_count}/{len(unknown_files)}: {file_info.get('filename', 'unknown')}")
                
                # Re-evaluate this file
                reclassification = await self._re_evaluate_single_file(file_info, new_config_name)
                
                if reclassification:
                    reclassified_files.append(reclassification)
                    print(f"    ✅ Reclassified: {reclassification.filename} → {reclassification.new_bank_name} (confidence: {reclassification.new_confidence:.2f})")
                else:
                    print(f"    ⏭️  No change: {file_info.get('filename', 'unknown')} remains unknown")
                    
            except Exception as e:
                error_info = {
                    'file_id': file_info.get('file_id', 'unknown'),
                    'filename': file_info.get('filename', 'unknown'),
                    'error_type': 'processing_error',
                    'message': str(e),
                    'recoverable': True
                }
                errors.append(error_info)
                print(f"    ❌ Error processing {file_info.get('filename', 'unknown')}: {str(e)}")
        
        # Generate summary
        summary = self._generate_summary(processed_count, len(reclassified_files), len(errors))
        
        result = ReEvaluationResult(
            processed_files=processed_count,
            reclassified_files=reclassified_files,
            errors=errors,
            summary=summary
        )
        
        print(f"ℹ [FileReEvaluationService] Re-evaluation complete: {summary}")
        return result
    
    async def _re_evaluate_single_file(self, file_info: Dict[str, Any], new_config_name: str) -> Optional[FileReclassification]:
        """
        Re-evaluate a single file to see if it now matches the new configuration
        
        Args:
            file_info: File information dictionary
            new_config_name: Name of the newly created configuration
            
        Returns:
            FileReclassification if file was reclassified, None otherwise
        """
        filename = file_info.get('filename', 'unknown')
        file_path = file_info.get('temp_path') or file_info.get('file_path')
        
        if not file_path:
            raise ValueError(f"No file path available for {filename}")
        
        try:
            # Create a basic parse config for re-evaluation
            parse_config = {
                'encoding': 'utf-8',
                'start_row': None,
                'end_row': None,
                'start_col': None,
                'end_col': None,
                'enable_cleaning': False  # Just for detection, not full processing
            }
            
            # Process the file to get bank detection results
            processing_result = self.csv_processing_service.process_single_file(
                file_info=file_info,
                parse_config=parse_config,
                enable_cleaning=False
            )
            
            if not processing_result.get('success'):
                raise Exception(f"Processing failed: {processing_result.get('error', 'Unknown error')}")
            
            # Check if the file now matches a known bank (including the new one)
            bank_info = processing_result.get('bank_info', {})
            detected_bank = bank_info.get('bank_name', 'unknown')
            confidence = bank_info.get('confidence', 0.0)
            
            # Consider it reclassified if:
            # 1. It's no longer unknown
            # 2. Has reasonable confidence (>= 0.5)
            # 3. Matches the new config or any existing config
            if detected_bank != 'unknown' and confidence >= 0.5:
                return FileReclassification(
                    file_id=file_info.get('file_id', 'unknown'),
                    filename=filename,
                    old_status='unknown',
                    new_status='known',
                    new_bank_name=detected_bank,
                    new_confidence=confidence
                )
            
            return None
            
        except Exception as e:
            # Return error in reclassification object
            return FileReclassification(
                file_id=file_info.get('file_id', 'unknown'),
                filename=filename,
                old_status='unknown',
                new_status='error',
                new_bank_name='',
                new_confidence=0.0,
                error=str(e)
            )
    
    def _generate_summary(self, processed: int, reclassified: int, errors: int) -> str:
        """Generate a human-readable summary of re-evaluation results"""
        if errors == 0:
            if reclassified == 0:
                return f"Processed {processed} files - no files were reclassified"
            elif reclassified == 1:
                return f"Processed {processed} files - 1 file was reclassified from unknown to known"
            else:
                return f"Processed {processed} files - {reclassified} files were reclassified from unknown to known"
        else:
            return f"Processed {processed} files - {reclassified} reclassified, {errors} errors"
    
    def update_file_classifications(self, reclassifications: List[FileReclassification]) -> Dict[str, Any]:
        """
        Update file classifications based on re-evaluation results
        
        Args:
            reclassifications: List of file reclassification results
            
        Returns:
            Update summary
        """
        print(f"ℹ [FileReEvaluationService] Updating classifications for {len(reclassifications)} files")
        
        successful_updates = 0
        failed_updates = 0
        
        for reclassification in reclassifications:
            try:
                if reclassification.error:
                    failed_updates += 1
                    continue
                
                # In a real implementation, this would update a database or file system
                # For now, we just log the changes
                print(f"  Updated: {reclassification.filename} → {reclassification.new_bank_name}")
                successful_updates += 1
                
            except Exception as e:
                print(f"  Failed to update {reclassification.filename}: {str(e)}")
                failed_updates += 1
        
        return {
            'successful_updates': successful_updates,
            'failed_updates': failed_updates,
            'total_processed': len(reclassifications)
        }
    
    def notify_ui_state_change(self, changes: List[FileReclassification]) -> None:
        """
        Notify UI components about file state changes
        
        Args:
            changes: List of file state changes
        """
        print(f"ℹ [FileReEvaluationService] Notifying UI of {len(changes)} file state changes")
        
        # In a real implementation, this would use WebSocket or similar
        # to notify the frontend about state changes
        for change in changes:
            if not change.error:
                print(f"  UI Update: {change.filename} status changed from {change.old_status} to {change.new_status}")