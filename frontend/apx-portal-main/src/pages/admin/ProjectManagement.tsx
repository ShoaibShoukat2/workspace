import { useState } from 'react';
import PortalLayout from '@/components/PortalLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import {
    Briefcase,
    Plus,
    ChevronRight,
    CheckCircle,
    AlertTriangle,
    ArrowRight
} from 'lucide-react';
import { projects } from '@/data/mockData';
import { Project, ProjectStatus, SubtaskStatus } from '@/types';

export default function ProjectManagement() {
    const [viewMode, setViewMode] = useState<'list' | 'detail'>('list');
    const [selectedProject, setSelectedProject] = useState<Project | null>(null);

    const handleViewProject = (project: Project) => {
        setSelectedProject(project);
        setViewMode('detail');
    };

    const getStatusVariant = (status: ProjectStatus) => {
        switch (status) {
            case 'Setup': return 'warning';
            // case 'Ready': return 'info'; // Ready not in ProjectStatus type anymore? Check type def. Setup | AdminApproved | InProgress | Completed
            case 'AdminApproved': return 'info';
            case 'InProgress': return 'default'; // primary not supported
            case 'Completed': return 'success';
            default: return 'default';
        }
    };

    const getSubtaskStatusVariant = (status: SubtaskStatus) => {
        switch (status) {
            case 'NotStarted': return 'default';
            case 'MaterialsVerified': return 'info';
            case 'InProgress': return 'default'; // primary not supported
            case 'Blocked': return 'danger';
            case 'Completed': return 'success';
            default: return 'default';
        }
    };

    return (
        <PortalLayout title="Project Management" navItems={[]}>
            <div className="space-y-6 animate-fade-in pb-24">

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                            {viewMode === 'list' ? 'Project Overview' : selectedProject?.name}
                        </h1>
                        <p className="text-gray-500">
                            {viewMode === 'list' ? 'Manage complex multi-trade jobs and timelines.' : `Project ID: #${selectedProject?.id}`}
                        </p>
                    </div>
                    {viewMode === 'list' ? (
                        <Button>
                            <Plus className="w-5 h-5 mr-2" />
                            New Project
                        </Button>
                    ) : (
                        <Button variant="outline" onClick={() => setViewMode('list')}>
                            Back to List
                        </Button>
                    )}
                </div>

                {viewMode === 'list' ? (
                    <div className="grid gap-4">
                        {projects.map((project) => (
                            <Card key={project.id} hover className="cursor-pointer transition-all hover:scale-[1.01]" onClick={() => handleViewProject(project)}>
                                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                                    <div className="flex items-center gap-4 w-full md:w-auto">
                                        <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                                            <Briefcase className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900 dark:text-white">{project.name}</h3>
                                            <p className="text-sm text-gray-500">{project.propertyAddress}</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
                                        <div className="flex items-center gap-2 text-sm text-gray-500">
                                            {/* <Users className="w-4 h-4" /> */}
                                            <span>{project.trades.length} Trades</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-500">
                                            {/* <Layers className="w-4 h-4" /> */}
                                            <span>{project.subtasks.length} Phases</span>
                                        </div>
                                        <Badge variant={getStatusVariant(project.status)}>
                                            {project.status.toUpperCase()}
                                        </Badge>
                                        <ChevronRight className="w-5 h-5 text-gray-400" />
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                ) : selectedProject && (
                    <div className="grid gap-6">
                        {/* Project Stats */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <Card className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white border-0">
                                <div className="text-white/80 text-sm mb-1">Status</div>
                                <div className="text-2xl font-bold flex items-center gap-2">
                                    {selectedProject.status}
                                    {selectedProject.adminApproved && <CheckCircle className="w-5 h-5" />}
                                </div>
                                <div className="mt-4 text-xs bg-white/20 p-2 rounded-lg inline-block">
                                    {selectedProject.adminApproved ? 'Admin Approved' : 'Waiting Approval'}
                                </div>
                            </Card>

                            <Card>
                                <div className="text-gray-500 text-sm mb-1">Active Trades</div>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {selectedProject.trades.map(t => (
                                        <Badge key={t} variant="default">{t}</Badge>
                                    ))}
                                </div>
                            </Card>

                            <Card>
                                <div className="text-gray-500 text-sm mb-1">Total Estimated Hours</div>
                                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {selectedProject.subtasks.reduce((acc, curr) => acc + curr.estimatedTime, 0)} hrs
                                </div>
                            </Card>
                        </div>

                        {/* Timeline / Subtasks */}
                        <Card>
                            <div className="mb-4 font-bold text-lg border-b pb-2">Project Timeline & Subtasks</div>
                            <div className="space-y-4">
                                {selectedProject.subtasks.map((task, index) => (
                                    <div key={task.id} className="relative pl-8 pb-8 last:pb-0 border-l-2 border-dashed border-gray-200 dark:border-gray-700">
                                        <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 ${task.status === 'Completed' ? 'bg-green-500' :
                                            task.status === 'InProgress' ? 'bg-blue-500' :
                                                task.status === 'Blocked' ? 'bg-red-500' : 'bg-gray-300'
                                            }`} />

                                        <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                                            <div>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <h4 className="font-bold text-gray-900 dark:text-white">{task.trade.charAt(0).toUpperCase() + task.trade.slice(1)} Phase</h4>
                                                    <Badge variant={getSubtaskStatusVariant(task.status)} className="text-xs">
                                                        {task.status}
                                                    </Badge>
                                                </div>
                                                <p className="text-sm text-gray-500">Estimated: {task.estimatedTime} hrs • Job ID: {task.jobId || 'N/A'}</p>

                                                {task.status === 'Blocked' && (
                                                    <p className="text-xs text-red-500 mt-2 font-medium flex items-center">
                                                        <AlertTriangle className="w-3 h-3 mr-1" />
                                                        Waiting on Materials
                                                    </p>
                                                )}
                                            </div>

                                            <div className="flex gap-2 w-full md:w-auto">
                                                <Button size="sm" variant={task.status === 'InProgress' ? 'danger' : 'outline'} disabled={task.status === 'Completed' || task.status === 'Blocked'}>
                                                    {task.status === 'InProgress' ? 'Stop' : 'Start Phase'}
                                                </Button>
                                                <Button size="sm" variant="ghost">Details</Button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>

                    </div>
                )}
            </div>
        </PortalLayout>
    );
}
