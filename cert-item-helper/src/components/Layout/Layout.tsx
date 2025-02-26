import React, { ReactNode } from 'react';
import {
  AppLayout,
  ContentLayout,
  SideNavigation,
  SideNavigationProps,
  TopNavigation,
} from '@cloudscape-design/components';

interface LayoutProps {
  children: ReactNode;
  activeHref?: string;
  breadcrumbs?: React.ReactNode;
}

const navigationItems: SideNavigationProps.Item[] = [
  {
    type: 'link',
    text: 'Dashboard',
    href: '/',
  },
  {
    type: 'link',
    text: 'Exam Items',
    href: '/exam-items',
  },
  {
    type: 'link',
    text: 'Practice Tests',
    href: '/practice-tests',
  },
  {
    type: 'link',
    text: 'Reports',
    href: '/reports',
  },
  {
    type: 'link',
    text: 'Settings',
    href: '/settings',
  },
];

const Layout: React.FC<LayoutProps> = ({ 
  children, 
  activeHref = '/',
  breadcrumbs 
}) => {
  return (
    <AppLayout
      navigation={
        <SideNavigation
          activeHref={activeHref}
          header={{ text: 'Cert Item Helper', href: '/' }}
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