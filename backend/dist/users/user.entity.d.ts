export declare enum UserRole {
    ADMIN = "ADMIN",
    OPERATOR = "OPERATOR",
    SCIENTIST = "SCIENTIST",
    VIEWER = "VIEWER"
}
export declare class User {
    id: string;
    email: string;
    passwordHash: string;
    role: UserRole;
    createdAt: Date;
    updatedAt: Date;
}
