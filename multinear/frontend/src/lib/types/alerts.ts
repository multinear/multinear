export type AlertType = "regression" | "security" | "improvement";
export type KeyAlert = {
    type: AlertType;
    message: string;
}; 