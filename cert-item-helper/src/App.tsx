import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { applyMode } from '@cloudscape-design/global-styles';
import DashboardPage from './pages/DashboardPage';
import ExamItemsPage from './pages/ExamItemsPage';

// Apply Cloudscape theme
applyMode('light');

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/exam-items" element={<ExamItemsPage />} />
        <Route path="*" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App; 