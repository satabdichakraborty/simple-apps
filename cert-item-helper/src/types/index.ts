export interface ExamItem {
  id: string;
  questionId: string;
  question: string;
  option1: string;
  option2: string;
  option3: string;
  option4: string;
  key: string; // Correct answer
}

export type SortingState = {
  sortingColumn: keyof ExamItem | null;
  sortingDescending: boolean;
};

export type PaginationState = {
  currentPageIndex: number;
  pageSize: number;
};

export type FilteringState = {
  filteringText: string;
  filteringColumn: keyof ExamItem | null;
}; 