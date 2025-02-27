import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { applyMode } from '@cloudscape-design/global-styles';
import DashboardPage from './pages/DashboardPage';
import ExamItemsPage from './pages/ExamItemsPage';

// Apply Cloudscape theme
applyMode('light');

// Base path for the application
const BASE_PATH = '/item-helper-app';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={`${BASE_PATH}`} element={<DashboardPage />} />
        <Route path={`${BASE_PATH}/`} element={<DashboardPage />} />
        <Route path={`${BASE_PATH}/exam-items`} element={<ExamItemsPage />} />
        <Route path="*" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App; 