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

// Base path for the application
const BASE_PATH = '/item-helper-app';

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
        { text: 'Home', href: `${BASE_PATH}/` },
        { text: 'Exam Items', href: `${BASE_PATH}/exam-items` }
      ]}
    />
  );

  return (
    <Layout activeHref={`${BASE_PATH}/exam-items`} breadcrumbs={breadcrumbs}>
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