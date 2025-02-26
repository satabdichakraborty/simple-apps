import { create } from 'zustand';
import { ExamItem, SortingState, PaginationState, FilteringState } from '../types';

// Mock data for initial state
const mockExamItems: ExamItem[] = Array.from({ length: 10 }, (_, i) => ({
  id: `item-${i + 1}`,
  questionId: `Resource ${i + 1}`,
  question: 'Cell_value',
  option1: 'Cell_value',
  option2: 'Cell_value',
  option3: 'Cell_value',
  option4: 'Cell_value',
  key: 'Cell_value',
}));

interface ExamItemsState {
  items: ExamItem[];
  totalItems: number;
  loading: boolean;
  error: string | null;
  pagination: PaginationState;
  sorting: SortingState;
  filtering: FilteringState;
  
  // Actions
  setItems: (items: ExamItem[]) => void;
  addItem: (item: ExamItem) => void;
  updateItem: (id: string, item: Partial<ExamItem>) => void;
  deleteItem: (id: string) => void;
  setPagination: (pagination: Partial<PaginationState>) => void;
  setSorting: (sorting: Partial<SortingState>) => void;
  setFiltering: (filtering: Partial<FilteringState>) => void;
  fetchItems: () => Promise<void>;
}

export const useExamItemsStore = create<ExamItemsState>((set, get) => ({
  items: mockExamItems,
  totalItems: mockExamItems.length,
  loading: false,
  error: null,
  pagination: {
    currentPageIndex: 0,
    pageSize: 10,
  },
  sorting: {
    sortingColumn: null,
    sortingDescending: false,
  },
  filtering: {
    filteringText: '',
    filteringColumn: null,
  },

  setItems: (items) => set({ items }),
  
  addItem: (item) => {
    set((state) => ({
      items: [...state.items, item],
      totalItems: state.totalItems + 1,
    }));
  },
  
  updateItem: (id, updatedFields) => {
    set((state) => ({
      items: state.items.map((item) => 
        item.id === id ? { ...item, ...updatedFields } : item
      ),
    }));
  },
  
  deleteItem: (id) => {
    set((state) => ({
      items: state.items.filter((item) => item.id !== id),
      totalItems: state.totalItems - 1,
    }));
  },
  
  setPagination: (pagination) => {
    set((state) => ({
      pagination: { ...state.pagination, ...pagination },
    }));
  },
  
  setSorting: (sorting) => {
    set((state) => ({
      sorting: { ...state.sorting, ...sorting },
    }));
  },
  
  setFiltering: (filtering) => {
    set((state) => ({
      filtering: { ...state.filtering, ...filtering },
    }));
  },
  
  fetchItems: async () => {
    set({ loading: true, error: null });
    try {
      // In a real app, this would be an API call
      // For now, just simulate an API call with a delay
      await new Promise((resolve) => setTimeout(resolve, 500));
      set({ loading: false });
    } catch (error) {
      set({ 
        loading: false, 
        error: error instanceof Error ? error.message : 'An unknown error occurred' 
      });
    }
  },
})); 