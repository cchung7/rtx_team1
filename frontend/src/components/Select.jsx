export default function Select({ label, value, onChange, children, id }) {
  return (
    <div className="space-y-2">
      {label && <label htmlFor={id} className="text-sm font-semibold text-slate-800">{label}</label>}
      <select
        id={id}
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full border-2 border-slate-200 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {children}
      </select>
    </div>
  );
}
