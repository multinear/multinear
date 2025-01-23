export function getScoreStyles(score: number, includePrintStyles: boolean = false): { color: string, border: string, text: string } {
    const printSuffix = includePrintStyles ? ' print:bg-green-50' : '';
    if (score >= 1) {
        return { 
            color: `status-completed status-completed-border${printSuffix}`, 
            border: 'status-completed-border',
            text: 'text-green-600'
        };
    } else if (score >= 0.5) {
        return { 
            color: `status-default status-default-border${includePrintStyles ? ' print:bg-yellow-50' : ''}`, 
            border: 'status-default-border',
            text: 'text-yellow-500'
        };
    }
    return { 
        color: `status-failed status-failed-border${includePrintStyles ? ' print:bg-red-50' : ''}`, 
        border: 'status-failed-border',
        text: 'text-red-600'
    };
}

export function truncateText(text: string, maxLength: number = 500): string {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
} 