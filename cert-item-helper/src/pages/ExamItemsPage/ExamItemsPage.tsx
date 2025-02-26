import React, { useState } from 'react';
import {
  BreadcrumbGroup,
  Modal,
  SpaceBetween,
} from '@cloudscape-design/components';
import Layout from '../../components/Layout/Layout';
import ExamItemsTable from '../../components/ExamItemsTable';
import ExamItemForm from '../../components/ExamItemForm';
import { ExamItem } from '../../types';

const ExamItemsPage: React.FC = () => {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [itemToEdit, setItemToEdit] = useState<ExamItem | undefined>(undefined);

  const handleAddItem = () => {
    setItemToEdit(undefined);
    setIsFormVisible(true);
  };

  const handleEditItem = (item: ExamItem) => {
    setItemToEdit(item);
    setIsFormVisible(true);
  };

  const handleCloseForm = () => {
    setIsFormVisible(false);
    setItemToEdit(undefined);
  };

  const breadcrumbs = (
    <BreadcrumbGroup
      items={[
        { text: 'Home', href: '/' },
        { text: 'Exam Items', href: '/exam-items' }
      ]}
    />
  );

  return (
    <Layout activeHref="/exam-items" breadcrumbs={breadcrumbs}>
      <SpaceBetween size="l">
        <ExamItemsTable />

        {isFormVisible && (
          <Modal
            visible
            onDismiss={handleCloseForm}
            size="large"
            header={
              itemToEdit ? 'Edit exam item' : 'Add new exam item'
            }
          >
            <ExamItemForm
              initialData={itemToEdit}
              onCancel={handleCloseForm}
              onSubmit={handleCloseForm}
            />
          </Modal>
        )}
      </SpaceBetween>
    </Layout>
  );
};

export default ExamItemsPage; 