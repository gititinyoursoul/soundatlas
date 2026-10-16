import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
import { makeRoute } from '$lib/test/fixtures';
import NavigationDrawer from './NavigationDrawer.svelte';

describe('NavigationDrawer mode labels', () => {
  it('labels the editorial workflow and its route-review task precisely', () => {
    const { body } = render(NavigationDrawer, {
      props: {
        open: true,
        showEditorialReview: true,
        showAdminReview: true,
        editorialProposalCount: 5
      }
    });

    expect(body).toContain('Editorial');
    expect(body).toContain('Route review');
    expect(body).toContain('Editorial mode');
  });

  it('retains the admin and public mode labels outside editorial mode', () => {
    const admin = render(NavigationDrawer, {
      props: { open: true, showAdminReview: true }
    });
    const publicView = render(NavigationDrawer, {
      props: { open: true, showAdminReview: false }
    });

    expect(admin.body).toContain('Admin review');
    expect(publicView.body).toContain('Public explorer');
    expect(publicView.body).not.toContain('Editorial');
    expect(publicView.body).not.toContain('Route review');
    expect(publicView.body).not.toContain('Media Review');
  });

  it('renders reader and review routes directly in editorial navigation', () => {
    const { body } = render(NavigationDrawer, {
      props: {
        open: true,
        showEditorialReview: true,
        routes: [makeRoute({ id: 'reader', title: 'Reader route' })],
        reviewRoutes: [makeRoute({ id: 'review', title: 'Review route' })]
      }
    });

    expect(body).toContain('Routes to review');
    expect(body).toContain('Reader route');
    expect(body).toContain('Review route');
    expect(body).toContain('min-h-[3.75rem]');
    expect(body).toContain('Current review revision');
    expect(body).not.toContain('Choose selected route');
  });

  it('keeps same-id reader and review rows distinct by selection context', () => {
    const route = makeRoute({
      id: 'birth-of-hip-hop',
      title: 'Birth of Hip-Hop'
    });
    const { body } = render(NavigationDrawer, {
      props: {
        open: true,
        showEditorialReview: true,
        enableEditorialActions: false,
        routes: [route],
        reviewRoutes: [route],
        selectedRouteId: route.id,
        selectedRouteContext: 'reader'
      }
    });

    expect(body.match(/aria-current="page"/g)).toHaveLength(1);
    expect(body).toContain('Routes to review');
    expect(body).not.toContain('Route review');
  });

  it('shows a current reader route publicly and a current review revision editorially', () => {
    const route = makeRoute({
      id: 'birth-of-hip-hop',
      title: 'Birth of Hip-Hop',
      year_start: 1970,
      year_end: 1985
    });
    const publicView = render(NavigationDrawer, {
      props: {
        open: true,
        showAdminReview: false,
        routes: [route],
        selectedRouteId: route.id,
        selectedRouteContext: 'reader'
      }
    });
    const editorialView = render(NavigationDrawer, {
      props: {
        open: true,
        showEditorialReview: true,
        enableEditorialActions: false,
        routes: [route],
        reviewRoutes: [route],
        selectedRouteId: route.id,
        selectedRouteContext: 'review'
      }
    });

    expect(publicView.body).toContain('Birth of Hip-Hop');
    expect(publicView.body).toContain('1970-1985');
    expect(publicView.body).toContain('aria-current="page"');
    expect(publicView.body).not.toContain('Routes to review');

    expect(editorialView.body).toContain('Routes to review');
    expect(editorialView.body).toContain('Current review revision');
    const currentRoute = editorialView.body.match(
      /<button[^>]*aria-current="page"[^>]*>[\s\S]*?<\/button>/g
    );
    expect(currentRoute).toHaveLength(1);
    expect(currentRoute?.[0]).toContain('Current review revision');
  });
});
