"""
Quality Checker
Handles data quality assessment and reporting
"""

from typing import List, Dict, Any

class QualityChecker:
    """
    Assesses data quality and reports potential issues
    Provides insights into data completeness and consistency
    """
    
    def check_data_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive data quality check
        
        Args:
            data: Data to analyze for quality issues
            
        Returns:
            Dict[str, Any]: Quality assessment report
        """
        if not data:
            return {'error': 'No data provided'}
        
        print(f"      🔍 Checking data quality...")
        
        quality_report = {
            'total_rows': len(data),
            'columns': list(data[0].keys()),
            'issues': [],
            'completeness': {},
            'data_types': {},
            'recommendations': []
        }
        
        # Check for various quality issues
        self._check_empty_columns(data, quality_report)
        self._check_bom_issues(data, quality_report)
        self._check_data_types(data, quality_report)
        self._check_completeness(data, quality_report)
        self._generate_recommendations(quality_report)
        
        # Report results
        if quality_report['issues']:
            print(f"      ⚠️ Data quality issues detected:")
            for issue in quality_report['issues']:
                print(f"         • {issue}")
        else:
            print(f"      ✅ Data quality check passed")
        
        return quality_report
    
    def _check_empty_columns(self, data: List[Dict], report: Dict[str, Any]):
        """Check for empty essential columns"""
        essential_cols = ['Date', 'Amount']
        
        for col in essential_cols:
            if col in data[0]:
                empty_count = sum(1 for row in data if not row.get(col) or str(row.get(col)).strip() == '')
                if empty_count > 0:
                    report['issues'].append(f"{empty_count}/{len(data)} rows have empty '{col}' values")
                    report['completeness'][col] = {
                        'empty_count': empty_count,
                        'completion_rate': (len(data) - empty_count) / len(data)
                    }
    
    def _check_bom_issues(self, data: List[Dict], report: Dict[str, Any]):
        """Check for BOM characters (should be handled by proper encoding)"""
        bom_cols = [col for col in data[0].keys() if '\ufeff' in str(col)]
        if bom_cols:
            report['issues'].append(f"BOM characters present in columns: {bom_cols}")
            report['recommendations'].append("Use UTF-8-sig encoding when reading CSV files")
    
    def _check_data_types(self, data: List[Dict], report: Dict[str, Any]):
        """Check for reasonable data types"""
        sample_row = data[0]
        
        # Check Amount column
        if 'Amount' in sample_row:
            non_numeric_amounts = sum(1 for row in data if not isinstance(row.get('Amount'), (int, float)))
            if non_numeric_amounts > 0:
                report['issues'].append(f"{non_numeric_amounts}/{len(data)} amounts are not numeric")
                report['data_types']['Amount'] = 'mixed_types'
            else:
                report['data_types']['Amount'] = 'numeric'
        
        # Check Date column
        if 'Date' in sample_row:
            empty_dates = sum(1 for row in data if not row.get('Date') or str(row.get('Date')).strip() == '')
            if empty_dates > 0:
                report['data_types']['Date'] = 'incomplete'
            else:
                report['data_types']['Date'] = 'complete'
    
    def _check_completeness(self, data: List[Dict], report: Dict[str, Any]):
        """Calculate overall data completeness"""
        essential_columns = ['Date', 'Amount', 'Title']
        total_cells = len(data) * len(essential_columns)
        filled_cells = 0
        
        for row in data:
            for col in essential_columns:
                if col in row and row[col] and str(row[col]).strip():
                    filled_cells += 1
        
        completeness_score = filled_cells / total_cells if total_cells > 0 else 0.0
        report['completeness']['overall_score'] = completeness_score
        report['completeness']['grade'] = self._get_completeness_grade(completeness_score)
    
    def _get_completeness_grade(self, score: float) -> str:
        """Convert completeness score to letter grade"""
        if score >= 0.95:
            return 'A+ (Excellent)'
        elif score >= 0.85:
            return 'A (Very Good)'
        elif score >= 0.75:
            return 'B (Good)'
        elif score >= 0.65:
            return 'C (Acceptable)'
        elif score >= 0.50:
            return 'D (Poor)'
        else:
            return 'F (Critical Issues)'
    
    def _generate_recommendations(self, report: Dict[str, Any]):
        """Generate improvement recommendations based on issues found"""
        if not report['issues']:
            report['recommendations'].append("Data quality is good - no immediate improvements needed")
            return
        
        # Recommendations based on specific issues
        for issue in report['issues']:
            if 'empty' in issue.lower() and 'date' in issue.lower():
                report['recommendations'].append("Consider filtering out rows with missing dates")
            elif 'empty' in issue.lower() and 'amount' in issue.lower():
                report['recommendations'].append("Review rows with missing amounts - may indicate parsing issues")
            elif 'not numeric' in issue.lower():
                report['recommendations'].append("Improve numeric parsing for amount columns")
            elif 'bom' in issue.lower():
                report['recommendations'].append("Use UTF-8-sig encoding when reading CSV files to handle BOM properly")
    
    def validate_bank_specific_requirements(self, data: List[Dict], bank_name: str) -> List[str]:
        """
        Validate bank-specific data requirements
        
        Args:
            data: Data to validate
            bank_name: Name of the bank for specific validation rules
            
        Returns:
            List[str]: List of validation warnings/errors
        """
        warnings = []
        bank_lower = bank_name.lower()
        
        if 'wise' in bank_lower:
            # Wise-specific validations
            if not any('description' in col.lower() for col in data[0].keys()):
                warnings.append("Wise data missing 'Description' column")
            
            if not any('paymentreference' in col.lower().replace(' ', '') for col in data[0].keys()):
                warnings.append("Wise data missing 'Payment Reference' column")
        
        elif 'nayapay' in bank_lower:
            # NayaPay-specific validations
            if not any('timestamp' in col.lower() for col in data[0].keys()):
                warnings.append("NayaPay data missing 'TIMESTAMP' column")
            
            if not any('type' in col.lower() for col in data[0].keys()):
                warnings.append("NayaPay data missing 'TYPE' column")
        
        return warnings
