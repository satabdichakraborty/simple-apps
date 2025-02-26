import { useCollection } from '@cloudscape-design/collection-hooks';
import { useState, useMemo } from 'react';
import { useExamItemsStore } from '../store/examItemsStore';
import { ExamItem } from '../types';

export function useExamItemsTable() {
  const { 
    items, 
    pagination: { currentPageIndex, pageSize },
    setPagination,
    fetchItems
  } = useExamItemsStore();
  
  const [selectedItems, setSelectedItems] = useState<ExamItem[]>([]);

  // Collection hook to manage sorting, filtering, and pagination
  const { items: collectionItems, collectionProps, paginationProps, filterProps } = useCollection(
    items,
    {
      filtering: {
        empty: 'No exam items found',
        noMatch: 'No exam items match the filter criteria',
      },
      pagination: { pageSize },
      sorting: {},
      selection: {},
    }
  );

  // Calculate page items based on pagination
  const paginatedItems = useMemo(() => {
    const startIndex = currentPageIndex * pageSize;
    const endIndex = startIndex + pageSize;
    return collectionItems.slice(startIndex, endIndex);
  }, [collectionItems, currentPageIndex, pageSize]);
  
  const handlePaginationChange = (pageIndex: number) => {
    setPagination({ currentPageIndex: pageIndex });
  };
  
  const handleRefresh = () => {
    fetchItems();
  };

  const handleSelectionChange = (items: ExamItem[]) => {
    setSelectedItems(items);
  };
  
  return {
    items: paginatedItems,
    totalItems: items.length,
    selectedItems,
    currentPageIndex,
    pageSize,
    collectionProps,
    paginationProps,
    filterProps,
    handlePaginationChange,
    handleRefresh,
    handleSelectionChange,
  };
} 