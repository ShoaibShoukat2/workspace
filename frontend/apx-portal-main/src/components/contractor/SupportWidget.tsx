import React, { useState } from 'react';
import { MessageCircle, HelpCircle, X, Send } from 'lucide-react';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';

export default function SupportWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [view, setView] = useState<'menu' | 'chat' | 'faq'>('menu');
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<{ sender: 'user' | 'ai', text: string }[]>([]);

    const handleSendMessage = () => {
        if (!message.trim()) return;

        // Add user message
        const newHistory = [...chatHistory, { sender: 'user' as const, text: message }];
        setChatHistory(newHistory);
        setMessage('');

        // Mock reply after 1s
        setTimeout(() => {
            setChatHistory(prev => [...prev, {
                sender: 'ai',
                text: "Thanks for reaching out! A human agent has been notified and will join this chat shortly. (Mock Reply)"
            }]);
        }, 1000);
    };

    const faqs = [
        { q: "How do I get paid?", a: "Payments are processed automatically 24-48 hours after job completion and customer sign-off." },
        { q: "Material delivery is late?", a: "Check the 'Materials' tab in the job detail. If urgent, click 'Report Issue' on the job card." },
        { q: "Customer isn't home?", a: "Wait 15 minutes, then mark 'Customer No-Show' in the job options." },
    ];

    const toggleOpen = () => {
        setIsOpen(!isOpen);
        if (!isOpen) setView('menu');
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {/* Main Toggle Button */}
            <button
                onClick={toggleOpen}
                className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all transform hover:scale-105 ${isOpen ? 'bg-red-500 rotate-45' : 'bg-gradient-to-r from-blue-600 to-indigo-600'
                    } text-white`}
            >
                {isOpen ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
            </button>

            {/* Support Window */}
            {isOpen && (
                <div className="absolute bottom-20 right-0 w-80 sm:w-96 animate-fade-in-up">
                    <Card className="shadow-2xl border-0 overflow-hidden flex flex-col max-h-[500px]">

                        {/* Header */}
                        <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-lg">Apex Support</h3>
                                <p className="text-xs text-blue-100">We're here to help.</p>
                            </div>
                            {view !== 'menu' && (
                                <button onClick={() => setView('menu')} className="text-xs bg-white/20 px-2 py-1 rounded hover:bg-white/30 transition">
                                    Back
                                </button>
                            )}
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-4 bg-white dark:bg-gray-900 min-h-[300px]">

                            {/* MENU VIEW */}
                            {view === 'menu' && (
                                <div className="space-y-3">
                                    <button
                                        onClick={() => setView('chat')}
                                        className="w-full flex items-center gap-3 p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition text-left group"
                                    >
                                        <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg text-blue-600 dark:text-blue-300 group-hover:scale-110 transition">
                                            <MessageCircle className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="font-bold text-gray-900 dark:text-white">Chat with Support</p>
                                            <p className="text-xs text-gray-500">Live agent wait time: &lt; 2 mins</p>
                                        </div>
                                    </button>

                                    <button
                                        onClick={() => setView('faq')}
                                        className="w-full flex items-center gap-3 p-4 rounded-xl bg-purple-50 dark:bg-purple-900/20 hover:bg-purple-100 dark:hover:bg-purple-900/40 transition text-left group"
                                    >
                                        <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg text-purple-600 dark:text-purple-300 group-hover:scale-110 transition">
                                            <HelpCircle className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="font-bold text-gray-900 dark:text-white">Quick Help / FAQ</p>
                                            <p className="text-xs text-gray-500">Common questions answered</p>
                                        </div>
                                    </button>
                                </div>
                            )}

                            {/* FAQ VIEW */}
                            {view === 'faq' && (
                                <div className="space-y-4">
                                    {faqs.map((item, i) => (
                                        <div key={i} className="border-b border-gray-100 dark:border-gray-800 pb-3 last:border-0">
                                            <p className="font-semibold text-sm text-gray-900 dark:text-white mb-1">{item.q}</p>
                                            <p className="text-sm text-gray-500 leading-relaxed">{item.a}</p>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* CHAT VIEW (Mock) */}
                            {view === 'chat' && (
                                <div className="space-y-4 h-full flex flex-col">
                                    <div className="flex-1 space-y-4 overflow-y-auto mb-2 pr-1">
                                        <div className="flex gap-2">
                                            <div className="w-8 h-8 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center text-xs font-bold text-blue-600">AI</div>
                                            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg rounded-tl-none text-sm text-gray-800 dark:text-gray-200">
                                                Hi! How can I help you with your job today?
                                            </div>
                                        </div>
                                        {chatHistory.map((msg, idx) => (
                                            <div key={idx} className={`flex gap-2 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                                                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${msg.sender === 'user' ? 'bg-purple-100 text-purple-600' : 'bg-blue-100 text-blue-600'}`}>
                                                    {msg.sender === 'user' ? 'Me' : 'AI'}
                                                </div>
                                                <div className={`p-3 rounded-lg text-sm max-w-[80%] ${msg.sender === 'user' ? 'bg-purple-600 text-white rounded-tr-none' : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'}`}>
                                                    {msg.text}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="flex gap-2 mt-auto pt-2 border-t border-gray-100 dark:border-gray-800">
                                        <input
                                            type="text"
                                            placeholder="Type a message..."
                                            className="flex-1 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm px-3 focus:ring-1 focus:ring-blue-500"
                                            value={message}
                                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') handleSendMessage();
                                            }}
                                        />
                                        <Button size="sm" className="w-9 h-9 p-0" onClick={handleSendMessage}>
                                            <Send className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            )}

                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
}
