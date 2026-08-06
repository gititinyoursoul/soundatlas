import { render } from 'svelte/server';
import { describe, expect, it } from 'vitest';
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
});
