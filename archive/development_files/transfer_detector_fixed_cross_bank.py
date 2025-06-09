    def _is_cross_bank_transfer(self, outgoing: Dict, incoming: Dict) -> bool:
        """Check if this is a cross-bank transfer (like Wise->NayaPay)"""
        outgoing_desc = str(outgoing.get('Description', '')).lower()
        incoming_desc = str(incoming.get('Description', incoming.get('Title', incoming.get('Note', '')))).lower()
        
        print(f"         🔍 Cross-bank check:")
        print(f"            📤 Outgoing bank: {outgoing.get('_bank_type')}")
        print(f"            📥 Incoming bank: {incoming.get('_bank_type')}")
        print(f"            📤 Outgoing desc: {outgoing_desc[:60]}...")
        print(f"            📥 Incoming desc: {incoming_desc[:60]}...")
        
        # Different banks (cross-bank requirement)
        if outgoing.get('_csv_index') == incoming.get('_csv_index'):
            print(f"            ❌ Same CSV file - not cross-bank")
            return False
        
        # ENHANCED: More flexible cross-bank detection
        
        # Strategy 1: Wise->NayaPay pattern (strict)
        if (outgoing.get('_bank_type') == 'wise' and 
            incoming.get('_bank_type') in ['nayapay', 'bank_alfalah']):
            
            if ('sent money' in outgoing_desc and self.user_name.lower() in outgoing_desc):
                if ('incoming fund transfer' in incoming_desc and self.user_name.lower() in incoming_desc):
                    print(f"            ✅ Strict Wise->NayaPay match")
                    return True
        
        # Strategy 2: Any cross-bank transfer with user name (flexible)
        if (outgoing.get('_bank_type') != incoming.get('_bank_type') and
            outgoing.get('_bank_type') not in ['unknown', None] and
            incoming.get('_bank_type') not in ['unknown', None]):
            
            # Check if both mention user name
            user_in_outgoing = self.user_name.lower() in outgoing_desc
            user_in_incoming = self.user_name.lower() in incoming_desc
            
            # Check for transfer-related keywords
            outgoing_transfer_keywords = any(keyword in outgoing_desc for keyword in [
                'sent', 'transfer', 'money', 'payment'
            ])
            
            incoming_transfer_keywords = any(keyword in incoming_desc for keyword in [
                'incoming', 'transfer', 'received', 'ibft', 'fund transfer'
            ])
            
            if user_in_outgoing and user_in_incoming and outgoing_transfer_keywords and incoming_transfer_keywords:
                print(f"            ✅ Flexible cross-bank match (both have user name + transfer keywords)")
                return True
        
        # Strategy 3: Very flexible - just different banks with amount match potential
        if (outgoing.get('_csv_index') != incoming.get('_csv_index') and
            outgoing.get('_bank_type') != incoming.get('_bank_type')):
            
            # If we have an exchange amount, be even more flexible
            exchange_amount = self._get_exchange_amount(outgoing)
            if exchange_amount:
                print(f"            ✅ Exchange amount present - flexible cross-bank match")
                return True
            
            # Basic transfer patterns
            if any(keyword in outgoing_desc for keyword in ['sent', 'transfer']) and \
               any(keyword in incoming_desc for keyword in ['incoming', 'transfer', 'received']):
                print(f"            ✅ Basic transfer pattern match")
                return True
        
        print(f"            ❌ No cross-bank match")
        return False
