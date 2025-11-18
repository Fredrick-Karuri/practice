import { useState } from "react";
import "./App.css";
import { Header } from "./components/Header";
import { ShortenForm } from "./components/Shorten";
import { StatsSection } from "./components/Stats";

/*
states:
  1. longurl
  2.customcode
  3.shorturl
  4.loading
  5.error
  6.copied
  7.stats
  8.statscode
  9.loadingstats

handlers:
 1. handleshorten
 2. copytoclipboard
 3. fetchstats

*/

function App() {
  const [longUrl, setLongUrl] = useState("");
  const [customCode, setCustomCode] = useState("");
  const [error, setError] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <Header />

        {/* Shorten Form */}
        <ShortenForm
          longUrl={longUrl}
          setLongUrl={setLongUrl}
          customCode={customCode}
          setCustomCode={setCustomCode}
          error={error}
          setError={setError}
        />

        {/* Stats Section */}
        <StatsSection error={error} setError={setError} />

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Built with FastAPI + PostgreSQL + Redis + React</p>
        </div>
      </div>
    </div>
  );
}
export default App;
