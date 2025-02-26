import React, { useState } from 'react';
import {
  Button,
  Container,
  Form,
  FormField,
  Header,
  Input,
  SpaceBetween,
  Textarea,
} from '@cloudscape-design/components';
import { ExamItem } from '../../types';
import { useExamItemsStore } from '../../store/examItemsStore';

interface ExamItemFormProps {
  initialData?: ExamItem;
  onCancel: () => void;
  onSubmit: () => void;
}

const ExamItemForm: React.FC<ExamItemFormProps> = ({ 
  initialData, 
  onCancel,
  onSubmit
}) => {
  const { addItem, updateItem } = useExamItemsStore();
  const isEditMode = !!initialData;

  const [formData, setFormData] = useState<Partial<ExamItem>>(
    initialData || {
      questionId: '',
      question: '',
      option1: '',
      option2: '',
      option3: '',
      option4: '',
      key: '',
    }
  );

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: keyof ExamItem, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.questionId?.trim()) {
      newErrors.questionId = 'Question ID is required';
    }
    
    if (!formData.question?.trim()) {
      newErrors.question = 'Question is required';
    }
    
    if (!formData.option1?.trim()) {
      newErrors.option1 = 'Option 1 is required';
    }
    
    if (!formData.option2?.trim()) {
      newErrors.option2 = 'Option 2 is required';
    }
    
    if (!formData.key?.trim()) {
      newErrors.key = 'Answer key is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;
    
    if (isEditMode && initialData) {
      updateItem(initialData.id, formData);
    } else {
      // In a real app, you'd generate a proper ID or let the backend handle it
      const newItem = {
        ...formData,
        id: `item-${Date.now()}`,
      } as ExamItem;
      
      addItem(newItem);
    }
    
    onSubmit();
  };

  return (
    <Container>
      <Form
        header={
          <Header variant="h2">
            {isEditMode ? 'Edit Exam Item' : 'Add New Exam Item'}
          </Header>
        }
        actions={
          <SpaceBetween direction="horizontal" size="xs">
            <Button variant="link" onClick={onCancel}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmit}>
              {isEditMode ? 'Save changes' : 'Add item'}
            </Button>
          </SpaceBetween>
        }
      >
        <SpaceBetween direction="vertical" size="l">
          <FormField
            label="Question ID"
            errorText={errors.questionId}
          >
            <Input
              value={formData.questionId || ''}
              onChange={({ detail }) => handleChange('questionId', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Question"
            errorText={errors.question}
          >
            <Textarea
              value={formData.question || ''}
              onChange={({ detail }) => handleChange('question', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Option 1"
            errorText={errors.option1}
          >
            <Input
              value={formData.option1 || ''}
              onChange={({ detail }) => handleChange('option1', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Option 2"
            errorText={errors.option2}
          >
            <Input
              value={formData.option2 || ''}
              onChange={({ detail }) => handleChange('option2', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Option 3"
            errorText={errors.option3}
          >
            <Input
              value={formData.option3 || ''}
              onChange={({ detail }) => handleChange('option3', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Option 4"
            errorText={errors.option4}
          >
            <Input
              value={formData.option4 || ''}
              onChange={({ detail }) => handleChange('option4', detail.value)}
            />
          </FormField>
          
          <FormField
            label="Answer Key"
            description="Enter the correct answer option"
            errorText={errors.key}
          >
            <Input
              value={formData.key || ''}
              onChange={({ detail }) => handleChange('key', detail.value)}
            />
          </FormField>
        </SpaceBetween>
      </Form>
    </Container>
  );
};

export default ExamItemForm; 