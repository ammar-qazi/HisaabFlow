import { create } from 'zustand'

/**
 * UI Store - Manages user interface state
 * Handles navigation, modals, drag-and-drop, and other UI interactions
 */
const useUIStore = create((set, get) => ({
  // Navigation state
  currentStep: 1,
  
  // Configuration UI state
  showAdvancedConfig: false,
  expandedSections: [],
  
  // File drag and drop state
  dragOver: false,
  dragCounter: 0,
  
  // Table and data view state
  searchTerm: '',
  sortConfig: { key: null, direction: 'asc' },
  filterCategory: '',
  currentPage: 1,
  itemsPerPage: 50,
  
  // Modal and panel state
  viewMode: 'table',
  expandedFiles: [],
  validationChecklist: {
    duplicatesChecked: false,
    categoriesReviewed: false,
    transfersValidated: false,
    dataQualityConfirmed: false
  },
  
  // Navigation actions
  setCurrentStep: (step) => set({ currentStep: step }),
  
  nextStep: () => set((state) => ({ 
    currentStep: Math.min(state.currentStep + 1, 3) 
  })),
  
  prevStep: () => set((state) => ({ 
    currentStep: Math.max(state.currentStep - 1, 1) 
  })),
  
  // Configuration UI actions
  setShowAdvancedConfig: (show) => set({ showAdvancedConfig: show }),
  
  toggleAdvancedConfig: () => set((state) => ({ 
    showAdvancedConfig: !state.showAdvancedConfig 
  })),
  
  setExpandedSections: (sections) => set({ expandedSections: sections }),
  
  toggleExpandedSection: (sectionId) => set((state) => {
    const isExpanded = state.expandedSections.includes(sectionId)
    return {
      expandedSections: isExpanded 
        ? state.expandedSections.filter(id => id !== sectionId)
        : [...state.expandedSections, sectionId]
    }
  }),
  
  // Drag and drop actions
  setDragOver: (dragOver) => set({ dragOver }),
  
  setDragCounter: (counter) => set({ dragCounter: counter }),
  
  incrementDragCounter: () => set((state) => ({ 
    dragCounter: state.dragCounter + 1 
  })),
  
  decrementDragCounter: () => set((state) => ({ 
    dragCounter: Math.max(0, state.dragCounter - 1) 
  })),
  
  resetDragState: () => set({ dragOver: false, dragCounter: 0 }),
  
  // Table and filtering actions
  setSearchTerm: (term) => set({ searchTerm: term }),
  
  setSortConfig: (config) => set({ sortConfig: config }),
  
  setFilterCategory: (category) => set({ filterCategory: category }),
  
  setCurrentPage: (page) => set({ currentPage: page }),
  
  setItemsPerPage: (itemsPerPage) => set({ 
    itemsPerPage, 
    currentPage: 1 // Reset to first page when changing items per page
  }),
  
  // View mode actions
  setViewMode: (mode) => set({ viewMode: mode }),
  
  setExpandedFiles: (files) => set({ expandedFiles: files }),
  
  toggleExpandedFile: (fileId) => set((state) => {
    const isExpanded = state.expandedFiles.includes(fileId)
    return {
      expandedFiles: isExpanded 
        ? state.expandedFiles.filter(id => id !== fileId)
        : [...state.expandedFiles, fileId]
    }
  }),
  
  // Validation checklist actions
  setValidationChecklist: (checklist) => set({ validationChecklist: checklist }),
  
  updateValidationItem: (item, checked) => set((state) => ({
    validationChecklist: {
      ...state.validationChecklist,
      [item]: checked
    }
  })),
  
  resetValidationChecklist: () => set({
    validationChecklist: {
      duplicatesChecked: false,
      categoriesReviewed: false,
      transfersValidated: false,
      dataQualityConfirmed: false
    }
  }),
  
  // Utility actions
  resetUIState: () => set({
    currentStep: 1,
    showAdvancedConfig: false,
    expandedSections: [],
    dragOver: false,
    dragCounter: 0,
    searchTerm: '',
    sortConfig: { key: null, direction: 'asc' },
    filterCategory: '',
    currentPage: 1,
    itemsPerPage: 50,
    viewMode: 'table',
    expandedFiles: [],
    validationChecklist: {
      duplicatesChecked: false,
      categoriesReviewed: false,
      transfersValidated: false,
      dataQualityConfirmed: false
    }
  }),
  
  // Computed getters
  getTableConfig: () => {
    const state = get()
    return {
      searchTerm: state.searchTerm,
      sortConfig: state.sortConfig,
      filterCategory: state.filterCategory,
      currentPage: state.currentPage,
      itemsPerPage: state.itemsPerPage
    }
  },
  
  isValidationComplete: () => {
    const state = get()
    const checklist = state.validationChecklist
    return Object.values(checklist).every(item => item === true)
  },
  
  getExpandedSectionCount: () => {
    const state = get()
    return state.expandedSections.length
  }
}))

export default useUIStore