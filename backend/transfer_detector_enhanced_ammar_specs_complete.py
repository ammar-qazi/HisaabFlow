            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _dates_within_tolerance(self, date1: datetime, date2: datetime) -> bool:
        """Check if two dates are within the tolerance period"""
        try:
            delta = abs((date1 - date2).total_seconds() / 3600)
            return delta <= self.date_tolerance_hours
        except Exception:
            return False
    
    def apply_transfer_categorization(self, csv_data_list: List[Dict], transfer_pairs: List[Dict]) -> List[Dict]:
        """Apply Balance Correction category to detected transfers"""
        transfer_matches = []
        
        for pair in transfer_pairs:
            outgoing = pair['outgoing']
            incoming = pair['incoming']
            
            # Include exchange amount information in notes
            exchange_note = ""
            if pair.get('exchange_amount'):
                exchange_note = f" | Exchange Amount: {pair['exchange_amount']}"
            
            transfer_matches.append({
                'csv_index': outgoing['_csv_index'],
                'amount': str(self._parse_amount(outgoing.get('Amount', '0'))),
                'date': self._parse_date(outgoing.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(outgoing.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer out - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'outgoing',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
            
            transfer_matches.append({
                'csv_index': incoming['_csv_index'],
                'amount': str(self._parse_amount(incoming.get('Amount', '0'))),
                'date': self._parse_date(incoming.get('Date', '')).strftime('%Y-%m-%d'),
                'description': str(incoming.get('Description', '')),
                'category': 'Balance Correction',
                'note': f"Transfer in - {pair['transfer_type']} - Pair ID: {pair['pair_id']}{exchange_note}",
                'pair_id': pair['pair_id'],
                'transfer_type': 'incoming',
                'match_strategy': pair.get('match_strategy', 'traditional')
            })
        
        return transfer_matches
