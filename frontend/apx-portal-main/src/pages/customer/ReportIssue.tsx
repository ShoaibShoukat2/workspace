import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { AlertCircle, Home, Send, Bot, User as UserIcon } from 'lucide-react';
import { getJobByToken, createDispute } from '@/data/mockData';

type Message = {
    id: string;
    sender: 'user' | 'ai';
    text: string;
    timestamp: Date;
};

export default function ReportIssue() {
    const { token } = useParams();
    const job = getJobByToken(token || 'mock-token-123') || getJobByToken('mock-token-123');

    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [reportStage, setReportStage] = useState<'initial' | 'details' | 'category' | 'submitted'>('initial');
    const [issueData, setIssueData] = useState({ description: '', category: 'other' });

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Initial Greeting
    useEffect(() => {
        if (job && messages.length === 0) {
            simulateAiResponse(`Hi, I'm your Apex Support Assistant. I see you have an active job at ${job.propertyAddress}. How can I help you today?`);
        }
    }, [job]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const simulateAiResponse = (text: string, delay = 1000) => {
        setIsTyping(true);
        setTimeout(() => {
            const newMessage: Message = {
                id: Date.now().toString(),
                sender: 'ai',
                text,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, newMessage]);
            setIsTyping(false);
        }, delay);
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputText.trim()) return;

        // User Message
        const userMsg: Message = {
            id: Date.now().toString(),
            sender: 'user',
            text: inputText,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMsg]);
        setInputText('');

        // AI Logic Flow
        if (reportStage === 'initial') {
            setIssueData(prev => ({ ...prev, description: inputText }));
            simulateAiResponse("I'm sorry to hear that. To help me route this correctly, is this related to 'Quality', 'Damage', 'Incomplete Work', or 'Other'?");
            setReportStage('category');
        } else if (reportStage === 'category') {
            const lowerInput = inputText.toLowerCase();
            let category = 'other';
            if (lowerInput.includes('quality')) category = 'quality';
            else if (lowerInput.includes('damage')) category = 'damage';
            else if (lowerInput.includes('incomplete')) category = 'incomplete';

            setIssueData(prev => ({ ...prev, category }));
            simulateAiResponse("Got it. Please provide any final specific details or context for our Field Manager.");
            setReportStage('details');
        } else if (reportStage === 'details') {
            // Finalize and Submit
            simulateAiResponse("Thank you. I am generating a formal report now...");

            if (job) {
                createDispute(job.id, 'customer', `${issueData.category}: AI Reported`, `${issueData.description} \n\nDetails: ${inputText}`);
            }

            setTimeout(() => {
                setReportStage('submitted');
                simulateAiResponse(`Update: Ticket #${Math.floor(Math.random() * 1000) + 500} created successfully. A manager will review this within 24 hours.`);
            }, 2000);
        } else {
            simulateAiResponse("Your issue has already been logged. Is there anything else?");
        }
    };

    if (!job) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
                <Card className="max-w-md w-full text-center">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">Invalid Link</h2>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col md:flex-row">
            {/* Sidebar / Info Panel (Desktop) */}
            <div className="hidden md:block w-1/3 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-8">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4 shadow-lg">
                        <Bot className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Apex AI Support</h1>
                    <p className="text-gray-500 mt-2">24/7 Intelligent Assistance</p>
                </div>

                <Card className="bg-gray-50 dark:bg-gray-900/50">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Job Details</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                        <Home className="w-4 h-4 inline mr-2" />
                        {job.propertyAddress}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        Job ID: #{job.id}
                    </p>
                </Card>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col h-screen max-w-4xl mx-auto w-full">
                {/* Mobile Header */}
                <div className="md:hidden p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center space-x-3">
                    <div className="p-2 bg-purple-100 rounded-full">
                        <Bot className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                        <h1 className="font-bold text-gray-900 dark:text-white">Apex AI Support</h1>
                        <p className="text-xs text-green-500 flex items-center">
                            <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span> Online
                        </p>
                    </div>
                </div>

                {/* Messages Feed */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`flex max-w-[80%] md:max-w-[70%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mx-2 ${msg.sender === 'user' ? 'bg-blue-500' : 'bg-purple-600'
                                    }`}>
                                    {msg.sender === 'user' ? <UserIcon className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                                </div>
                                <div className={`p-4 rounded-2xl shadow-sm ${msg.sender === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                    : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none border border-gray-100 dark:border-gray-700'
                                    }`}>
                                    <p className="text-sm md:text-base">{msg.text}</p>
                                    <span className="text-[10px] opacity-70 mt-1 block">
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="flex justify-start animate-fade-in">
                            <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 p-4 rounded-2xl rounded-tl-none border border-gray-100 dark:border-gray-700 ml-12">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                    <form onSubmit={handleSendMessage} className="flex gap-2 relative max-w-4xl mx-auto">
                        <Input
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder={reportStage === 'submitted' ? "Session ended." : "Type your message..."}
                            disabled={reportStage === 'submitted'}
                            className="flex-1 pr-12 rounded-full border-gray-300 dark:border-gray-600 focus:ring-purple-500"
                        />
                        <Button
                            type="submit"
                            disabled={!inputText.trim() || reportStage === 'submitted'}
                            className="absolute right-1 top-1 bottom-1 rounded-full w-10 h-10 p-0 flex items-center justify-center bg-purple-600 hover:bg-purple-700 text-white shadow-md"
                        >
                            <Send className="w-4 h-4 ml-0.5" />
                        </Button>
                    </form>
                    <p className="text-center text-xs text-gray-400 mt-2">
                        Apex AI Assistant can make mistakes. Please verify critical info.
                    </p>
                </div>
            </div>
        </div>
    );
}
