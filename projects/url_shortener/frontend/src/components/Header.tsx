import { Link } from "lucide-react";

export const Header:React.FC =()=>{
  return (
    <div className="text-center mb-12">
      <div className="flex items-center justify-center gap-3 mb-4">
        <Link className="w-12 h-12 text-indigo-600" />
        <h1 className="text-5xl font-bold text-gray-800">URL Shortener</h1>
      </div>
      <p className="text-gray-600 text-lg">
        Fast, reliable, and analytics-powered link shortening
      </p>
    </div>
  )
};
