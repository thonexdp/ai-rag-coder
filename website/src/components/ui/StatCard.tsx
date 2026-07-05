interface StatCardProps {
  label: string;
  value: string | number;
  helper?: string;
}

export function StatCard({ helper, label, value }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {helper ? <div className="delta">{helper}</div> : null}
    </div>
  );
}
