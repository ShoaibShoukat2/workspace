import { useState } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Calendar, Plus, X, LayoutDashboard, Briefcase, ShieldCheck, AlertTriangle, FileText, DollarSign, Users, Clock } from 'lucide-react';

export default function AdminMeetings() {
    // Mock data for meetings
    const [meetings, setMeetings] = useState([
        { id: 1, title: 'Site Walkthrough - 123 Main St', date: '2025-12-20', time: '10:00', with: 'John Doe (Customer)' },
        { id: 2, title: 'Compliance Review', date: '2025-12-21', time: '14:00', with: 'Mike Smith (Contractor)' },
        { id: 3, title: 'Investor Monthly Sync', date: '2025-12-22', time: '11:00', with: 'Sarah Connor' },
    ]);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newMeeting, setNewMeeting] = useState({ title: '', date: '', time: '', with: '' });

    const navItems = [
        { label: 'Dashboard', path: '/admin/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
        { label: 'Jobs', path: '/admin/jobs', icon: <Briefcase className="w-5 h-5" /> },
        { label: 'Legal & Compliance', path: '/admin/legal-compliance', icon: <ShieldCheck className="w-5 h-5" /> },
        { label: 'Disputes', path: '/admin/disputes', icon: <AlertTriangle className="w-5 h-5" /> },
        { label: 'Ledger', path: '/admin/ledger', icon: <FileText className="w-5 h-5" /> },
        { label: 'Payouts', path: '/admin/payouts', icon: <DollarSign className="w-5 h-5" /> },
        { label: 'Meetings', path: '/admin/meetings', icon: <Calendar className="w-5 h-5" /> },
        { label: 'Leads', path: '/admin/leads', icon: <Users className="w-5 h-5" /> },
    ];

    const handleAddMeeting = (e: React.FormEvent) => {
        e.preventDefault();
        setMeetings([
            ...meetings,
            { id: Date.now(), ...newMeeting }
        ]);
        setNewMeeting({ title: '', date: '', time: '', with: '' });
        setIsModalOpen(false);
    };

    return (
        <PortalLayout title="Scheduled Meetings" navItems={navItems}>
            <div className="space-y-6 animate-fade-in">
                <div className="flex justify-end">
                    <Button onClick={() => setIsModalOpen(true)}>
                        <Plus className="w-4 h-4 mr-2" />
                        Schedule Meeting
                    </Button>
                </div>

                <Card>
                    <div className="space-y-4">
                        {meetings.length === 0 ? (
                            <p className="text-gray-500 text-center py-8">No meetings scheduled.</p>
                        ) : (
                            meetings.map((m) => (
                                <div key={m.id} className="flex items-start space-x-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-lg transition-colors border-b border-gray-100 dark:border-gray-800 last:border-0">
                                    <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                                        <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-semibold text-gray-900 dark:text-white">{m.title}</h4>
                                        <div className="flex items-center space-x-4 mt-1">
                                            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                                                <Calendar className="w-3 h-3 mr-1" />
                                                {m.date}
                                            </div>
                                            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                                                <Clock className="w-3 h-3 mr-1" />
                                                {m.time}
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">With: <span className="font-medium">{m.with}</span></p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </Card>
            </div>

            {/* Schedule Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md p-6 m-4 animate-scale-in">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold">Schedule Meeting</h2>
                            <button onClick={() => setIsModalOpen(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <form onSubmit={handleAddMeeting} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Title</label>
                                <Input
                                    required
                                    value={newMeeting.title}
                                    onChange={e => setNewMeeting({ ...newMeeting, title: e.target.value })}
                                    placeholder="e.g. Site Visit"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Date</label>
                                    <Input
                                        required
                                        type="date"
                                        value={newMeeting.date}
                                        onChange={e => setNewMeeting({ ...newMeeting, date: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Time</label>
                                    <Input
                                        required
                                        type="time"
                                        value={newMeeting.time}
                                        onChange={e => setNewMeeting({ ...newMeeting, time: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">With (Name/Role)</label>
                                <Input
                                    required
                                    value={newMeeting.with}
                                    onChange={e => setNewMeeting({ ...newMeeting, with: e.target.value })}
                                    placeholder="e.g. John Doe"
                                />
                            </div>
                            <div className="pt-4 flex gap-3">
                                <Button type="button" variant="outline" className="flex-1" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                                <Button type="submit" className="flex-1">Schedule</Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </PortalLayout>
    );
}
