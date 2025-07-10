import { create } from 'zustand'

/**
 * File Store - Manages file upload, parsing, and template state
 * Replaces scattered useState variables related to file management
 */
const useFileStore = create((set, get) => ({
  // File management state
  uploadedFiles: [],
  activeTab: 0,
  selectedFileIndex: null,
  
  // Template and configuration state
  templates: [],
  bankConfigMapping: {},
  
  // Parsing results
  parsedResults: [],
  
  // File upload actions
  addFiles: (newFiles) => set((state) => ({
    uploadedFiles: [...state.uploadedFiles, ...newFiles]
  })),
  
  removeFile: (index) => set((state) => {
    const newFiles = state.uploadedFiles.filter((_, i) => i !== index)
    return {
      uploadedFiles: newFiles,
      activeTab: Math.min(state.activeTab, newFiles.length - 1),
      selectedFileIndex: state.selectedFileIndex === index ? null : state.selectedFileIndex
    }
  }),
  
  clearAllFiles: () => set({
    uploadedFiles: [],
    activeTab: 0,
    selectedFileIndex: null,
    parsedResults: []
  }),
  
  // Tab and selection actions
  setActiveTab: (tabIndex) => set({ activeTab: tabIndex }),
  
  setSelectedFileIndex: (index) => set({ selectedFileIndex: index }),
  
  // Template actions
  setTemplates: (templates) => set({ templates }),
  
  setBankConfigMapping: (mapping) => set({ bankConfigMapping: mapping }),
  
  // Parsing results actions
  setParsedResults: (results) => set({ parsedResults: results }),
  
  updateParsedResult: (index, result) => set((state) => {
    const newResults = [...state.parsedResults]
    newResults[index] = result
    return { parsedResults: newResults }
  }),
  
  // Utility actions
  getFileByIndex: (index) => {
    const state = get()
    return state.uploadedFiles[index] || null
  },
  
  getParsedResultByIndex: (index) => {
    const state = get()
    return state.parsedResults[index] || null
  },
  
  getActiveFile: () => {
    const state = get()
    return state.uploadedFiles[state.activeTab] || null
  },
  
  getActiveParsedResult: () => {
    const state = get()
    return state.parsedResults[state.activeTab] || null
  }
}))

export default useFileStore