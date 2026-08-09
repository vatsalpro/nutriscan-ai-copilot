import React, { useState } from 'react';
import { X, Send, Sparkles, ChefHat, AlertTriangle, Bot, User } from 'lucide-react';
import { api } from '../services/api';

export default function AssistantDrawer({ isOpen, onClose, currentRecipe, userIngredients }) {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hi! I am your NutriScan Kitchen Assistant. Ask me anything about ingredient swaps, cooking time adjustments, budget tips, or nutritional tweaks!',
      type: 'welcome'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const quickPrompts = [
    "I don't have tomatoes.",
    "Make this high protein.",
    "I only have 15 minutes.",
    "Can I replace paneer?",
    "Make this cheaper."
  ];

  const handleSend = async (queryText = null) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const res = await api.askAssistant(textToSend, currentRecipe, userIngredients);
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: res.response,
        type: res.type
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: 'Sorry, I had trouble processing your question. Please try again!',
        type: 'error'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5">
              <div className="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center text-emerald-400">
                <ChefHat className="w-5 h-5" />
              </div>
            </div>
            <div>
              <h3 className="font-bold text-white text-sm flex items-center gap-1.5">
                Ask NutriScan
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              </h3>
              <p className="text-[11px] text-slate-400">AI Kitchen Assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl p-3 leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-emerald-500 text-slate-950 font-medium rounded-tr-none'
                    : msg.type === 'disclaimer'
                    ? 'bg-amber-950/40 text-amber-200 border border-amber-800/50 rounded-tl-none'
                    : 'bg-slate-800/80 text-slate-200 border border-slate-700/50 rounded-tl-none'
                }`}
              >
                {msg.type === 'disclaimer' && (
                  <div className="flex items-center gap-1 text-amber-400 font-semibold mb-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>General Disclaimer</span>
                  </div>
                )}
                {msg.text}
              </div>
              {msg.sender === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-2.5 items-center text-slate-400 text-xs">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <span>NutriScan assistant is thinking...</span>
            </div>
          )}
        </div>

        {/* Quick Suggestions */}
        <div className="px-4 py-2 bg-slate-950/40 border-t border-slate-800/60 overflow-x-auto whitespace-nowrap scrollbar-none flex gap-2">
          {quickPrompts.map((prompt, i) => (
            <button
              key={i}
              onClick={() => handleSend(prompt)}
              className="px-2.5 py-1 rounded-full bg-slate-800/60 hover:bg-emerald-500/20 hover:text-emerald-400 text-slate-300 text-[11px] border border-slate-700/50 transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <div className="p-3 border-t border-slate-800 bg-slate-950">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a cooking question..."
              className="flex-1 bg-slate-900 text-white placeholder-slate-500 text-xs px-3 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
