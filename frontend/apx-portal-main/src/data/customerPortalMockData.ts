import type { CustomerJob } from '@/types/customerPortal';

export const mockCustomerJob: CustomerJob = {
    id: '8291',
    title: 'Master Bath & Kitchen Remodel',
    address: '1248 Highland Avenue',
    status: 'active',
    estimatedCost: 12450.00,
    schedule: {
        duration: '3 Weeks',
        completionDate: 'Nov 24',
    },
    contractor: {
        id: '1',
        name: 'Mike Ross',
        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150&h=150',
        rating: 4.9,
        jobsCount: 128,
        role: 'Lead Contractor',
    },
    timelineSteps: [
        { id: '1', label: 'Job Created', status: 'completed' },
        { id: '2', label: 'Walkthrough Scheduled', status: 'completed' },
        { id: '3', label: 'Quote Pending Approval', status: 'active' },
        { id: '4', label: 'Work in Progress', status: 'pending' },
    ],
    measurements: {
        totalArea: '450 sq ft',
        ceilingHeight: '9.5 ft',
        linearCabinetry: '22 ft',
    },
    scopeItems: [
        {
            id: '1',
            title: 'Demolition & Disposal',
            description: 'Remove existing cabinets, flooring, and backsplash.',
            price: 1200,
            completed: true,
        },
        {
            id: '2',
            title: 'Electrical & Plumbing Rough-in',
            description: 'Relocate sink drain, add 4 recessed lights.',
            price: 3450,
            completed: true,
        },
        {
            id: '3',
            title: 'Cabinet Installation',
            description: 'Install shaker cabinets and hardware.',
            price: 4100,
            completed: false,
        },
    ],
    materials: [
        {
            id: '1',
            name: 'Kohler Purist Faucet',
            description: 'Brushed Modern Brass • 1.2 GPM',
            image: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=600',
            price: 349,
            unit: 'per unit',
            vendor: {
                name: 'Home Depot',
                logo: 'H',
                color: 'orange',
            },
            inStock: true,
        },
        {
            id: '2',
            name: 'Marazzi Porcelain Tile',
            description: 'Marble Look • 12x24 Matte',
            image: 'https://images.unsplash.com/photo-1615873968403-89e068629265?auto=format&fit=crop&q=80&w=600',
            price: 3.89,
            unit: 'sq. ft.',
            vendor: {
                name: "Lowe's",
                logo: 'L',
                color: 'blue',
            },
        },
        {
            id: '3',
            name: 'Wyndham 60" Vanity',
            description: 'Double Sink • Carrara Top',
            image: 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&q=80&w=600',
            price: 1850,
            unit: 'set',
            vendor: {
                name: 'Wayfair PRO',
                logo: 'W',
                color: 'purple',
            },
        },
        {
            id: '4',
            name: 'Behr Ultra Pure',
            description: 'Eggshell Enamel • 5 Gallon',
            image: 'https://images.unsplash.com/photo-1540932296774-3ed69c372864?auto=format&fit=crop&q=80&w=600',
            price: 198,
            unit: 'pail',
            vendor: {
                name: 'Home Depot',
                logo: 'H',
                color: 'orange',
            },
        },
    ],
    progressPhases: [
        {
            id: '1',
            title: 'Demolition Phase',
            status: 'completed',
        },
        {
            id: '2',
            title: 'Installation & Finishes',
            status: 'active',
            dayProgress: 'Day 3/5',
            contractorNote: {
                author: 'Mike Ross',
                avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150',
                text: '"Shower waterproofing passed inspection. Starting the mosaic floor tile now - looks fantastic against the dark grout."',
            },
            tasks: [
                { id: '1', label: 'Waterproofing', status: 'completed' },
                { id: '2', label: 'Mosaic Install', status: 'in-progress' },
                { id: '3', label: 'Grouting', status: 'pending' },
            ],
        },
        {
            id: '3',
            title: 'Final Walkthrough',
            status: 'pending',
        },
    ],
    gallery: [
        {
            id: '1',
            image: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&q=80&w=800',
            label: 'Kitchen (Existing)',
        },
        {
            id: '2',
            image: 'https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/917d6f93-fb36-439a-8c48-884b67b35381_1600w.jpg',
            label: 'Bath Plumbing',
        },
        {
            id: '3',
            image: 'https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/4734259a-bad7-422f-981e-ce01e79184f2_1600w.jpg',
            label: 'Floor Damage',
        },
    ],
    beforeImage: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&q=80&w=800',
    afterImage: 'https://hoirqrkdgbmvpwutwuwj.supabase.co/storage/v1/object/public/assets/assets/917d6f93-fb36-439a-8c48-884b67b35381_1600w.jpg',
    finalBalance: 4150.00,
};

