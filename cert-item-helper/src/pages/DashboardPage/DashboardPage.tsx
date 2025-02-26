import React from 'react';
import {
  BreadcrumbGroup,
  Cards,
  Container,
  Header,
  SpaceBetween,
  Box,
  Link,
} from '@cloudscape-design/components';
import Layout from '../../components/Layout/Layout';

const DashboardPage: React.FC = () => {
  const breadcrumbs = (
    <BreadcrumbGroup items={[{ text: 'Home', href: '/' }]} />
  );

  return (
    <Layout activeHref="/" breadcrumbs={breadcrumbs}>
      <SpaceBetween size="l">
        <Container>
          <Header variant="h1">Cert Item Helper Dashboard</Header>
          <Box variant="p">
            Welcome to the Cert Item Helper. Use this application to manage and review certification exam questions.
          </Box>
        </Container>

        <Cards
          cardDefinition={{
            header: item => item.name,
            sections: [
              {
                id: 'description',
                content: item => item.description,
              },
              {
                id: 'link',
                content: item => <Link href={item.href}>Go to {item.name}</Link>,
              },
            ],
          }}
          cardsPerRow={[
            { cards: 1 },
            { minWidth: 500, cards: 2 },
          ]}
          items={[
            {
              name: 'Exam Items',
              description: 'Manage and organize your certification exam questions and answers.',
              href: '/exam-items',
            },
            {
              name: 'Practice Tests',
              description: 'Create and take practice tests to prepare for your certification exams.',
              href: '/practice-tests',
            },
            {
              name: 'Reports',
              description: 'View analytics and performance reports on your practice test results.',
              href: '/reports',
            },
            {
              name: 'Settings',
              description: 'Configure application settings and preferences.',
              href: '/settings',
            },
          ]}
        />
      </SpaceBetween>
    </Layout>
  );
};

export default DashboardPage; 