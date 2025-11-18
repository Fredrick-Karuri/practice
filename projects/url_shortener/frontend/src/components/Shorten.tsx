import { useState } from "react";
import { API_BASE } from "../api";
import type { ShortenResponse } from ".";
import { Copy } from 'lucide-react';
interface ShortenFormProps{
    longUrl:string
    setLongUrl:(url:string)=>void
    customCode:string
    setCustomCode:(code:string)=>void
    error:string
    setError:(error:string)=>void
}

export const ShortenForm:React.FC<ShortenFormProps> = ({
    longUrl,
    setLongUrl,
    customCode,
    setCustomCode,
    error,
    setError
}) =>{
      const [shortUrl,setShortUrl] = useState('')
      const [loading,setLoading] = useState(false)
      const [copied,setCopied] = useState(false)

      const handleShorten = async() =>{
          setError('')
          setLoading(true)
          
          try {
            const res = await fetch(`${API_BASE}/shorten`,{
              method: 'POST',
              headers: {'Content-Type':'application/json'},
              body: JSON.stringify({
                long_url:longUrl,
                custom_code:customCode || null
              })
            });
      
            if (!res.ok){
              const err = await res.json()
              throw new Error(err.detail || "Failed to shorten url")
            }
      
            const data:ShortenResponse = await res.json()
            setShortUrl(data.short_url)
            setLongUrl('')
            setCustomCode('')
            
          } catch (err) {
            setError( err instanceof Error? err.message: 'Unknown error')
            
          } finally{
            setLoading(false)
          }
        }

    const copyToClipboard = () =>{
        navigator.clipboard.writeText(shortUrl)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000);
    }
    

    return(
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
    <h2 className="text-2xl font-semibold mb-6 text-gray-800">Shorten URL</h2>

    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Long URL
        </label>
        <input
          type="url"
          value={longUrl}
          onChange={(e) => setLongUrl(e.target.value)}
          placeholder="https://example.com/very/long/url"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Custom Code (Optional)
        </label>
        <input
          type="text"
          value={customCode}
          onChange={(e) => setCustomCode(e.target.value)}
          placeholder="myBrandPromo"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" />
        <p className="text-xs text-gray-500 mt-1">Letters and numbers only</p>
      </div>

      <button
        onClick={handleShorten}
        disabled={loading || !longUrl}
        className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Shortening...' : 'Shorten URL'}
      </button>
    </div>

    {error && (
      <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
        {error}
      </div>
    )}

    {shortUrl && (
      <div className="mt-6 p-6 bg-green-50 border border-green-200 rounded-lg">
        <p className="text-sm font-medium text-gray-700 mb-2">Your shortened URL:</p>
        <div className="flex items-center gap-3">
          <a
            href={shortUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 text-indigo-600 font-semibold text-lg hover:underline break-all"
          >
            {shortUrl}
          </a>
          <button
            onClick={copyToClipboard}
            className="p-2 hover:bg-green-100 rounded-lg transition"
            title="Copy to clipboard"
          >
            <Copy className={`w-5 h-5 ${copied ? 'text-green-600' : 'text-gray-600'}`} />
          </button>
        </div>
        {copied && <p className="text-sm text-green-600 mt-2">✓ Copied to clipboard!</p>}
      </div>
    )}
  </div>

    )
    
}

