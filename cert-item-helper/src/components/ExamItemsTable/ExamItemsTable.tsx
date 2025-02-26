import React, { useEffect } from 'react';
import {
  Table,
  Box,
  Button,
  Pagination,
  TextFilter,
  Header,
  SpaceBetween,
  BreadcrumbGroup,
  Container,
} from '@cloudscape-design/components';
import { useExamItemsStore } from '../../store/examItemsStore';
import { useExamItemsTable } from '../../hooks/useExamItemsTable';

const ExamItemsTable: React.FC = () => {
  const { 
    items,
    totalItems,
    fetchItems,
    loading
  } = useExamItemsStore();

  const {
    items: displayItems,
    currentPageIndex,
    pageSize,
    handlePaginationChange,
    handleSelectionChange,
    selectedItems,
    handleRefresh
  } = useExamItemsTable();

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  return (
    <Container>
      <SpaceBetween size="l">
        <Header
          variant="h1"
          actions={
            <SpaceBetween direction="horizontal" size="xs">
              <Button
                iconName="refresh"
                onClick={handleRefresh}
              />
              <Button
                variant="primary"
                iconName="add-plus"
              >
                Add Items
              </Button>
            </SpaceBetween>
          }
        >
          Exam Items ({totalItems})
        </Header>

        <Table
          loading={loading}
          loadingText="Loading exam items"
          columnDefinitions={[
            {
              id: 'questionId',
              header: 'QuestionId',
              cell: item => item.questionId,
              sortingField: 'questionId',
            },
            {
              id: 'question',
              header: 'Question',
              cell: item => item.question,
              sortingField: 'question',
            },
            {
              id: 'option1',
              header: 'Option 1',
              cell: item => item.option1,
              sortingField: 'option1',
            },
            {
              id: 'option2',
              header: 'Option 2',
              cell: item => item.option2,
              sortingField: 'option2',
            },
            {
              id: 'option3',
              header: 'Option 3',
              cell: item => item.option3,
              sortingField: 'option3',
            },
            {
              id: 'option4',
              header: 'Option 4',
              cell: item => item.option4,
              sortingField: 'option4',
            },
            {
              id: 'key',
              header: 'Key',
              cell: item => item.key,
              sortingField: 'key',
            },
          ]}
          items={displayItems}
          selectionType="multi"
          selectedItems={selectedItems}
          onSelectionChange={({ detail }) => handleSelectionChange(detail.selectedItems)}
          filter={
            <TextFilter
              filteringPlaceholder="Find resource"
              filteringText=""
              onChange={() => {}}
            />
          }
          pagination={
            <Pagination
              currentPageIndex={currentPageIndex + 1}
              pagesCount={Math.ceil(totalItems / pageSize)}
              onChange={({ detail }) => handlePaginationChange(detail.currentPageIndex - 1)}
            />
          }
          header={
            <Header
              counter={`(${totalItems})`}
              actions={
                <SpaceBetween direction="horizontal" size="xs">
                  <Button>Actions</Button>
                </SpaceBetween>
              }
            >
              Exam Items
            </Header>
          }
        />
      </SpaceBetween>
    </Container>
  );
};

export default ExamItemsTable; 