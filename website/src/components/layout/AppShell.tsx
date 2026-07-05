import { Outlet } from 'react-router-dom';

import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell() {
  return (
    <>
      <Sidebar />
      <main id="main">
        <Topbar />
        <div className="content">
          <Outlet />
        </div>
      </main>
    </>
  );
}
