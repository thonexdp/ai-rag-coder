import { NavLink } from 'react-router-dom';

interface SidebarItemProps {
  to: string;
  label: string;
  end?: boolean;
}

export function SidebarItem({ end = false, label, to }: SidebarItemProps) {
  return (
    <NavLink end={end} to={to} className={({ isActive }) => `sb-item${isActive ? ' active' : ''}`}>
      {label}
    </NavLink>
  );
}
