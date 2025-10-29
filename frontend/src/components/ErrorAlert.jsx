export default function ErrorAlert({ message }) {
  if (!message) return null;
  return (
    <div className="bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
      <strong className="font-semibold">Error:</strong> {message}
    </div>
  );
}
