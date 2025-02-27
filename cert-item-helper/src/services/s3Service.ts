import { S3Client } from '@aws-sdk/client-s3';
import { Upload } from '@aws-sdk/lib-storage';

// Configure your S3 client
// In a production app, you should use environment variables and proper authentication
const s3Client = new S3Client({
  region: 'us-east-1', // Replace with your region
  credentials: {
    // In a real app, use AWS Cognito, environment variables, or other secure methods
    // for credentials - this is just for demonstration
    accessKeyId: 'YOUR_ACCESS_KEY',
    secretAccessKey: 'YOUR_SECRET_KEY',
  },
});

/**
 * Upload a file to an S3 bucket
 * @param file The file to upload
 * @param bucketName The S3 bucket name
 * @param prefix Optional path prefix
 * @returns Promise with upload result
 */
export const uploadFileToS3 = async (
  file: File,
  bucketName: string,
  prefix: string = ''
): Promise<{ success: boolean; url?: string; error?: string }> => {
  try {
    // Generate a file name with timestamp to avoid duplicates
    const timestamp = new Date().getTime();
    const fileName = `${prefix}${timestamp}-${file.name}`;
    
    // Create the upload parameters
    const params = {
      Bucket: bucketName,
      Key: fileName,
      Body: file,
      ContentType: file.type,
    };
    
    // Use the Upload utility for better handling of large files
    const upload = new Upload({
      client: s3Client,
      params,
    });
    
    // Execute the upload
    const result = await upload.done();
    
    // Return the URL of the uploaded file
    return {
      success: true,
      url: `https://${bucketName}.s3.amazonaws.com/${fileName}`,
    };
    
  } catch (error) {
    console.error('Error uploading file to S3:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'An unknown error occurred',
    };
  }
};

/**
 * Parse a CSV file and return array of objects
 * @param file CSV file to parse
 * @returns Promise with parsed data
 */
export const parseCSVFile = async (file: File): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const csvData = event.target?.result as string;
        if (!csvData) {
          reject(new Error('Failed to read CSV file'));
          return;
        }
        
        // Simple CSV parsing (in a real app, use a robust CSV parser library)
        const lines = csvData.split('\\n');
        const headers = lines[0].split(',').map(header => header.trim());
        const results = [];
        
        for (let i = 1; i < lines.length; i++) {
          if (!lines[i].trim()) continue; // Skip empty lines
          
          const data = lines[i].split(',');
          const item: Record<string, string> = {};
          
          headers.forEach((header, index) => {
            item[header] = data[index]?.trim() || '';
          });
          
          results.push(item);
        }
        
        resolve(results);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = (error) => reject(error);
    reader.readAsText(file);
  });
}; 