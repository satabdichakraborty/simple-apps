import React, { useState, useRef } from 'react';
import {
  Button,
  Form,
  FormField,
  Input,
  Modal,
  SpaceBetween,
  Alert,
  Box,
  Spinner,
} from '@cloudscape-design/components';
import { uploadFileToS3, parseCSVFile } from '../../services/s3Service';
import { useExamItemsStore } from '../../store/examItemsStore';

interface CSVUploadProps {
  visible: boolean;
  onDismiss: () => void;
  onUploadComplete: () => void;
}

const CSVUpload: React.FC<CSVUploadProps> = ({ 
  visible, 
  onDismiss,
  onUploadComplete
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [bucketName, setBucketName] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const { addItem } = useExamItemsStore();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      
      // Check file type
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        setError('Please select a valid CSV file');
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a CSV file to upload');
      return;
    }
    
    if (!bucketName) {
      setError('Please enter an S3 bucket name');
      return;
    }
    
    setIsUploading(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      // Upload file to S3
      const uploadResult = await uploadFileToS3(selectedFile, bucketName, 'exam-items/');
      
      if (!uploadResult.success) {
        throw new Error(uploadResult.error || 'Failed to upload file');
      }
      
      // Parse CSV data for local state
      try {
        const parsedData = await parseCSVFile(selectedFile);
        
        // Add items to local state
        parsedData.forEach(item => {
          // Map CSV columns to the ExamItem format
          const examItem = {
            id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            questionId: item.QuestionId || item.questionId || `Q-${Date.now()}`,
            question: item.Question || item.question || '',
            option1: item.Option1 || item.option1 || '',
            option2: item.Option2 || item.option2 || '',
            option3: item.Option3 || item.option3 || '',
            option4: item.Option4 || item.option4 || '',
            key: item.Key || item.key || item.CorrectOption || item.correctOption || '',
          };
          
          addItem(examItem);
        });
        
        setSuccessMessage(`Successfully uploaded ${parsedData.length} items to S3: ${uploadResult.url}`);
        setTimeout(() => {
          onUploadComplete();
          onDismiss();
        }, 2000);
      } catch (parseError) {
        console.error('Error parsing CSV:', parseError);
        setError('The file was uploaded to S3 but could not be processed. Please check the CSV format.');
      }
    } catch (uploadError) {
      console.error('Error uploading to S3:', uploadError);
      setError(uploadError instanceof Error ? uploadError.message : 'An error occurred during upload');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      onDismiss={onDismiss}
      header="Upload Exam Items CSV"
      size="medium"
    >
      <Form
        actions={
          <SpaceBetween direction="horizontal" size="xs">
            <Button variant="link" onClick={onDismiss} disabled={isUploading}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleUpload} loading={isUploading} disabled={!selectedFile || !bucketName}>
              Upload to S3
            </Button>
          </SpaceBetween>
        }
      >
        <SpaceBetween direction="vertical" size="m">
          {error && (
            <Alert type="error">
              {error}
            </Alert>
          )}
          
          {successMessage && (
            <Alert type="success">
              {successMessage}
            </Alert>
          )}
          
          <FormField
            label="S3 Bucket Name"
            description="Enter the name of the S3 bucket where you want to upload the CSV file"
          >
            <Input
              value={bucketName}
              onChange={({ detail }) => setBucketName(detail.value)}
              placeholder="my-exam-data-bucket"
              disabled={isUploading}
            />
          </FormField>
          
          <FormField
            label="CSV File"
            description="Select a CSV file containing exam items data"
          >
            <SpaceBetween direction="horizontal" size="xs">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                ref={fileInputRef}
                style={{ display: 'none' }}
                disabled={isUploading}
              />
              <Button onClick={handleBrowseClick} disabled={isUploading}>
                Browse
              </Button>
              <Box padding="xs">
                {selectedFile ? selectedFile.name : 'No file selected'}
              </Box>
            </SpaceBetween>
          </FormField>
          
          {isUploading && (
            <Box textAlign="center" padding={{ top: 'l', bottom: 'l' }}>
              <Spinner size="large" />
              <Box variant="p" padding={{ top: 'm' }}>
                Uploading and processing your file...
              </Box>
            </Box>
          )}
          
          <Box variant="p">
            <b>CSV Format:</b> The CSV should have headers matching the exam item fields 
            (QuestionId, Question, Option1, Option2, Option3, Option4, Key)
          </Box>
        </SpaceBetween>
      </Form>
    </Modal>
  );
};

export default CSVUpload; 