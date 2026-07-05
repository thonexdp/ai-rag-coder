interface SearchInputProps {
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}

export function SearchInput({ onChange, placeholder, value }: SearchInputProps) {
  return (
    <label className="search-box">
      <span>Search</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
    </label>
  );
}
