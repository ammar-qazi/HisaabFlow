import React, { useState, useMemo } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button } from '../../ui';
import { Search, Filter, ChevronUp, ChevronDown, Download } from '../../ui/Icons';

function InteractiveDataTable({ transformedData = [] }) {
  const theme = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [filterCategory, setFilterCategory] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(25);

  console.log('🔍 InteractiveDataTable Debug:', {
    transformedData,
    transformedDataType: Array.isArray(transformedData) ? 'array' : typeof transformedData,
    transformedDataLength: Array.isArray(transformedData) ? transformedData.length : 'not array'
  });

  // Ensure we have valid array data
  const data = useMemo(() => {
    if (Array.isArray(transformedData)) {
      return transformedData;
    }
    console.log('⚠️ TransformedData is not an array, using empty array');
    return [];
  }, [transformedData]);

  // Get unique categories for filter dropdown
  const categories = useMemo(() => {
    const uniqueCategories = [...new Set(data.map(item => item.Category || 'Uncategorized'))];
    return uniqueCategories.sort();
  }, [data]);

  // Filter and search logic
  const filteredData = useMemo(() => {
    let filtered = data;

    // Apply category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(item => {
        const itemCategory = item.Category || 'Uncategorized';
        return itemCategory === filterCategory;
      });
    }

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        Object.values(item).some(value =>
          String(value).toLowerCase().includes(searchLower)
        )
      );
    }

    return filtered;
  }, [data, filterCategory, searchTerm]);

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key] || '';
      const bValue = b[sortConfig.key] || '';

      // Handle numeric sorting for Amount
      if (sortConfig.key === 'Amount') {
        const aNum = parseFloat(String(aValue).replace(/[^-\d.]/g, '')) || 0;
        const bNum = parseFloat(String(bValue).replace(/[^-\d.]/g, '')) || 0;
        return sortConfig.direction === 'asc' ? aNum - bNum : bNum - aNum;
      }

      // Handle date sorting
      if (sortConfig.key === 'Date') {
        const aDate = new Date(aValue);
        const bDate = new Date(bValue);
        return sortConfig.direction === 'asc' ? aDate - bDate : bDate - aDate;
      }

      // String sorting
      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();
      
      if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortConfig]);

  // Pagination logic
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedData, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);

  // Handle sorting
  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Get table columns from data
  const columns = useMemo(() => {
    if (data.length === 0) return [];
    
    // Get all unique keys from the data, prioritizing main fields
    const allKeys = new Set();
    data.forEach(item => {
      Object.keys(item).forEach(key => allKeys.add(key));
    });

    // Define preferred column order
    const preferredOrder = ['Date', 'Title', 'Amount', 'Category', 'Account', 'Note'];
    const otherKeys = Array.from(allKeys).filter(key => 
      !preferredOrder.includes(key) && !key.startsWith('_') // Hide internal fields
    );

    return [...preferredOrder.filter(key => allKeys.has(key)), ...otherKeys];
  }, [data]);

  // Export filtered data
  const exportData = () => {
    const csvContent = [
      columns.join(','),
      ...sortedData.map(row => 
        columns.map(col => `"${String(row[col] || '').replace(/"/g, '""')}"`).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `filtered_transactions_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (data.length === 0) {
    return (
      <Card style={{ padding: theme.spacing.xl }}>
        <h3 style={{ ...theme.typography.h5, color: theme.colors.text.primary, marginBottom: theme.spacing.md }}>
          Transaction Data Table
        </h3>
        <p style={{ ...theme.typography.body1, color: theme.colors.text.secondary }}>
          No transaction data available to display.
        </p>
      </Card>
    );
  }

  return (
    <Card style={{ padding: theme.spacing.xl, marginBottom: theme.spacing.lg }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: theme.spacing.lg 
      }}>
        <h3 style={{ ...theme.typography.h5, color: theme.colors.text.primary, margin: 0 }}>
          Transaction Data Table
        </h3>
        <Button 
          onClick={exportData}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: theme.spacing.sm,
            backgroundColor: theme.colors.primary,
            color: 'white',
            border: 'none',
            padding: `${theme.spacing.sm} ${theme.spacing.md}`,
            borderRadius: theme.borderRadius.md,
            cursor: 'pointer'
          }}
        >
          <Download size={16} />
          Export Filtered Data
        </Button>
      </div>

      {/* Filters and Search */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr auto auto', 
        gap: theme.spacing.md, 
        marginBottom: theme.spacing.lg,
        alignItems: 'center'
      }}>
        {/* Search Input */}
        <div style={{ position: 'relative' }}>
          <Search 
            size={18} 
            style={{ 
              position: 'absolute', 
              left: theme.spacing.sm, 
              top: '50%', 
              transform: 'translateY(-50%)',
              color: theme.colors.text.secondary
            }} 
          />
          <input
            type="text"
            placeholder="Search transactions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: `${theme.spacing.sm} ${theme.spacing.sm} ${theme.spacing.sm} 40px`,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              backgroundColor: theme.colors.background.paper,
              color: theme.colors.text.primary,
              fontSize: theme.typography.body2.fontSize
            }}
          />
        </div>

        {/* Category Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
          <Filter size={18} color={theme.colors.text.secondary} />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            style={{
              padding: theme.spacing.sm,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              backgroundColor: theme.colors.background.paper,
              color: theme.colors.text.primary,
              fontSize: theme.typography.body2.fontSize
            }}
          >
            <option value="all">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>

        {/* Results Count */}
        <div style={{ ...theme.typography.body2, color: theme.colors.text.secondary }}>
          Showing {paginatedData.length} of {sortedData.length} transactions
        </div>
      </div>

      {/* Table */}
      <div style={{ 
        overflowX: 'auto',
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.md
      }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          backgroundColor: theme.colors.background.paper
        }}>
          <thead style={{ backgroundColor: theme.colors.background.default }}>
            <tr>
              {columns.map(column => (
                <th
                  key={column}
                  onClick={() => handleSort(column)}
                  style={{
                    padding: theme.spacing.md,
                    textAlign: 'left',
                    borderBottom: `1px solid ${theme.colors.border}`,
                    cursor: 'pointer',
                    userSelect: 'none',
                    position: 'relative',
                    ...theme.typography.body2,
                    fontWeight: 600,
                    color: theme.colors.text.primary
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    {column}
                    {sortConfig.key === column && (
                      sortConfig.direction === 'asc' 
                        ? <ChevronUp size={14} />
                        : <ChevronDown size={14} />
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr 
                key={index}
                style={{
                  borderBottom: `1px solid ${theme.colors.border}`,
                  '&:hover': { backgroundColor: theme.colors.background.default }
                }}
              >
                {columns.map(column => (
                  <td
                    key={column}
                    style={{
                      padding: theme.spacing.md,
                      ...theme.typography.body2,
                      color: theme.colors.text.primary,
                      maxWidth: '200px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                    title={String(row[column] || '')} // Show full value on hover
                  >
                    {/* Special formatting for certain columns */}
                    {column === 'Amount' && (
                      <span style={{ 
                        color: parseFloat(String(row[column]).replace(/[^-\d.]/g, '')) >= 0 
                          ? theme.colors.success 
                          : theme.colors.error,
                        fontWeight: 600
                      }}>
                        {row[column]}
                      </span>
                    )}
                    {column === 'Category' && (
                      <span style={{
                        padding: `2px 8px`,
                        backgroundColor: theme.colors.background.default,
                        borderRadius: theme.borderRadius.sm,
                        fontSize: '0.85em',
                        color: theme.colors.text.secondary
                      }}>
                        {row[column] || 'Uncategorized'}
                      </span>
                    )}
                    {column !== 'Amount' && column !== 'Category' && (
                      String(row[column] || '')
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          gap: theme.spacing.md,
          marginTop: theme.spacing.lg 
        }}>
          <Button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.md}`,
              border: `1px solid ${theme.colors.border}`,
              backgroundColor: theme.colors.background.paper,
              color: theme.colors.text.primary,
              borderRadius: theme.borderRadius.md,
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
              opacity: currentPage === 1 ? 0.5 : 1
            }}
          >
            Previous
          </Button>
          
          <span style={{ ...theme.typography.body2, color: theme.colors.text.secondary }}>
            Page {currentPage} of {totalPages}
          </span>
          
          <Button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: `${theme.spacing.sm} ${theme.spacing.md}`,
              border: `1px solid ${theme.colors.border}`,
              backgroundColor: theme.colors.background.paper,
              color: theme.colors.text.primary,
              borderRadius: theme.borderRadius.md,
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
              opacity: currentPage === totalPages ? 0.5 : 1
            }}
          >
            Next
          </Button>
        </div>
      )}
    </Card>
  );
}

export default InteractiveDataTable;