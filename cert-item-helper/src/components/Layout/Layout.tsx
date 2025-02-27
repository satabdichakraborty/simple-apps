import React, { ReactNode } from 'react';
import {
  AppLayout,
  ContentLayout,
  SideNavigation,
  SideNavigationProps,
  TopNavigation,
} from '@cloudscape-design/components';

// Base path for the application
const BASE_PATH = '/item-helper-app';

interface LayoutProps {
  children: ReactNode;
  activeHref?: string;
  breadcrumbs?: React.ReactNode;
}

const navigationItems: SideNavigationProps.Item[] = [
  {
    type: 'link',
    text: 'Dashboard',
    href: `${BASE_PATH}/`,
  },
  {
    type: 'link',
    text: 'Exam Items',
    href: `${BASE_PATH}/exam-items`,
  },
  {
    type: 'link',
    text: 'Practice Tests',
    href: `${BASE_PATH}/practice-tests`,
  },
  {
    type: 'link',
    text: 'Reports',
    href: `${BASE_PATH}/reports`,
  },
  {
    type: 'link',
    text: 'Settings',
    href: `${BASE_PATH}/settings`,
  },
];

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  activeHref = `${BASE_PATH}/`,
  breadcrumbs 
}) => {
  return (
    <AppLayout
      navigation={
        <SideNavigation
          activeHref={activeHref}
          header={{ text: 'Cert Item Helper', href: `${BASE_PATH}/` }}
          items={navigationItems}
        />
      }
      toolsHide
      notifications={<></>}
      breadcrumbs={breadcrumbs}
      content={
        <ContentLayout>
          {children}
        </ContentLayout>
      }
      headerSelector="#header"
    />
  );
};

export default Layout; 