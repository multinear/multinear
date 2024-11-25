export function getTaskStatus(task: any) {
    return {
        isPassed: task.eval_passed,
        statusClass: task.eval_passed ? 
            'bg-green-50 hover:bg-green-100' : 
            'bg-red-100 hover:bg-red-200'
    };
}

export function truncateInput(input: any, maxLength: number = 50): string {
    if (!input) return '-';
    
    const text = typeof input === 'object' && 'str' in input 
        ? input.str 
        : JSON.stringify(input);
        
    return text.length > maxLength 
        ? text.slice(0, maxLength) + '...' 
        : text;
}

export function filterTasks(
    tasks: any[], 
    statusFilter: string, 
    searchTerm: string,
    selectedIds: string[] | null = null
) {
    return tasks?.filter((task: any) => {
        // Filter by selected tasks if selectedIds is provided
        if (selectedIds !== null && !selectedIds.includes(task.id)) return false;
        
        // Filter by status if specified
        if (statusFilter && task.status !== statusFilter) return false;
        
        // Filter by search term if specified
        if (searchTerm) {
            const search = searchTerm.toLowerCase();
            return searchInObject(search, task);
        }
        
        return true;
    });
}

export function getStatusCounts(tasks: any[]) {
    return tasks?.reduce((acc: Record<string, number>, task: { status: string }) => {
        acc[task.status] = (acc[task.status] || 0) + 1;
        return acc;
    }, {} as Record<string, number>) || {};
}

function searchInObject(searchTerm: string, obj: any): boolean {
    if (!obj) return false;
    const search = searchTerm.toLowerCase();
    if (typeof obj === 'string') return obj.toLowerCase().includes(search);
    if (typeof obj === 'number') return obj.toString().toLowerCase().includes(search);
    if (Array.isArray(obj)) return obj.some(item => searchInObject(search, item));
    if (typeof obj === 'object') {
        return Object.values(obj).some(value => searchInObject(search, value));
    }
    return false;
}
