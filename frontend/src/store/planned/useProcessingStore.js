import { create } from 'zustand'

/**
 * Processing Store - Manages data processing pipeline state
 * Handles transformation, transfer detection, and categorization
 */
const useProcessingStore = create((set, get) => ({
  // Processing state
  loading: false,
  error: null,
  
  // Data transformation state
  transformedData: [],
  stageIndex: 0,
  
  // Transfer detection state
  transferAnalysis: null,
  manuallyConfirmedTransfers: [],
  expandedTransfers: [],
  expandedPotentialTransfers: [],
  selectedPotentialTransfers: [],
  
  // Categorization state
  isApplyingCategorization: false,
  
  // Export state
  exporting: false,
  exportSuccess: false,
  selectedFormat: 'csv',
  
  // Loading and error actions
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
  
  // Data transformation actions
  setTransformedData: (data) => set({ transformedData: data }),
  
  updateTransformedData: (index, data) => set((state) => {
    const newData = [...state.transformedData]
    newData[index] = data
    return { transformedData: newData }
  }),
  
  setStageIndex: (index) => set({ stageIndex: index }),
  
  // Transfer detection actions
  setTransferAnalysis: (analysis) => set({ transferAnalysis: analysis }),
  
  addManuallyConfirmedTransfer: (transfer) => set((state) => ({
    manuallyConfirmedTransfers: [...state.manuallyConfirmedTransfers, transfer]
  })),
  
  removeManuallyConfirmedTransfer: (transferId) => set((state) => ({
    manuallyConfirmedTransfers: state.manuallyConfirmedTransfers.filter(t => t.id !== transferId)
  })),
  
  setExpandedTransfers: (expanded) => set({ expandedTransfers: expanded }),
  
  toggleExpandedTransfer: (transferId) => set((state) => {
    const isExpanded = state.expandedTransfers.includes(transferId)
    return {
      expandedTransfers: isExpanded 
        ? state.expandedTransfers.filter(id => id !== transferId)
        : [...state.expandedTransfers, transferId]
    }
  }),
  
  setExpandedPotentialTransfers: (expanded) => set({ expandedPotentialTransfers: expanded }),
  
  toggleExpandedPotentialTransfer: (transferId) => set((state) => {
    const isExpanded = state.expandedPotentialTransfers.includes(transferId)
    return {
      expandedPotentialTransfers: isExpanded 
        ? state.expandedPotentialTransfers.filter(id => id !== transferId)
        : [...state.expandedPotentialTransfers, transferId]
    }
  }),
  
  setSelectedPotentialTransfers: (selected) => set({ selectedPotentialTransfers: selected }),
  
  toggleSelectedPotentialTransfer: (transferId) => set((state) => {
    const isSelected = state.selectedPotentialTransfers.includes(transferId)
    return {
      selectedPotentialTransfers: isSelected 
        ? state.selectedPotentialTransfers.filter(id => id !== transferId)
        : [...state.selectedPotentialTransfers, transferId]
    }
  }),
  
  // Categorization actions
  setIsApplyingCategorization: (applying) => set({ isApplyingCategorization: applying }),
  
  // Export actions
  setExporting: (exporting) => set({ exporting }),
  
  setExportSuccess: (success) => set({ exportSuccess: success }),
  
  setSelectedFormat: (format) => set({ selectedFormat: format }),
  
  // Utility actions
  resetProcessingState: () => set({
    loading: false,
    error: null,
    transformedData: [],
    stageIndex: 0,
    transferAnalysis: null,
    manuallyConfirmedTransfers: [],
    expandedTransfers: [],
    expandedPotentialTransfers: [],
    selectedPotentialTransfers: [],
    isApplyingCategorization: false,
    exporting: false,
    exportSuccess: false
  }),
  
  // Computed getters
  getTransferById: (transferId) => {
    const state = get()
    return state.transferAnalysis?.confirmed_transfers?.find(t => t.id === transferId) ||
           state.transferAnalysis?.potential_transfers?.find(t => t.id === transferId)
  },
  
  getConfirmedTransfersCount: () => {
    const state = get()
    return (state.transferAnalysis?.confirmed_transfers?.length || 0) + 
           state.manuallyConfirmedTransfers.length
  },
  
  getPotentialTransfersCount: () => {
    const state = get()
    return state.transferAnalysis?.potential_transfers?.length || 0
  }
}))

export default useProcessingStore