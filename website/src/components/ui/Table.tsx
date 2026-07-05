import type { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render: (item: T) => ReactNode;
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage: string;
}

export function Table<T>({ columns, data, emptyMessage }: TableProps<T>) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} className={column.className}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length ? (
            data.map((item, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column.key} className={column.className}>
                    {column.render(item)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr className="empty-row">
              <td colSpan={columns.length}>{emptyMessage}</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
