/**
 * Configuration handlers
 * Manages file configuration updates and column mapping
 */

/**
 * Creates configuration update handlers
 */
export const createConfigHandlers = (state) => {
  const { setUploadedFiles } = state;

  const updateFileConfig = (fileIndex, field, value) => {
    setUploadedFiles(prev => {
      const updated = [...prev];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        updated[fileIndex] = {
          ...updated[fileIndex],
          [parent]: {
            ...updated[fileIndex][parent],
            [child]: value
          }
        };
      } else {
        updated[fileIndex] = {
          ...updated[fileIndex],
          [field]: value
        };
      }
      return updated;
    });
  };

  const updateColumnMapping = (fileIndex, column, value) => {
    setUploadedFiles(prev => {
      const updated = [...prev];
      updated[fileIndex] = {
        ...updated[fileIndex],
        columnMapping: {
          ...updated[fileIndex].columnMapping,
          [column]: value
        }
      };
      return updated;
    });
  };

  return { updateFileConfig, updateColumnMapping };
};
