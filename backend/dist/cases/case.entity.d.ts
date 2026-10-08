export declare enum CaseStatus {
    ACTIVE = "ACTIVE",
    ARCHIVED = "ARCHIVED"
}
export declare class Case {
    id: string;
    name: string;
    description: string;
    status: CaseStatus;
    createdAt: Date;
    updatedAt: Date;
}
