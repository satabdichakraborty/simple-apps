# Cert Item Helper

A React TypeScript application for managing certification exam questions and creating practice tests.

## Features

- Manage and organize certification exam questions
- Create and customize practice tests
- Track performance and progress
- Modern UI built with AWS Cloudscape Design System

## Tech Stack

- React 18
- TypeScript
- AWS Cloudscape Design System
- React Router for navigation
- Zustand for state management
- Vite for build tooling

## Project Structure

```
src/
  ├── components/              # Reusable UI components
  │   ├── ExamItemsTable/      # Table component for displaying exam items
  │   ├── ExamItemForm/        # Form for adding/editing exam items
  │   └── Layout/              # App layout with navigation
  ├── contexts/                # React context providers
  ├── hooks/                   # Custom React hooks
  ├── pages/                   # Application pages
  │   ├── DashboardPage/       # Dashboard/home page
  │   └── ExamItemsPage/       # Exam items listing and management
  ├── services/                # API and service functions
  ├── store/                   # State management (using Zustand)
  ├── styles/                  # Global styles and theme
  ├── types/                   # TypeScript interfaces and types
  ├── utils/                   # Utility functions
  ├── App.tsx                  # Main App component with routing
  └── main.tsx                 # Application entry point
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run dev
   ```

## Building for Production

```
npm run build
```

## License

MIT 