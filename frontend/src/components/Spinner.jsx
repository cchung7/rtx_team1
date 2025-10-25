export default function Spinner({ text = "Loading..." }) {
  return (
    <div className="flex items-center gap-3 text-slate-600">
      <div className="w-6 h-6 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin" />
      <span className="font-medium">{text}</span>
    </div>
  );
}
